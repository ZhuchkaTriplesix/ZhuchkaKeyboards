"""
Metrics middleware для сбора метрик HTTP запросов
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from utils.logger import get_logger

logger = get_logger(__name__)


def get_or_create_counter(name, description, labels):
    """Создает Counter или возвращает существующий"""
    try:
        return Counter(name, description, labels)
    except ValueError:
        # Метрика уже существует, получаем её из реестра
        for collector in REGISTRY._collector_to_names:
            if hasattr(collector, '_name') and collector._name == name:
                return collector
        # Если не нашли, возвращаем None - будет создано заново
        logger.warning(f"Could not find existing counter {name}, will create new one")
        return None


def get_or_create_histogram(name, description, labels):
    """Создает Histogram или возвращает существующий"""
    try:
        return Histogram(name, description, labels)
    except ValueError:
        # Метрика уже существует, получаем её из реестра
        for collector in REGISTRY._collector_to_names:
            if hasattr(collector, '_name') and collector._name == name:
                return collector
        # Если не нашли, возвращаем None - будет создано заново
        logger.warning(f"Could not find existing histogram {name}, will create new one")
        return None


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
        
        # Создаем базовые метрики безопасно
        self.http_requests_total = get_or_create_counter(
            'gateway_http_requests_total', 
            'Total HTTP requests', 
            ['method', 'endpoint', 'status_code', 'cache_status']
        )
        if self.http_requests_total is None:
            self.http_requests_total = Counter(
                'gateway_http_requests_total', 
                'Total HTTP requests', 
                ['method', 'endpoint', 'status_code', 'cache_status']
            )
        
        self.http_request_duration_seconds = get_or_create_histogram(
            'gateway_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'cache_status']
        )
        if self.http_request_duration_seconds is None:
            self.http_request_duration_seconds = Histogram(
                'gateway_http_request_duration_seconds',
                'HTTP request duration in seconds',
                ['method', 'endpoint', 'cache_status']
            )
        
        # Метрики кэширования
        self.cache_requests_total = get_or_create_counter(
            'gateway_cache_requests_total',
            'Total cache requests by status',
            ['cache_status']
        )
        if self.cache_requests_total is None:
            self.cache_requests_total = Counter(
                'gateway_cache_requests_total',
                'Total cache requests by status',
                ['cache_status']
            )
        
        self.cache_hit_ratio = get_or_create_counter(
            'gateway_cache_hit_ratio_total',
            'Cache hit ratio counter',
            ['endpoint']
        )
        if self.cache_hit_ratio is None:
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
    metrics_data = generate_latest()
    logger.info(f"Generated metrics data length: {len(metrics_data)}")
    logger.debug(f"Metrics preview: {metrics_data[:200]}...")
    return Response(metrics_data, media_type=CONTENT_TYPE_LATEST)


def add_metrics_endpoint(app):
    """Add /metrics endpoint to FastAPI app"""
    @app.get("/metrics")
    def metrics():
        """Prometheus metrics endpoint"""
        return get_metrics_response()
