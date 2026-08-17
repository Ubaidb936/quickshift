from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from datetime import datetime
from app.database.db import get_db
from app.auth import get_current_user, require_business
from app.models.models import Business, AgentConversation
from app.agent.business_agent import BusinessAgent
from app.llm.openai import OpenAILLM
from app.tools.search_workers import SearchWorkersTool
from app.tools.post_shift import PostShiftTool
from app.logger import get_logger

router = APIRouter(prefix="/agent", tags=["agent"])
logger = get_logger(__name__)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class AgentConversationResponse(BaseModel):
    id: int
    created_at: Optional[datetime]
    user_message: str
    tool_called: Optional[str]
    tool_args: Optional[dict]
    result_count: Optional[int]
    latency_ms: Optional[float]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    status: Optional[str]
    error_message: Optional[str]
    agent_response: Optional[str]

    class Config:
        from_attributes = True


@router.post("/chat")
async def chat(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "business":
        raise HTTPException(status_code=403, detail="Only businesses can use the staffing agent")

    result = await db.execute(select(Business).where(Business.id == user["id"]))
    business = result.scalars().first()

    llm = OpenAILLM()
    tools = [
        SearchWorkersTool(db=db, business=business),
        PostShiftTool(db=db, business_id=business.id),
    ]
    agent = BusinessAgent(llm=llm, tools=tools, db=db, business=business)

    # seed the agent's history: system prompt first, then prior turns from the client
    from app.llm.base import Message
    agent.history.append(Message(role="system", content=agent.system_prompt()))
    for msg in data.history:
        if msg.get("role") in ("user", "assistant") and msg.get("content"):
            agent.history.append(Message(role=msg["role"], content=msg["content"]))

    return StreamingResponse(
        agent.run(data.message),
        media_type="text/plain",
        headers={"X-Accel-Buffering": "no"},
    )


@router.get("/conversations", response_model=List[AgentConversationResponse])
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_business),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    tool: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None, pattern="^(success|error)$"),
):
    stmt = (
        select(AgentConversation)
        .where(AgentConversation.business_id == user["id"])
        .order_by(desc(AgentConversation.created_at))
        .limit(limit)
        .offset(offset)
    )
    if tool is not None:
        stmt = stmt.where(AgentConversation.tool_called == tool)
    if status is not None:
        stmt = stmt.where(AgentConversation.status == status)

    result = await db.execute(stmt)
    rows = result.scalars().all()

    logger.info(
        "Fetched agent conversations",
        extra={
            "business_id": user["id"],
            "count": len(rows),
            "limit": limit,
            "offset": offset,
            "tool_filter": tool,
            "status_filter": status,
        },
    )

    return [
        AgentConversationResponse(
            id=row.id,
            created_at=row.created_at,
            user_message=(row.user_message or "")[:100],
            tool_called=row.tool_called,
            tool_args=row.tool_args,
            result_count=row.result_count,
            latency_ms=row.latency_ms,
            input_tokens=row.input_tokens,
            output_tokens=row.output_tokens,
            status=row.status,
            error_message=row.error_message,
            agent_response=(row.agent_response or "")[:200] if row.agent_response else None,
        )
        for row in rows
    ]