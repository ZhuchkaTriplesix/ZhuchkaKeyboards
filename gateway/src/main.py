import secrets
from contextvars import ContextVar
from typing import Final, Optional
from fastapi import Depends, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from starlette import status
from starlette.responses import HTMLResponse
from configuration.app import App
from utils.responses import api_responses
from utils.logger import get_logger
from main_schemas import TestSchema

# Инициализируем логгер
logger = get_logger(__name__)

REQUEST_ID_CTX_KEY: Final[str] = "request_id"
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar(
    REQUEST_ID_CTX_KEY, default=None
)


def get_request_id() -> Optional[str]:
    return _request_id_ctx_var.get()


# Создаем экземпляр приложения
app = App().app

# Простые HTTP метрики для Grafana
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Создаем базовые метрики
http_requests_total = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Middleware to collect HTTP metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    method = request.method
    endpoint = request.url.path
    status_code = str(response.status_code)
    
    http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    return response

@app.get("/metrics")
def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def get_current_username(
    credentials: HTTPBasicCredentials = Depends(HTTPBasic()),
) -> str:
    correct_username = secrets.compare_digest(credentials.username, "123")
    correct_password = secrets.compare_digest(credentials.password, "123")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get(path="/api/docs", response_class=HTMLResponse, responses=api_responses())
async def get_docs(username: str = Depends(get_current_username)) -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title="docs")


@app.get(path="/api/test", responses=api_responses(success_model=TestSchema))
async def test_responses():
    return {"hello": "world"}


# Disabled catch-all for debugging
# @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
# async def catch_all(path: str):
#     raise HTTPException(status_code=404, detail="Not Found")
