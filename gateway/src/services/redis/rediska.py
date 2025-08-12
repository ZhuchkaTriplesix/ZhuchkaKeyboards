import redis
import json
from typing import Optional, List, Any
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
                    logger.warning(
                        f"Redis connection attempt {attempt + 1} failed: {str(e)}"
                    )
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
            decode_responses=True,
        )

    # Базовые методы для работы с ключами
    async def set_record(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Устанавливает запись в Redis с опциональным TTL."""
        try:
            if ttl:
                return bool(self.redis_client.setex(key, ttl, value))
            else:
                return bool(self.redis_client.set(key, value))
        except Exception as e:
            logger.error(f"Error setting record in Redis: {e}")
            return False

    async def get_record(self, key: str) -> Optional[str]:
        """Получает запись из Redis по ключу."""
        try:
            return self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Error getting record from Redis: {e}")
            return None

    async def del_record(self, key: str) -> bool:
        """Удаляет запись из Redis по ключу."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting record from Redis: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Проверяет существование ключа в Redis."""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking key existence in Redis: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """Устанавливает TTL для ключа."""
        try:
            return bool(self.redis_client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Error setting TTL in Redis: {e}")
            return False

    # Методы для работы с множествами (sets)
    async def sadd(self, key: str, *members: str) -> int:
        """Добавляет элементы в множество."""
        try:
            return self.redis_client.sadd(key, *members)
        except Exception as e:
            logger.error(f"Error adding to set in Redis: {e}")
            return 0

    async def srem(self, key: str, *members: str) -> int:
        """Удаляет элементы из множества."""
        try:
            return self.redis_client.srem(key, *members)
        except Exception as e:
            logger.error(f"Error removing from set in Redis: {e}")
            return 0

    async def smembers(self, key: str) -> List[str]:
        """Получает все элементы множества."""
        try:
            return list(self.redis_client.smembers(key))
        except Exception as e:
            logger.error(f"Error getting set members from Redis: {e}")
            return []

    async def scard(self, key: str) -> int:
        """Получает количество элементов в множестве."""
        try:
            return self.redis_client.scard(key)
        except Exception as e:
            logger.error(f"Error getting set cardinality from Redis: {e}")
            return 0

    # Методы для работы с хешами (hashes)
    async def hset(self, key: str, field: str, value: str) -> bool:
        """Устанавливает поле в хеше."""
        try:
            return bool(self.redis_client.hset(key, field, value))
        except Exception as e:
            logger.error(f"Error setting hash field in Redis: {e}")
            return False

    async def hget(self, key: str, field: str) -> Optional[str]:
        """Получает поле из хеша."""
        try:
            return self.redis_client.hget(key, field)
        except Exception as e:
            logger.error(f"Error getting hash field from Redis: {e}")
            return None

    async def hgetall(self, key: str) -> dict:
        """Получает все поля хеша."""
        try:
            return self.redis_client.hgetall(key)
        except Exception as e:
            logger.error(f"Error getting all hash fields from Redis: {e}")
            return {}

    async def hdel(self, key: str, *fields: str) -> int:
        """Удаляет поля из хеша."""
        try:
            return self.redis_client.hdel(key, *fields)
        except Exception as e:
            logger.error(f"Error deleting hash fields from Redis: {e}")
            return 0

    # Методы для работы со списками (lists)
    async def lpush(self, key: str, *values: str) -> int:
        """Добавляет элементы в начало списка."""
        try:
            return self.redis_client.lpush(key, *values)
        except Exception as e:
            logger.error(f"Error pushing to list in Redis: {e}")
            return 0

    async def rpush(self, key: str, *values: str) -> int:
        """Добавляет элементы в конец списка."""
        try:
            return self.redis_client.rpush(key, *values)
        except Exception as e:
            logger.error(f"Error pushing to list in Redis: {e}")
            return 0

    async def lpop(self, key: str) -> Optional[str]:
        """Извлекает элемент из начала списка."""
        try:
            return self.redis_client.lpop(key)
        except Exception as e:
            logger.error(f"Error popping from list in Redis: {e}")
            return None

    async def rpop(self, key: str) -> Optional[str]:
        """Извлекает элемент из конца списка."""
        try:
            return self.redis_client.rpop(key)
        except Exception as e:
            logger.error(f"Error popping from list in Redis: {e}")
            return None

    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Получает диапазон элементов из списка."""
        try:
            return self.redis_client.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Error getting list range from Redis: {e}")
            return []

    # Методы для поиска ключей
    async def keys(self, pattern: str) -> List[str]:
        """Находит ключи по паттерну."""
        try:
            return self.redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Error searching keys in Redis: {e}")
            return []

    # Методы для работы с TTL
    async def ttl(self, key: str) -> int:
        """Получает TTL ключа в секундах."""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL from Redis: {e}")
            return -1

    # Методы для работы с JSON
    async def set_json(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Сохраняет JSON данные в Redis."""
        try:
            json_data = json.dumps(data, ensure_ascii=False)
            return await self.set_record(key, json_data, ttl)
        except Exception as e:
            logger.error(f"Error setting JSON in Redis: {e}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """Получает JSON данные из Redis."""
        try:
            data = await self.get_record(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting JSON from Redis: {e}")
            return None

    # Методы для работы с токенами (совместимость)
    def get_token(self, username: str) -> Optional[str]:
        """Получает токен пользователя из Redis."""
        try:
            return self.redis_client.get(f"token:{username}")
        except Exception as e:
            logger.error(f"Error getting token from Redis: {e}")
            return None

    def token_exists(self, username: str, token: str) -> bool:
        """Проверяет существование токена пользователя в Redis."""
        try:
            stored_token = self.redis_client.get(f"token:{username}")
            return stored_token == token
        except Exception as e:
            logger.error(f"Error checking token in Redis: {e}")
            return False

    # Методы для работы с счетчиками
    async def incr(self, key: str, amount: int = 1) -> int:
        """Увеличивает счетчик."""
        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing counter in Redis: {e}")
            return 0

    async def decr(self, key: str, amount: int = 1) -> int:
        """Уменьшает счетчик."""
        try:
            return self.redis_client.decr(key, amount)
        except Exception as e:
            logger.error(f"Error decrementing counter in Redis: {e}")
            return 0

    # Методы для работы с блокировками
    async def acquire_lock(self, key: str, ttl: int = 10) -> bool:
        """Приобретает блокировку."""
        try:
            return bool(self.redis_client.set(f"lock:{key}", "1", ex=ttl, nx=True))
        except Exception as e:
            logger.error(f"Error acquiring lock in Redis: {e}")
            return False

    async def release_lock(self, key: str) -> bool:
        """Освобождает блокировку."""
        try:
            return await self.del_record(f"lock:{key}")
        except Exception as e:
            logger.error(f"Error releasing lock in Redis: {e}")
            return False

    # Методы для очистки
    async def flush_db(self) -> bool:
        """Очищает текущую базу данных Redis."""
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Error flushing Redis DB: {e}")
            return False

    async def ping(self) -> bool:
        """Проверяет соединение с Redis."""
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Error pinging Redis: {e}")
            return False


# Создаем глобальный экземпляр
redis_manager = RedisManager()
