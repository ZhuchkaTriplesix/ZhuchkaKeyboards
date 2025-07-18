from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from starlette.responses import JSONResponse
from typing import Dict, List
from routers import Router
from config import mongo_cfg
import asyncio
import os
from utils.logger import get_logger

from starlette.responses import JSONResponse

# Инициализируем логгер
logger = get_logger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 20, time_window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_logs: Dict[str, List[datetime]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host or "unknown"
        current_time = datetime.now()
        self._cleanup_old_entries(current_time)
        if client_ip in self.request_logs:
            if len(self.request_logs[client_ip]) >= self.max_requests:
                retry_after = self._calculate_retry_after(client_ip, current_time)
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Too many requests. Limit is {self.max_requests} per minute.",
                        "retry_after": retry_after
                    },
                    headers={"Retry-After": str(retry_after)}
                )
            self.request_logs[client_ip].append(current_time)
        else:
            self.request_logs[client_ip] = [current_time]

        return await call_next(request)

    def _cleanup_old_entries(self, current_time: datetime):
        cutoff_time = current_time - timedelta(seconds=self.time_window)
        for ip in list(self.request_logs.keys()):
            self.request_logs[ip] = [t for t in self.request_logs[ip] if t > cutoff_time]
            if not self.request_logs[ip]:
                del self.request_logs[ip]

    def _calculate_retry_after(self, ip: str, current_time: datetime) -> int:
        oldest_request = min(self.request_logs[ip])
        time_passed = (current_time - oldest_request).total_seconds()
        return max(1, int(self.time_window - time_passed))


class App:
    def __init__(self):
        self._app: FastAPI = FastAPI(
            title="Gateway API",
            description="Gateway API for ZhuchkaKeyboards",
            docs_url=None,
            redoc_url=None,
            openapi_url="/api/openapi.json",
        )
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "DELETE", "PATCH"],
            allow_headers=["*"]
        )
        self._app.add_middleware(RateLimiterMiddleware)
        self._register_routers()

    def _register_routers(self) -> None:
        for router, prefix, tags in Router.routers:
            self._app.include_router(router=router, prefix=prefix, tags=tags)

    @property
    def app(self) -> FastAPI:
        return self._app
