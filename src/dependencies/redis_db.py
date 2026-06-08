from redis.asyncio import Redis
from config import settings

client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
EXPIRY = 3600


async def add_to_blacklist(jti: str):
    await client.set(name=jti, value="", ex=EXPIRY)


async def is_in_blacklist(jti: str):
    jti_data = await client.get(jti)
    print(jti_data)
    return True if jti_data is not None else False
