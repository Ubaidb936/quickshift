import redis.asyncio as aioredis
from app.utils.config import settings


class RedisClient:
    def __init__(self):
        self.client: aioredis.Redis | None = None

    async def init(self):
        self.client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self):
        if self.client:
            close = getattr(self.client, 'aclose', None) or getattr(self.client, 'close')
            await close()

    def get(self) -> aioredis.Redis:
        return self.client


redis_client = RedisClient()
