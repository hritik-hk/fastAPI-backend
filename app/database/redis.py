from redis import asyncio as aioredis
from app.config import Config


token_blocklist = aioredis.StrictRedis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0
)


async def add_jwtId_to_blocklist(jwtId: str) -> None:
    await token_blocklist.set(name=jwtId, value="", ex=Config.ACCESS_TOKEN_EXPIRY)


async def token_in_blocklist(jwtId: str) -> bool:
    jwt_id = await token_blocklist.get(jwtId)
    return jwt_id is not None
