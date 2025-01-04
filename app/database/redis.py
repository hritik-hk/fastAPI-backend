from redis import asyncio as aioredis
from app.config import Config


redis_client = aioredis.StrictRedis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0
)


async def add_jwtId_to_blocklist(jwtId: str) -> None:
    await redis_client.set(name=jwtId, value="", ex=Config.ACCESS_TOKEN_EXPIRY)


async def token_in_blocklist(jwtId: str) -> bool:
    jwt_id = await redis_client.get(jwtId)
    return jwt_id is not None
