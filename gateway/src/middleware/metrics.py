"""
Metrics middleware для сбора метрик HTTP запросов
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from utils.logger import get_logger

logger = get_logger(__name__)


class HTTPMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware для сбора HTTP метрик и метрик кэширования
    
    Собирает метрики:
    - gateway_http_requests_total: Общее количество запросов по методам, эндпоинтам, статус кодам и статусу кэша
    - gateway_http_request_duration_seconds: Время выполнения запросов
    - gateway_cache_requests_total: Общее количество запросов к кэшу (HIT/MISS)
    - gateway_cache_hit_ratio_total: Счетчик попаданий в кэш по эндпоинтам
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Создаем базовые метрики
        self.http_requests_total = Counter(
            'gateway_http_requests_total', 
            'Total HTTP requests', 
            ['method', 'endpoint', 'status_code', 'cache_status']
        )
        
        self.http_request_duration_seconds = Histogram(
            'gateway_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'cache_status']
        )
        
        # Метрики кэширования
        self.cache_requests_total = Counter(
            'gateway_cache_requests_total',
            'Total cache requests by status',
            ['cache_status']
        )
        
        self.cache_hit_ratio = Counter(
            'gateway_cache_hit_ratio_total',
            'Cache hit ratio counter',
            ['endpoint']
        )

    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с записью метрик"""
        start_time = time.time()
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Записываем метрики
        duration = time.time() - start_time
        method = request.method
        endpoint = request.url.path
        status_code = str(response.status_code)
        
        # Определяем статус кэша из заголовка X-Cache
        cache_status = response.headers.get('X-Cache', 'NONE').upper()
        
        # Обновляем счетчики
        self.http_requests_total.labels(
            method=method, 
            endpoint=endpoint, 
            status_code=status_code,
            cache_status=cache_status
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method, 
            endpoint=endpoint,
            cache_status=cache_status
        ).observe(duration)
        
        # Записываем метрики кэширования
        if cache_status in ['HIT', 'MISS']:
            self.cache_requests_total.labels(cache_status=cache_status).inc()
            
            if cache_status == 'HIT':
                self.cache_hit_ratio.labels(endpoint=endpoint).inc()
        
        return response


def get_metrics_response() -> Response:
    """Возвращает все метрики Prometheus в текстовом формате"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
