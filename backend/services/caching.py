import redis.asyncio as redis
from backend.config import settings
from backend.logger import logger

def normalize_query(query: str) -> str:
    """Normalizes whitespace and removes special characters for consistent caching keys."""
    normalized = "".join(c for c in query.lower() if c.isalnum() or c.isspace()).strip()
    return " ".join(normalized.split())

def report_key(query: str) -> str:
    return f"report:{normalize_query(query)}"

def search_key(provider: str, query: str) -> str:
    return f"search:{provider}:{normalize_query(query)}"

def paper_key(paper_id: str) -> str:
    return f"paper:{paper_id}"

class RedisCache:
    def __init__(self):
        self.use_fallback = False
        self.fallback_db: dict[str, str] = {}
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD or None,
                decode_responses=True,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                db=settings.REDIS_DB
            )
        except Exception:
            logger.exception("Failed to initialize Redis client. Falling back to in-memory cache.")
            self.use_fallback = True

    async def get(self, key: str) -> str | None:
        """Retrieves cached responses, executing direct calls and falling back dynamically."""
        if self.use_fallback:
            val = self.fallback_db.get(key)
            logger.info("Cache Fallback | GET: | key=%s, %s", key, "Hit" if val is not None else "Miss")
            return val
        
        try:
            val = await self.client.get(key)
            logger.info("Redis Cache | GET: | key=%s, %s", key, "Hit" if val is not None else "Miss")
            return val
        except Exception:
            logger.exception("Redis GET failed. Switching to in-memory fallback cache.")
            self.use_fallback = True
            return self.fallback_db.get(key)

    async def set(self, key: str, value: str, ttl: int) -> None:
        """Sets caching values, updating the fallback database on connection exceptions."""
        if self.use_fallback:
            logger.info("Cache Fallback | SET | key=%s | ttl=%ss", key, ttl)
            self.fallback_db[key] = value
            return

        try:
            logger.info("Redis Cache | SET | key=%s | ttl=%ss", key, ttl)
            await self.client.set(key, value, ex=ttl)
        except Exception:
            logger.exception("Redis SET failed. Switching to in-memory fallback cache.")
            self.use_fallback = True
            self.fallback_db[key] = value

    async def delete(self, key: str) -> None:
        if self.use_fallback:
            logger.info("Cache Fallback | DELETE | key=%s", key)
            self.fallback_db.pop(key, None)
            return

        try:
            logger.info("Redis Cache | DELETE | key=%s", key)
            await self.client.delete(key)
        except Exception:
            logger.exception("Redis DELETE failed.")
    
    async def close(self) -> None:
        if not self.use_fallback:
            await self.client.aclose()

cache = RedisCache()
