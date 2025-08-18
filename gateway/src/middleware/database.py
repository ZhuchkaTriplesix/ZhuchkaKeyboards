"""
Database session middleware для автоматического управления транзакциями
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from database.core import engine
from utils.logger import get_logger

logger = get_logger(__name__)


class DBSessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware для управления сессиями базы данных
    
    Автоматически создает сессию для каждого запроса,
    коммитит транзакцию при успешном выполнении,
    откатывает при ошибке и закрывает сессию в любом случае.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с управлением сессией БД"""
        async with AsyncSession(engine) as session:
            # Добавляем сессию в state запроса для доступа в handlers
            request.state.db = session
            
            try:
                # Выполняем запрос
                response = await call_next(request)
                
                # Коммитим транзакцию при успешном выполнении
                await session.commit()
                return response
                
            except Exception as e:
                # Откатываем транзакцию при ошибке
                await session.rollback()
                logger.error(f"Database transaction rolled back due to error: {e}")
                raise
                
            finally:
                # Закрываем сессию в любом случае
                await session.close()
