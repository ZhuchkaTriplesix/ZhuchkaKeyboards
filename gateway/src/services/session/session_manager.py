"""
Менеджер сессий пользователей с Redis кэшированием
"""
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from routers.user.models import User
from services.redis.rediska import redis_manager
from utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Управление пользовательскими сессиями с Redis кэшированием"""
    
    def __init__(self):
        self.session_prefix = "user_session:"
        self.user_prefix = "user_data:"
        self.default_session_ttl = 3600  # 1 час
        self.max_sessions_per_user = 5
    
    async def create_session(
        self, 
        user_id: str, 
        user_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> str:
        """Создает новую сессию для пользователя"""
        session_id = str(uuid.uuid4())
        ttl = ttl or self.default_session_ttl
        
        # Проверяем количество активных сессий
        active_sessions = await self.get_user_active_sessions(user_id)
        if len(active_sessions) >= self.max_sessions_per_user:
            # Удаляем самую старую сессию
            oldest_session = min(active_sessions, key=lambda x: x['created_at'])
            await self.revoke_session(oldest_session['session_id'])
        
        # Создаем сессию
        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'user_agent': user_data.get('user_agent', ''),
            'ip_address': user_data.get('ip_address', ''),
            'is_active': True
        }
        
        # Сохраняем в Redis
        session_key = f"{self.session_prefix}{session_id}"
        user_sessions_key = f"{self.user_prefix}{user_id}:sessions"
        
        await redis_manager.set_record(
            session_key, 
            json.dumps(session_data), 
            ttl
        )
        
        # Добавляем сессию в список активных сессий пользователя
        await redis_manager.sadd(user_sessions_key, session_id)
        await redis_manager.expire(user_sessions_key, ttl)
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получает данные сессии по ID"""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await redis_manager.get_record(session_key)
        
        if not session_data:
            return None
        
        try:
            session = json.loads(session_data)
            # Обновляем время последней активности
            session['last_activity'] = datetime.utcnow().isoformat()
            await redis_manager.set_record(session_key, json.dumps(session))
            return session
        except json.JSONDecodeError:
            logger.error(f"Invalid session data for {session_id}")
            return None
    
    async def get_user_active_sessions(self, user_id: str) -> list[Dict[str, Any]]:
        """Получает все активные сессии пользователя"""
        user_sessions_key = f"{self.user_prefix}{user_id}:sessions"
        session_ids = await redis_manager.smembers(user_sessions_key)
        
        active_sessions = []
        for session_id in session_ids:
            session_data = await self.get_session(session_id)
            if session_data and session_data.get('is_active'):
                active_sessions.append({
                    'session_id': session_id,
                    **session_data
                })
        
        return active_sessions
    
    async def revoke_session(self, session_id: str) -> bool:
        """Отзывает (деактивирует) сессию"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return False
        
        # Удаляем сессию из Redis
        session_key = f"{self.session_prefix}{session_id}"
        user_sessions_key = f"{self.user_prefix}{session_data['user_id']}:sessions"
        
        await redis_manager.del_record(session_key)
        await redis_manager.srem(user_sessions_key, session_id)
        
        logger.info(f"Revoked session {session_id} for user {session_data['user_id']}")
        return True
    
    async def revoke_all_user_sessions(self, user_id: str) -> int:
        """Отзывает все сессии пользователя"""
        active_sessions = await self.get_user_active_sessions(user_id)
        revoked_count = 0
        
        for session in active_sessions:
            if await self.revoke_session(session['session_id']):
                revoked_count += 1
        
        logger.info(f"Revoked {revoked_count} sessions for user {user_id}")
        return revoked_count
    
    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Валидирует сессию и возвращает данные пользователя"""
        session_data = await self.get_session(session_id)
        if not session_data or not session_data.get('is_active'):
            return None
        
        # Проверяем время последней активности
        last_activity = datetime.fromisoformat(session_data['last_activity'])
        if datetime.utcnow() - last_activity > timedelta(hours=24):
            await self.revoke_session(session_id)
            return None
        
        return session_data
    
    async def get_user_by_session(self, session_id: str, db: AsyncSession) -> Optional[User]:
        """Получает пользователя по сессии"""
        session_data = await self.validate_session(session_id)
        if not session_data:
            return None
        
        # Получаем пользователя из БД
        result = await db.execute(
            select(User).where(User.id == session_data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await self.revoke_session(session_id)
            return None
        
        return user


# Глобальный экземпляр менеджера сессий
session_manager = SessionManager()
