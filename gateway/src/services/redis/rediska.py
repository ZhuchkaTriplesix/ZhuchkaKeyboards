import redis
from typing import Optional
from utils.logger import get_logger
import os
from time import sleep
from functools import wraps

# Инициализируем логгер
logger = get_logger(__name__)


def redis_retry(max_retries=3, delay=1):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return f(*args, **kwargs)
                except (redis.ConnectionError, redis.TimeoutError) as e:
                    last_exception = e
                    logger.warning(f"Redis connection attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        sleep(delay * (attempt + 1))
            raise last_exception

        return wrapper

    return decorator


class RedisManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD", ""),
            decode_responses=True
        )

    async def get_record(self, tag: str, key: str) -> Optional[str]:
        """Get record from Redis by tag and key."""
        try:
            return self.redis_client.get(f"{tag}:{key}")
        except Exception as e:
            logger.error(f"Error getting record from Redis: {e}")
            return None

    async def del_record(self, tag: str, key: str) -> bool:
        """Delete record from Redis by tag and key."""
        try:
            return bool(self.redis_client.delete(f"{tag}:{key}"))
        except Exception as e:
            logger.error(f"Error deleting record from Redis: {e}")
            return False

    def get_token(self, username: str) -> Optional[str]:
        """Get token for user from Redis."""
        try:
            return self.redis_client.get(f"token:{username}")
        except Exception as e:
            logger.error(f"Error getting token from Redis: {e}")
            return None

    def token_exists(self, username: str, token: str) -> bool:
        """Check if token exists for user in Redis."""
        try:
            stored_token = self.redis_client.get(f"token:{username}")
            return stored_token == token
        except Exception as e:
            logger.error(f"Error checking token in Redis: {e}")
            return False


# Создаем глобальный экземпляр
redis_manager = RedisManager()
