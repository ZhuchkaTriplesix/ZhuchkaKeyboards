"""
Система кэширования API ответов
"""

import hashlib
import json
from typing import Optional
from fastapi import Request, Response

from services.redis.rediska import redis_manager
from utils.logger import get_logger

logger = get_logger(__name__)


class APICache:
    """Кэширование API ответов для улучшения производительности"""

    def __init__(self):
        self.cache_prefix = "api_cache:"
        self.default_ttl = 300  # 5 минут
        self.cacheable_methods = {"GET", "HEAD"}
        self.cacheable_status_codes = {200, 201, 304}

    def generate_cache_key(
        self, request: Request, user_id: Optional[str] = None
    ) -> str:
        """
        Генерирует уникальный ключ кэша для запроса

        Args:
            request: FastAPI запрос
            user_id: ID пользователя для персонализированного кэша

        Returns:
            Уникальный ключ кэша
        """
        # Создаем хеш из URL, параметров и заголовков
        cache_data = {
            "method": request.method,
            "url": str(request.url),
            "query_params": dict(request.query_params),
            "headers": {
                k: v
                for k, v in request.headers.items()
                if k.lower() not in ["authorization", "cookie", "user-agent"]
            },
        }

        if user_id:
            cache_data["user_id"] = user_id

        # Создаем JSON строку и хеш
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()

        return f"{self.cache_prefix}{cache_hash}"

    def is_cacheable(self, request: Request, response: Response) -> bool:
        """
        Проверяет, можно ли кэшировать ответ

        Args:
            request: FastAPI запрос
            response: FastAPI ответ

        Returns:
            True если ответ можно кэшировать
        """
        # Исключаем /metrics endpoint из кэширования
        if request.url.path == "/metrics":
            return False
            
        # Проверяем метод запроса
        if request.method not in self.cacheable_methods:
            return False

        # Проверяем статус код
        if response.status_code not in self.cacheable_status_codes:
            return False

        # Проверяем заголовки
        cache_control = response.headers.get("cache-control", "")
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False

        return True

    async def get_cached_response(self, cache_key: str) -> Optional[Response]:
        """
        Получает кэшированный ответ

        Args:
            cache_key: Ключ кэша

        Returns:
            Кэшированный ответ или None
        """
        try:
            cached_data = await redis_manager.get_record(cache_key)
            if not cached_data:
                return None

            cache_info = json.loads(cached_data)

            # Готовим заголовки без Content-Length
            headers = dict(cache_info["headers"])
            headers.pop("content-length", None)  # Удаляем Content-Length
            headers.pop("Content-Length", None)  # На всякий случай с большой буквы
            headers["X-Cache"] = "HIT"  # Добавляем заголовок X-Cache

            # Создаем ответ из кэша
            response = Response(
                content=cache_info["content"],
                status_code=cache_info["status_code"],
                headers=headers,
                media_type=cache_info["media_type"],
            )

            logger.debug(f"Cache hit for key: {cache_key}")
            return response

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing cached response: {e}")
            await redis_manager.del_record(cache_key)
            return None

    async def cache_response(
        self, cache_key: str, response: Response, response_body: bytes, ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширует ответ API

        Args:
            cache_key: Ключ кэша
            response: FastAPI ответ
            response_body: Тело ответа в виде bytes
            ttl: Время жизни кэша в секундах

        Returns:
            True если ответ был закэширован
        """
        try:
            ttl = ttl or self.default_ttl

            # Готовим заголовки без X-Cache и X-Response-Time
            headers = dict(response.headers)
            headers.pop("x-cache", None)
            headers.pop("X-Cache", None)
            headers.pop("x-response-time", None)
            headers.pop("X-Response-Time", None)

            # Создаем данные для кэширования
            cache_data = {
                "content": response_body.decode('utf-8') if response_body else "",
                "status_code": response.status_code,
                "headers": headers,
                "media_type": response.media_type,
                "cached_at": str(response.headers.get("date", "")),
            }

            # Сохраняем в Redis
            await redis_manager.set_record(cache_key, json.dumps(cache_data), ttl)

            logger.debug(f"Cached response for key: {cache_key}, TTL: {ttl}s")
            return True

        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False

    async def invalidate_cache_pattern(self, pattern: str) -> int:
        """
        Инвалидирует кэш по паттерну

        Args:
            pattern: Паттерн для поиска ключей кэша

        Returns:
            Количество удаленных ключей
        """
        try:
            keys = await redis_manager.keys(f"{self.cache_prefix}{pattern}")
            deleted_count = 0

            for key in keys:
                if await redis_manager.del_record(key):
                    deleted_count += 1

            logger.info(
                f"Invalidated {deleted_count} cache keys for pattern: {pattern}"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Error invalidating cache pattern: {e}")
            return 0

    async def clear_all_cache(self) -> int:
        """
        Очищает весь кэш API

        Returns:
            Количество удаленных ключей
        """
        return await self.invalidate_cache_pattern("*")

    def get_cache_headers(self, ttl: int) -> dict:
        """
        Возвращает заголовки для кэширования

        Args:
            ttl: Время жизни кэша в секундах

        Returns:
            Словарь заголовков
        """
        return {
            "Cache-Control": f"public, max-age={ttl}",
            "ETag": f'W/"cache-{ttl}"',
            "Vary": "Accept-Encoding, Accept-Language",
        }


# Глобальный экземпляр кэша API
api_cache = APICache()
