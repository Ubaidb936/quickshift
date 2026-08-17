import hashlib
import json
from openai import AsyncOpenAI
from app.utils.config import settings
from app.database.redis import redis_client

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def build_business_text(business) -> str:
    parts = [
        f"{business.name} is a {business.industry or 'business'} located in {business.location or 'an unspecified location'}.",
        business.description or "",
        f"The environment is {business.vibe}." if business.vibe else "",
        f"Team size is {business.team_size}." if business.team_size else "",
        f"Working hours are {business.working_hours}." if business.working_hours else "",
    ]
    return " ".join(p for p in parts if p)


def build_worker_text(worker) -> str:
    parts = [
        f"{worker.name} is a {worker.profession or 'worker'}.",
        f"{worker.experience_years} years of experience." if worker.experience_years else "",
        f"Skills: {worker.skills}." if worker.skills else "",
        f"Available {worker.availability}." if worker.availability else "",
        f"Located in {worker.location}." if worker.location else "",
        worker.bio or "",
    ]
    return " ".join(p for p in parts if p)


async def embed_text(text: str) -> list[float]:
    cache_key = f"qs:emb:{hashlib.sha256(text.encode()).hexdigest()}"
    redis = redis_client.get()

    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    vector = response.data[0].embedding
    await redis.setex(cache_key, 86400, json.dumps(vector))
    return vector