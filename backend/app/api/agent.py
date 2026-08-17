from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.db import get_db
from app.auth import get_current_user
from app.models.models import Business
from app.agent.business_agent import BusinessAgent
from app.llm.openai import OpenAILLM
from app.tools.search_workers import SearchWorkersTool
from app.tools.post_shift import PostShiftTool

router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


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