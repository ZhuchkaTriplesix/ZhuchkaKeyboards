"""
Prometheus metrics collection for ZhuchkaKeyboards application
"""

import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Application info
app_info = Info("app_info", "Application info")
app_info.info(
    {
        "app_name": "ZhuchkaKeyboards Gateway",
        "version": "1.0.0",
        "description": "Keyboard manufacturing management system",
    }
)

# HTTP Metrics
http_requests_total = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

# Database Metrics
db_connections_total = Gauge(
    "db_connections_total", "Current number of database connections"
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
)

db_queries_total = Counter(
    "db_queries_total", "Total database queries", ["operation", "table", "status"]
)

# Redis Metrics
redis_operations_total = Counter(
    "redis_operations_total", "Total Redis operations", ["operation", "status"]
)

redis_connection_pool_size = Gauge(
    "redis_connection_pool_size", "Current Redis connection pool size"
)

# Business Metrics
orders_total = Counter("orders_total", "Total orders created", ["status"])

orders_processing_time_seconds = Histogram(
    "orders_processing_time_seconds", "Order processing time in seconds", ["stage"]
)

production_tasks_total = Counter(
    "production_tasks_total", "Total production tasks", ["stage", "status"]
)

quality_checks_total = Counter(
    "quality_checks_total", "Total quality checks", ["status"]
)

inventory_levels = Gauge(
    "inventory_levels", "Current inventory levels", ["item_sku", "warehouse_code"]
)

# Active connections and sessions
active_sessions = Gauge("active_sessions_total", "Number of active user sessions")

websocket_connections = Gauge(
    "websocket_connections_total", "Number of active WebSocket connections"
)

# Error Metrics
errors_total = Counter(
    "errors_total", "Total application errors", ["error_type", "component"]
)

# Cache Metrics
cache_operations_total = Counter(
    "cache_operations_total", "Total cache operations", ["operation", "result"]
)

cache_hit_ratio = Gauge("cache_hit_ratio", "Cache hit ratio percentage")


class MetricsMiddleware(BaseHTTPMiddleware):
    """Custom middleware for collecting application metrics"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Get endpoint for labeling
        endpoint = request.url.path
        method = request.method

        try:
            response = await call_next(request)
            status_code = str(response.status_code)

            # Record successful request
            http_requests_total.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()

        except Exception as e:
            # Record error
            errors_total.labels(error_type=type(e).__name__, component="api").inc()

            # Still need to track the request
            http_requests_total.labels(
                method=method, endpoint=endpoint, status_code="500"
            ).inc()

            raise

        finally:
            # Record request duration
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method, endpoint=endpoint
            ).observe(duration)

        return response


class PrometheusMetrics:
    """Main metrics collection class"""

    def __init__(self):
        self.instrumentator = None

    def init_app(self, app: FastAPI) -> None:
        """Initialize Prometheus metrics for FastAPI application"""

        # Initialize instrumentator with basic configuration
        self.instrumentator = Instrumentator()

        # Add default metrics
        self.instrumentator.add(metrics.default())
        self.instrumentator.add(metrics.latency())

        # Initialize instrumentator
        self.instrumentator.instrument(app)

        # Add custom middleware
        app.add_middleware(MetricsMiddleware)

        # Expose metrics endpoint
        self.instrumentator.expose(app, endpoint="/metrics")

    # Database metrics methods
    def record_db_query(
        self, operation: str, table: str, duration: float, success: bool = True
    ):
        """Record database query metrics"""
        status = "success" if success else "error"
        db_queries_total.labels(operation=operation, table=table, status=status).inc()
        db_query_duration_seconds.labels(operation=operation, table=table).observe(
            duration
        )

    def set_db_connections(self, count: int):
        """Set current database connections count"""
        db_connections_total.set(count)

    # Redis metrics methods
    def record_redis_operation(self, operation: str, success: bool = True):
        """Record Redis operation metrics"""
        status = "success" if success else "error"
        redis_operations_total.labels(operation=operation, status=status).inc()

    def set_redis_pool_size(self, size: int):
        """Set Redis connection pool size"""
        redis_connection_pool_size.set(size)

    # Business metrics methods
    def record_order_created(self, status: str):
        """Record new order creation"""
        orders_total.labels(status=status).inc()

    def record_order_processing_time(self, stage: str, duration: float):
        """Record order processing time"""
        orders_processing_time_seconds.labels(stage=stage).observe(duration)

    def record_production_task(self, stage: str, status: str):
        """Record production task metrics"""
        production_tasks_total.labels(stage=stage, status=status).inc()

    def record_quality_check(self, status: str):
        """Record quality check result"""
        quality_checks_total.labels(status=status).inc()

    def set_inventory_level(self, item_sku: str, warehouse_code: str, level: int):
        """Set inventory level for item"""
        inventory_levels.labels(item_sku=item_sku, warehouse_code=warehouse_code).set(
            level
        )

    # Session and connection metrics
    def set_active_sessions(self, count: int):
        """Set number of active sessions"""
        active_sessions.set(count)

    def set_websocket_connections(self, count: int):
        """Set number of WebSocket connections"""
        websocket_connections.set(count)

    # Error metrics
    def record_error(self, error_type: str, component: str):
        """Record application error"""
        errors_total.labels(error_type=error_type, component=component).inc()

    # Cache metrics
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation (hit/miss)"""
        cache_operations_total.labels(operation=operation, result=result).inc()

    def set_cache_hit_ratio(self, ratio: float):
        """Set cache hit ratio percentage"""
        cache_hit_ratio.set(ratio)


# Global metrics instance
prometheus_metrics = PrometheusMetrics()
