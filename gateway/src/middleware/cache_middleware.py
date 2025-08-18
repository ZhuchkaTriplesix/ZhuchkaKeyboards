"""
Middleware для автоматического кэширования API ответов
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from services.cache.api_cache import api_cache
from services.session.session_manager import session_manager
from utils.logger import get_logger

logger = get_logger(__name__)


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware для автоматического кэширования API ответов"""

    def __init__(self, app, cache_ttl: int = 300):
        super().__init__(app)
        self.cache_ttl = cache_ttl

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Пропускаем кэширование для не-GET запросов
        if request.method != "GET":
            return await call_next(request)

        # Получаем пользователя из сессии для персонализированного кэша
        user_id = None
        session_id = request.cookies.get("session_id")
        if session_id:
            session_data = await session_manager.get_session(session_id)
            if session_data:
                user_id = session_data.get("user_id")

        # Генерируем ключ кэша
        cache_key = api_cache.generate_cache_key(request, user_id)

        # Пытаемся получить кэшированный ответ
        cached_response = await api_cache.get_cached_response(cache_key)
        if cached_response:
            return cached_response

        # Если кэша нет, выполняем запрос
        start_time = time.time()
        response = await call_next(request)
        response_time = time.time() - start_time

        # Добавляем заголовок времени выполнения  
        response.headers["X-Response-Time"] = f"{response_time:.3f}s"

        # Кэшируем ответ если это возможно
        if api_cache.is_cacheable(request, response):
            # Добавляем заголовки кэширования
            cache_headers = api_cache.get_cache_headers(self.cache_ttl)
            for key, value in cache_headers.items():
                response.headers[key] = value

            # Читаем тело ответа для кэширования
            try:
                if isinstance(response, StreamingResponse):
                    # Для StreamingResponse собираем body из итератора
                    response_body = b""
                    async for chunk in response.body_iterator:
                        response_body += chunk
                    
                    # Создаем новый ответ с собранным body
                    response = Response(
                        content=response_body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type
                    )
                else:
                    # Для обычного Response используем body
                    response_body = getattr(response, 'body', b'')
                
                # Кэшируем ответ
                await api_cache.cache_response(cache_key, response, response_body, self.cache_ttl)
                
            except Exception as e:
                logger.error(f"Error caching response: {e}")
        
        # Добавляем X-Cache MISS только ПОСЛЕ кэширования
        response.headers["X-Cache"] = "MISS"

        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware для управления заголовками кэширования"""

    def __init__(self, app):
        super().__init__(app)
        self.no_cache_paths = {"/api/auth/*", "/api/user/profile", "/api/admin/*"}
        self.long_cache_paths = {
            "/api/static/*": 86400,  # 24 часа
            "/api/public/*": 3600,  # 1 час
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Проверяем путь запроса
        path = request.url.path

        # Устанавливаем заголовки кэширования
        if any(
            path.startswith(no_cache_path.replace("*", ""))
            for no_cache_path in self.no_cache_paths
        ):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        else:
            # Ищем подходящий TTL для пути
            cache_ttl = None
            for pattern, ttl in self.long_cache_paths.items():
                if path.startswith(pattern.replace("*", "")):
                    cache_ttl = ttl
                    break

            if cache_ttl:
                response.headers["Cache-Control"] = f"public, max-age={cache_ttl}"
                response.headers["ETag"] = f'W/"cache-{cache_ttl}"'

        return response
