"""
Centralized middleware collection for ZhuchkaKeyboards
"""

from .rate_limiter import RateLimiterMiddleware
from .database import DBSessionMiddleware
from .metrics import HTTPMetricsMiddleware, get_metrics_response
from .security import SecurityHeadersMiddleware, RequestValidationMiddleware
from .cache_middleware import CacheMiddleware, CacheControlMiddleware

__all__ = [
    # Rate limiting
    "RateLimiterMiddleware",
    
    # Database management
    "DBSessionMiddleware",
    
    # Metrics collection
    "HTTPMetricsMiddleware",
    "get_metrics_response",
    
    # Security
    "SecurityHeadersMiddleware", 
    "RequestValidationMiddleware",
    
    # Caching
    "CacheMiddleware",
    "CacheControlMiddleware",
]


def get_default_middleware_stack():
    """
    Возвращает список middleware в рекомендуемом порядке применения
    
    Порядок важен:
    1. Security headers - применяются первыми
    2. Request validation - валидация входящих запросов
    3. Metrics - сбор метрик (должен быть самым внешним для перехвата всех запросов)
    4. Rate limiting - ограничение частоты запросов
    5. Cache - кеширование ответов
    6. Database - управление сессиями БД (должно быть последним перед обработкой)
    """
    return [
        {
            "middleware": SecurityHeadersMiddleware,
            "description": "Adds security headers to responses"
        },
        {
            "middleware": RequestValidationMiddleware,
            "description": "Validates request size and headers"
        },
        {
            "middleware": HTTPMetricsMiddleware,
            "description": "Collects HTTP metrics for monitoring"
        },
        {
            "middleware": RateLimiterMiddleware,
            "description": "Rate limiting by IP address",
            "kwargs": {"max_requests": 999999, "time_window": 60}
        },
        {
            "middleware": CacheMiddleware,
            "description": "API response caching",
            "kwargs": {"cache_ttl": 300}
        },
        {
            "middleware": DBSessionMiddleware,
            "description": "Manages database sessions and transactions"
        }
    ]


def apply_middleware_stack(app, middleware_stack=None):
    """
    Применяет стек middleware к приложению FastAPI
    
    Args:
        app: Экземпляр FastAPI приложения
        middleware_stack: Список middleware для применения (по умолчанию - стандартный стек)
    """
    if middleware_stack is None:
        middleware_stack = get_default_middleware_stack()
    
    # Применяем middleware в обратном порядке (FastAPI применяет их в стеке)
    for middleware_config in reversed(middleware_stack):
        middleware_class = middleware_config["middleware"]
        kwargs = middleware_config.get("kwargs", {})
        
        app.add_middleware(middleware_class, **kwargs)
        print(f"Applied middleware: {middleware_class.__name__} - {middleware_config['description']}")
    
    # Добавляем /metrics endpoint
    from middleware.metrics import add_metrics_endpoint
    add_metrics_endpoint(app)
    print("Metrics endpoint added")
