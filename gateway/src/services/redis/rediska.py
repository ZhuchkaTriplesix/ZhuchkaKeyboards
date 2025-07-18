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
        self.redis = self._create_connection()
        self._test_connection()

    def _create_connection(self):
        return redis.Redis(
            host=os.getenv("REDIS_HOST", "auth_redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD"),
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            retry_on_timeout=True,
            health_check_interval=30
        )

    def _test_connection(self):
        try:
            if not self.redis.ping():
                raise ConnectionError("Redis connection failed")
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Redis connection error: {str(e)}")
            raise

    @redis_retry(max_retries=3, delay=1)
    def set_token(self, username: str, token: str, expire: int):
        self.redis.setex(f"user:{username}:token", expire, token)

    @redis_retry(max_retries=3, delay=1)
    def get_token(self, username: str) -> Optional[str]:
        return self.redis.get(f"user:{username}:token")

    @redis_retry(max_retries=3, delay=1)
    def delete_token(self, username: str):
        self.redis.delete(f"user:{username}:token")

    def token_exists(self, username: str, token: str) -> bool:
        stored_token = self.get_token(username)
        return stored_token is not None and stored_token == token


redis_manager = RedisManager()
