"""
Тесты для системы кэширования API
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import Request, Response
from starlette.responses import Response as StarletteResponse

from services.cache.api_cache import APICache, api_cache


class TestAPICache:
    """Тесты для класса APICache"""

    def test_init(self):
        """Тест инициализации кэша"""
        cache = APICache()
        assert cache.cache_prefix == "api_cache:"
        assert cache.default_ttl == 300
        assert cache.cacheable_methods == {"GET", "HEAD"}
        assert cache.cacheable_status_codes == {200, 201, 304}

    def test_generate_cache_key(self):
        """Тест генерации ключа кэша"""
        cache = APICache()

        # Создаем мок запроса
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = "http://localhost:8001/api/test"
        mock_request.query_params = {"param": "value"}
        mock_request.headers = {"accept": "application/json"}

        # Генерируем ключ без пользователя
        key1 = cache.generate_cache_key(mock_request)
        assert key1.startswith("api_cache:")
        assert len(key1) > 20

        # Генерируем ключ с пользователем
        key2 = cache.generate_cache_key(mock_request, "user123")
        assert key2.startswith("api_cache:")
        assert key1 != key2  # Ключи должны отличаться

    def test_is_cacheable_get_request(self):
        """Тест проверки возможности кэширования GET запроса"""
        cache = APICache()

        mock_request = Mock(spec=Request)
        mock_request.method = "GET"

        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}

        assert cache.is_cacheable(mock_request, mock_response) is True

    def test_is_cacheable_post_request(self):
        """Тест проверки возможности кэширования POST запроса"""
        cache = APICache()

        mock_request = Mock(spec=Request)
        mock_request.method = "POST"

        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}

        assert cache.is_cacheable(mock_request, mock_response) is False

    def test_is_cacheable_error_response(self):
        """Тест проверки возможности кэширования ответа с ошибкой"""
        cache = APICache()

        mock_request = Mock(spec=Request)
        mock_request.method = "GET"

        mock_response = Mock(spec=Response)
        mock_response.status_code = 500
        mock_response.headers = {}

        assert cache.is_cacheable(mock_request, mock_response) is False

    def test_is_cacheable_no_cache_headers(self):
        """Тест проверки заголовков no-cache"""
        cache = APICache()

        mock_request = Mock(spec=Request)
        mock_request.method = "GET"

        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {"cache-control": "no-cache"}

        assert cache.is_cacheable(mock_request, mock_response) is False

    def test_get_cache_headers(self):
        """Тест генерации заголовков кэширования"""
        cache = APICache()
        ttl = 600

        headers = cache.get_cache_headers(ttl)

        assert headers["Cache-Control"] == f"public, max-age={ttl}"
        assert headers["ETag"] == f'W/"cache-{ttl}"'
        assert headers["Vary"] == "Accept-Encoding, Accept-Language"


class TestGlobalAPICache:
    """Тесты для глобального экземпляра api_cache"""

    def test_global_instance_exists(self):
        """Тест, что глобальный экземпляр существует"""
        assert api_cache is not None
        assert isinstance(api_cache, APICache)


# Тесты для middleware кэширования
class TestCacheMiddleware:
    """Тесты для middleware кэширования"""

    def test_cache_middleware_init(self):
        """Тест инициализации middleware"""
        from middleware.cache_middleware import CacheMiddleware

        mock_app = Mock()
        middleware = CacheMiddleware(mock_app, cache_ttl=600)

        assert middleware.cache_ttl == 600
        assert middleware.app == mock_app


if __name__ == "__main__":
    pytest.main([__file__])
