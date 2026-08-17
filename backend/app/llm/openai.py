import asyncio
from typing import AsyncIterator
from openai import AsyncOpenAI, APIStatusError, APIConnectionError, RateLimitError
from app.llm.base import BaseLLM, Message
from app.utils.config import settings

MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds, doubles each attempt


class OpenAILLM(BaseLLM):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=30.0)
        self.model = model

    async def stream(self, messages: list[Message], tools: list[dict] | None = None) -> AsyncIterator[str]:
        openai_messages = [{"role": m.role, "content": m.content} for m in messages]

        params = {
            "model": self.model,
            "messages": openai_messages,
            "stream": True,
            "stream_options": {"include_usage": True},
            "temperature": 0.2,
        }

        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
            params["parallel_tool_calls"] = False

        attempt = 0
        delay = RETRY_DELAY

        while attempt < MAX_RETRIES:
            try:
                response = await self.client.chat.completions.create(**params)
                usage_chunk = None

                async for chunk in response:
                    if not chunk.choices:
                        if chunk.usage:
                            usage_chunk = chunk.usage
                        continue

                    delta = chunk.choices[0].delta

                    if delta.content:
                        yield delta.content

                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            if tc.function.name:
                                yield {"type": "tool_call", "name": tc.function.name, "arguments": ""}
                            if tc.function.arguments:
                                yield {"type": "tool_call", "name": None, "arguments": tc.function.arguments}

                if usage_chunk:
                    yield {
                        "type": "usage",
                        "input_tokens": usage_chunk.prompt_tokens,
                        "output_tokens": usage_chunk.completion_tokens,
                    }
                return

            except RateLimitError:
                attempt += 1
                if attempt >= MAX_RETRIES:
                    yield "I'm currently unavailable due to high demand. Please try again in a moment."
                    return
                await asyncio.sleep(delay)
                delay *= 2

            except APIConnectionError:
                attempt += 1
                if attempt >= MAX_RETRIES:
                    yield "I'm having trouble connecting. Please try again shortly."
                    return
                await asyncio.sleep(delay)
                delay *= 2

            except APIStatusError:
                yield "Something went wrong on my end. Please try again."
                return