"""
Prometheus metrics collection for ZhuchkaKeyboards application
"""

import time
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Request
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
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code", "handler"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "status_code"],
    buckets=(
        0.001,
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
        float("inf"),
    ),
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"],
)

http_request_size_bytes = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    buckets=(64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, float("inf")),
)

http_response_size_bytes = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint", "status_code"],
    buckets=(64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, float("inf")),
)

# Additional HTTP Metrics
http_requests_by_user_agent = Counter(
    "http_requests_by_user_agent_total",
    "HTTP requests grouped by user agent",
    ["user_agent_family", "user_agent_version"],
)

http_requests_by_ip = Counter(
    "http_requests_by_ip_total", "HTTP requests grouped by client IP", ["client_ip"]
)

http_slow_requests_total = Counter(
    "http_slow_requests_total",
    "Number of slow HTTP requests (>1s)",
    ["method", "endpoint", "status_code"],
)

http_errors_by_type = Counter(
    "http_errors_by_type_total",
    "HTTP errors grouped by error type",
    ["method", "endpoint", "error_type", "status_code"],
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
    """Enhanced middleware for collecting detailed HTTP metrics"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Extract request details
        endpoint = request.url.path
        method = request.method
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        request_size = request.headers.get("content-length", 0)

        # Parse user agent
        user_agent_family, user_agent_version = self._parse_user_agent(user_agent)

        # Track request in progress
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        try:
            # Record request size
            if request_size:
                try:
                    size = int(request_size)
                    http_request_size_bytes.labels(
                        method=method, endpoint=endpoint
                    ).observe(size)
                except (ValueError, TypeError):
                    pass

            response = await call_next(request)
            status_code = str(response.status_code)

            # Record response size
            response_size = response.headers.get("content-length")
            if response_size:
                try:
                    size = int(response_size)
                    http_response_size_bytes.labels(
                        method=method, endpoint=endpoint, status_code=status_code
                    ).observe(size)
                except (ValueError, TypeError):
                    pass

            # Record successful request
            http_requests_total.labels(
                method=method, endpoint=endpoint, status_code=status_code, handler="api"
            ).inc()

            # Record request by IP and user agent
            http_requests_by_ip.labels(client_ip=client_ip).inc()
            http_requests_by_user_agent.labels(
                user_agent_family=user_agent_family,
                user_agent_version=user_agent_version,
            ).inc()

        except Exception as e:
            status_code = "500"
            error_type = type(e).__name__

            # Record error metrics
            errors_total.labels(error_type=error_type, component="api").inc()
            http_errors_by_type.labels(
                method=method,
                endpoint=endpoint,
                error_type=error_type,
                status_code=status_code,
            ).inc()

            # Still track the request
            http_requests_total.labels(
                method=method, endpoint=endpoint, status_code=status_code, handler="api"
            ).inc()

            # Record by IP even for errors
            http_requests_by_ip.labels(client_ip=client_ip).inc()

            raise

        finally:
            # Track request no longer in progress
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

            # Record request duration
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).observe(duration)

            # Track slow requests (>1 second)
            if duration > 1.0:
                http_slow_requests_total.labels(
                    method=method, endpoint=endpoint, status_code=status_code
                ).inc()

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to client host
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _parse_user_agent(self, user_agent: str) -> tuple[str, str]:
        """Parse user agent string to extract family and version"""
        if not user_agent or user_agent == "unknown":
            return "unknown", "unknown"

        user_agent = user_agent.lower()

        # Simple user agent parsing
        if "chrome" in user_agent:
            family = "chrome"
        elif "firefox" in user_agent:
            family = "firefox"
        elif "safari" in user_agent and "chrome" not in user_agent:
            family = "safari"
        elif "edge" in user_agent:
            family = "edge"
        elif "opera" in user_agent:
            family = "opera"
        elif "curl" in user_agent:
            family = "curl"
        elif "postman" in user_agent:
            family = "postman"
        elif "python" in user_agent:
            family = "python"
        else:
            family = "other"

        # Extract version (simplified)
        try:
            if "/" in user_agent:
                parts = user_agent.split("/")
                for part in parts:
                    if any(char.isdigit() for char in part):
                        version = part.split()[0][:10]  # Limit length
                        break
                else:
                    version = "unknown"
            else:
                version = "unknown"
        except Exception:
            version = "unknown"

        return family, version


def init_app(app: FastAPI):
    """Initialize Prometheus metrics for FastAPI app"""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
    )

    instrumentator.instrument(app)
    instrumentator.expose(app, endpoint="/metrics")


# Global metrics instance for backward compatibility
class PrometheusMetrics:
    """Main metrics collection class"""

    def __init__(self):
        self.instrumentator = None

    def init_app(self, app: FastAPI) -> None:
        """Initialize Prometheus metrics for FastAPI application"""
        # Use simplified init_app function
        init_app(app)


# Global metrics instance
prometheus_metrics = PrometheusMetrics()
