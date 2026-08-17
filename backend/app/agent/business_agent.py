import json
from datetime import datetime
from typing import AsyncIterator
from app.agent.base import BaseAgent
from app.llm.base import Message
from app.models.models import AgentConversation
from app.logger import get_logger

logger = get_logger(__name__)


class BusinessAgent(BaseAgent):

    def __init__(self, llm, tools, db, business):
        super().__init__(llm, tools, db)
        self.business = business

    def system_prompt(self) -> str:
        b = self.business
        today = datetime.now()
        today_str = today.strftime("%A, %B %d, %Y")  # e.g. "Sunday, August 16, 2026"

        return (
            f"You are a staffing assistant for {b.name} on QuickShift. "
            f"Today is {today_str}. "
            f"The business is a {b.industry or 'business'} located in {b.location or 'an unspecified location'}. "
            + (f"Description: {b.description}. " if b.description else "")
            + (f"Environment vibe: {b.vibe}. " if b.vibe else "")
            + (f"Team size: {b.team_size}. " if b.team_size else "")
            + (f"Working hours: {b.working_hours}. " if b.working_hours else "")
            + "\n\n"
            "YOU HAVE TWO TOOLS:\n"
            "1. search_workers — find workers already on the platform that match the requirement.\n"
            "2. post_shift — post a new shift so workers can discover and apply to it.\n\n"
            "WHEN TO USE EACH:\n"
            "- Use search_workers when the user wants to find and contact workers directly.\n"
            "- Use post_shift when: search returns zero results, OR the user says they want to post a job/shift, "
            "OR they want workers to apply rather than being contacted directly.\n"
            "- If search returns results but the user still wants to post, do both.\n"
            "- Do NOT call any tool for conversational messages like 'thanks', 'looks good', 'tell me more about X'.\n\n"
            "AUTOMATIC BUSINESS CONTEXT: Unless the user says otherwise, always apply the business's defaults:\n"
            f"- Location filter: {b.location or 'not set'}\n"
            f"- Environment/vibe to embed in the query: {b.vibe or 'not set'}\n"
            f"- Industry context: {b.industry or 'not set'}\n"
            "Always build the semantic query to include the business's environment — e.g. for a fast-paced upscale "
            "restaurant, the query should be 'experienced bartender for fast-paced upscale restaurant environment, "
            "customer-facing, high volume service'. This ensures the embedding matches workers who fit the culture.\n\n"
            "DATE RESOLUTION: Resolve relative dates using today's date:\n"
            "- 'tomorrow' → compute the actual date and day of week\n"
            "- 'this weekend' → pass availability='Weekends'\n"
            "- weekday names (Monday–Friday) → pass availability='Weekdays'\n"
            "- 'tonight' / 'evenings' → pass availability='Evenings'\n"
            "- 'morning shift' → pass availability='Mornings'\n"
            "Include shift_date (YYYY-MM-DD) and day_of_week when a date is mentioned.\n"
            "TIME RESOLUTION: 'midnight' at end of a shift = next calendar day at 00:00. "
            "e.g. shift '6pm to midnight on Aug 17' → start_time=2026-08-17T18:00:00, end_time=2026-08-18T00:00:00.\n\n"
            "PRESENTING RESULTS:\n"
            "- search_workers: for each worker give name, profession, experience, location, availability, "
            "then 1–2 sentences on WHY they fit this business specifically — reference their bio and the business vibe. "
            "Be specific not generic. After results ask if they want to refine or post a shift instead.\n"
            "- post_shift: confirm the shift was posted, summarise the details (position, time, pay), "
            "and tell the business workers will now be able to discover and apply to it."
        )

    async def run(self, user_message: str) -> AsyncIterator[str]:
        try:
            if not self.history:
                self.history.append(Message(role="system", content=self.system_prompt()))

            self.history.append(Message(role="user", content=user_message))

            tool_schemas = [t.schema() for t in self.tools]
            tool_map = {t.name: t for t in self.tools}

            full_response = ""
            tool_call_name = None
            tool_call_args = ""

            async for chunk in self.llm.stream(self.history, tools=tool_schemas):
                if isinstance(chunk, dict) and chunk.get("type") == "tool_call":
                    # lock onto the first tool call name we see, ignore any others
                    if chunk.get("name") and not tool_call_name:
                        tool_call_name = chunk["name"]
                    # only accumulate args for the locked-in tool call
                    if tool_call_name and not chunk.get("name"):
                        tool_call_args += chunk.get("arguments", "")
                else:
                    full_response += chunk
                    yield chunk

            if tool_call_name and tool_call_name in tool_map:
                args = json.loads(tool_call_args) if tool_call_args else {}
                logger.info(
                    "Tool call: %s | args: %s",
                    tool_call_name,
                    json.dumps(args, indent=2),
                )
                tool_result = await tool_map[tool_call_name].execute(**args)
                result_count = len(tool_result.get("workers", []))

                self.history.append(Message(role="assistant", content=f"Tool call: {tool_call_name}({args})"))
                self.history.append(Message(role="user", content=f"Tool result: {json.dumps(tool_result)}"))

                final_response = ""
                async for chunk in self.llm.stream(self.history):
                    final_response += chunk
                    yield chunk

                self.history.append(Message(role="assistant", content=final_response))

                log = AgentConversation(
                    business_id=self.business.id,
                    user_message=user_message,
                    tool_called=tool_call_name,
                    tool_args=args,
                    result_count=result_count,
                    agent_response=final_response,
                )
            else:
                self.history.append(Message(role="assistant", content=full_response))

                log = AgentConversation(
                    business_id=self.business.id,
                    user_message=user_message,
                    tool_called=None,
                    tool_args=None,
                    result_count=None,
                    agent_response=full_response,
                )

            self.db.add(log)
            await self.db.commit()

        except Exception:
            logger.exception("Agent run() failed for business_id=%s", self.business.id)
            yield "\n\nSomething went wrong. Please try again."

        finally:
            yield "\0"