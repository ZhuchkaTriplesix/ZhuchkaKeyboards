"""
Rate limiting middleware для защиты от DDoS атак
"""

from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import Request
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logger import get_logger

logger = get_logger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware для ограничения частоты запросов по IP адресу
    
    Args:
        max_requests: Максимальное количество запросов в временном окне
        time_window: Временное окно в секундах
    """
    
    def __init__(self, app, max_requests: int = 999999, time_window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_logs: Dict[str, List[datetime]] = {}

    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с проверкой rate limit"""
        client_ip = request.client.host or "unknown"
        current_time = datetime.now()
        
        # Очищаем старые записи
        self._cleanup_old_entries(current_time)
        
        # Проверяем лимит для данного IP
        if client_ip in self.request_logs:
            if len(self.request_logs[client_ip]) >= self.max_requests:
                retry_after = self._calculate_retry_after(client_ip, current_time)
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return ORJSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Too many requests. Limit is {self.max_requests} per minute.",
                        "retry_after": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )
            self.request_logs[client_ip].append(current_time)
        else:
            self.request_logs[client_ip] = [current_time]

        return await call_next(request)

    def _cleanup_old_entries(self, current_time: datetime) -> None:
        """Удаление старых записей вне временного окна"""
        cutoff_time = current_time - timedelta(seconds=self.time_window)
        for ip in list(self.request_logs.keys()):
            self.request_logs[ip] = [
                t for t in self.request_logs[ip] if t > cutoff_time
            ]
            if not self.request_logs[ip]:
                del self.request_logs[ip]

    def _calculate_retry_after(self, ip: str, current_time: datetime) -> int:
        """Вычисление времени до следующего разрешенного запроса"""
        oldest_request = min(self.request_logs[ip])
        time_passed = (current_time - oldest_request).total_seconds()
        return max(1, int(self.time_window - time_passed))
