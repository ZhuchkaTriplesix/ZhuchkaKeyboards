"""
Security middleware для обеспечения безопасности приложения
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from utils.logger import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware для добавления security headers
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }

    async def dispatch(self, request: Request, call_next):
        """Добавление security headers к ответу"""
        response = await call_next(request)
        
        # Добавляем security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
            
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware для базовой валидации запросов
    """
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next):
        """Валидация размера запроса и других параметров"""
        
        # Проверяем размер запроса
        if hasattr(request, 'headers') and 'content-length' in request.headers:
            content_length = int(request.headers.get('content-length', 0))
            if content_length > self.max_request_size:
                logger.warning(f"Request too large: {content_length} bytes from {request.client.host}")
                return Response(
                    content="Request entity too large",
                    status_code=413
                )
        
        # Базовая валидация User-Agent (блокируем подозрительные)
        user_agent = request.headers.get('user-agent', '').lower()
        suspicious_agents = ['scanner', 'crawler', 'bot', 'spider']
        
        # Разрешаем известные боты
        allowed_bots = ['googlebot', 'bingbot', 'slackbot', 'telegrambot']
        
        is_suspicious = any(agent in user_agent for agent in suspicious_agents)
        is_allowed = any(bot in user_agent for bot in allowed_bots)
        
        if is_suspicious and not is_allowed and user_agent != '':
            logger.warning(f"Suspicious User-Agent blocked: {user_agent} from {request.client.host}")
            return Response(
                content="Forbidden",
                status_code=403
            )
        
        return await call_next(request)
