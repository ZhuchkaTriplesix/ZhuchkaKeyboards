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
    Middleware для сбора базовых HTTP метрик
    
    Собирает метрики:
    - Общее количество запросов по методам, эндпоинтам и статус кодам
    - Время выполнения запросов
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Создаем базовые метрики
        self.http_requests_total = Counter(
            'gateway_http_requests_total', 
            'Total HTTP requests', 
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration_seconds = Histogram(
            'gateway_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint']
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
        
        # Обновляем счетчики
        self.http_requests_total.labels(
            method=method, 
            endpoint=endpoint, 
            status_code=status_code
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method, 
            endpoint=endpoint
        ).observe(duration)
        
        return response


def get_metrics_response() -> Response:
    """Возвращает все метрики Prometheus в текстовом формате"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
