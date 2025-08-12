"""
Тесты для менеджера сессий пользователей
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from services.session.session_manager import SessionManager, session_manager
from routers.user.models import User


@pytest.fixture
def session_manager_instance():
    """Создает экземпляр менеджера сессий для тестирования"""
    return SessionManager()


@pytest.fixture
def mock_user_data():
    """Тестовые данные пользователя"""
    return {"user_agent": "Mozilla/5.0 (Test Browser)", "ip_address": "127.0.0.1"}


@pytest.fixture
def mock_session_data():
    """Тестовые данные сессии"""
    return {
        "user_id": "test-user-123",
        "created_at": datetime.utcnow().isoformat(),
        "last_activity": datetime.utcnow().isoformat(),
        "user_agent": "Mozilla/5.0 (Test Browser)",
        "ip_address": "127.0.0.1",
        "is_active": True,
    }


class TestSessionManager:
    """Тесты для класса SessionManager"""

    @pytest.mark.asyncio
    async def test_create_session_success(
        self, session_manager_instance, mock_user_data
    ):
        """Тест успешного создания сессии"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.set_record.return_value = True
            mock_redis.sadd.return_value = 1
            mock_redis.expire.return_value = True

            session_id = await session_manager_instance.create_session(
                "test-user-123", mock_user_data
            )

            assert session_id is not None
            assert len(session_id) > 0
            mock_redis.set_record.assert_called_once()
            mock_redis.sadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_session_max_sessions_limit(
        self, session_manager_instance, mock_user_data
    ):
        """Тест ограничения максимального количества сессий"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            # Симулируем максимальное количество активных сессий
            mock_redis.smembers.return_value = [
                "session1",
                "session2",
                "session3",
                "session4",
                "session5",
            ]
            mock_redis.get_record.side_effect = [
                '{"created_at": "2023-01-01T00:00:00"}',  # Самая старая сессия
                '{"created_at": "2023-01-02T00:00:00"}',
                '{"created_at": "2023-01-03T00:00:00"}',
                '{"created_at": "2023-01-04T00:00:00"}',
                '{"created_at": "2023-01-05T00:00:00"}',
            ]
            mock_redis.set_record.return_value = True
            mock_redis.sadd.return_value = 1
            mock_redis.expire.return_value = True
            mock_redis.del_record.return_value = True
            mock_redis.srem.return_value = 1

            session_id = await session_manager_instance.create_session(
                "test-user-123", mock_user_data
            )

            # Проверяем, что старая сессия была удалена
            mock_redis.del_record.assert_called_once()
            assert session_id is not None

    @pytest.mark.asyncio
    async def test_get_session_success(
        self, session_manager_instance, mock_session_data
    ):
        """Тест успешного получения сессии"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.get_record.return_value = (
                '{"user_id": "test-user-123", "is_active": true}'
            )
            mock_redis.set_record.return_value = True

            session = await session_manager_instance.get_session("test-session-123")

            assert session is not None
            assert session["user_id"] == "test-user-123"
            assert session["is_active"] is True
            mock_redis.set_record.assert_called_once()  # Обновление last_activity

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, session_manager_instance):
        """Тест получения несуществующей сессии"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.get_record.return_value = None

            session = await session_manager_instance.get_session("non-existent-session")

            assert session is None

    @pytest.mark.asyncio
    async def test_get_session_invalid_json(self, session_manager_instance):
        """Тест получения сессии с некорректными JSON данными"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.get_record.return_value = "invalid-json-data"

            session = await session_manager_instance.get_session("test-session-123")

            assert session is None

    @pytest.mark.asyncio
    async def test_revoke_session_success(
        self, session_manager_instance, mock_session_data
    ):
        """Тест успешного отзыва сессии"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.get_record.return_value = '{"user_id": "test-user-123"}'
            mock_redis.del_record.return_value = True
            mock_redis.srem.return_value = 1

            result = await session_manager_instance.revoke_session("test-session-123")

            assert result is True
            mock_redis.del_record.assert_called_once()
            mock_redis.srem.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_session_not_found(self, session_manager_instance):
        """Тест отзыва несуществующей сессии"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.get_record.return_value = None

            result = await session_manager_instance.revoke_session(
                "non-existent-session"
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_revoke_all_user_sessions(self, session_manager_instance):
        """Тест отзыва всех сессий пользователя"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.smembers.return_value = ["session1", "session2", "session3"]
            mock_redis.get_record.side_effect = [
                '{"user_id": "test-user-123"}',
                '{"user_id": "test-user-123"}',
                '{"user_id": "test-user-123"}',
            ]
            mock_redis.del_record.return_value = True
            mock_redis.srem.return_value = 1

            # Мокаем метод revoke_session
            with patch.object(
                session_manager_instance, "revoke_session", return_value=True
            ):
                result = await session_manager_instance.revoke_all_user_sessions(
                    "test-user-123"
                )

            assert result == 3

    @pytest.mark.asyncio
    async def test_validate_session_success(
        self, session_manager_instance, mock_session_data
    ):
        """Тест успешной валидации сессии"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.get_record.return_value = (
                '{"is_active": true, "last_activity": "2023-12-01T12:00:00"}'
            )
            mock_redis.set_record.return_value = True

            session = await session_manager_instance.validate_session(
                "test-session-123"
            )

            assert session is not None
            assert session["is_active"] is True

    @pytest.mark.asyncio
    async def test_validate_session_expired(self, session_manager_instance):
        """Тест валидации истекшей сессии"""
        expired_time = (datetime.utcnow() - timedelta(hours=25)).isoformat()

        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.get_record.return_value = (
                f'{{"is_active": true, "last_activity": "{expired_time}"}}'
            )
            mock_redis.del_record.return_value = True
            mock_redis.srem.return_value = 1

            session = await session_manager_instance.validate_session(
                "test-session-123"
            )

            assert session is None
            mock_redis.del_record.assert_called_once()  # Сессия должна быть удалена

    @pytest.mark.asyncio
    async def test_validate_session_inactive(self, session_manager_instance):
        """Тест валидации неактивной сессии"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.get_record.return_value = (
                '{"is_active": false, "last_activity": "2023-12-01T12:00:00"}'
            )

            session = await session_manager_instance.validate_session(
                "test-session-123"
            )

            assert session is None

    @pytest.mark.asyncio
    async def test_get_user_by_session_success(self, session_manager_instance):
        """Тест получения пользователя по сессии"""
        mock_user = MagicMock()
        mock_user.id = "test-user-123"

        with patch("services.redis.rediska.redis_manager") as mock_redis:
            mock_redis.get_record.return_value = '{"user_id": "test-user-123", "is_active": true, "last_activity": "2023-12-01T12:00:00"}'
            mock_redis.set_record.return_value = True

            with patch.object(
                session_manager_instance, "validate_session"
            ) as mock_validate:
                mock_validate.return_value = {"user_id": "test-user-123"}

                with patch("sqlalchemy.ext.asyncio.AsyncSession") as mock_db:
                    mock_db.execute.return_value.scalar_one_or_none.return_value = (
                        mock_user
                    )

                    user = await session_manager_instance.get_user_by_session(
                        "test-session-123", mock_db
                    )

                    assert user is not None
                    assert user.id == "test-user-123"

    @pytest.mark.asyncio
    async def test_get_user_by_session_invalid_session(self, session_manager_instance):
        """Тест получения пользователя по невалидной сессии"""
        with patch.object(
            session_manager_instance, "validate_session", return_value=None
        ):
            with patch("sqlalchemy.ext.asyncio.AsyncSession") as mock_db:
                user = await session_manager_instance.get_user_by_session(
                    "invalid-session", mock_db
                )

                assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_session_user_not_found(self, session_manager_instance):
        """Тест получения пользователя по сессии, когда пользователь не найден в БД"""
        with patch.object(
            session_manager_instance, "validate_session"
        ) as mock_validate:
            mock_validate.return_value = {"user_id": "test-user-123"}

            with patch("sqlalchemy.ext.asyncio.AsyncSession") as mock_db:
                mock_db.execute.return_value.scalar_one_or_none.return_value = None

                with patch.object(
                    session_manager_instance, "revoke_session", return_value=True
                ) as mock_revoke:
                    user = await session_manager_instance.get_user_by_session(
                        "test-session-123", mock_db
                    )

                    assert user is None
                    mock_revoke.assert_called_once_with("test-session-123")


class TestSessionManagerIntegration:
    """Интеграционные тесты для менеджера сессий"""

    @pytest.mark.asyncio
    async def test_session_lifecycle(self, session_manager_instance, mock_user_data):
        """Тест полного жизненного цикла сессии"""
        with patch("services.redis.rediska.redis_manager") as mock_redis:
            # Создание сессии
            mock_redis.set_record.return_value = True
            mock_redis.sadd.return_value = 1
            mock_redis.expire.return_value = True

            session_id = await session_manager_instance.create_session(
                "test-user-123", mock_user_data
            )

            assert session_id is not None

            # Получение сессии
            mock_redis.get_record.return_value = '{"user_id": "test-user-123", "is_active": true, "last_activity": "2023-12-01T12:00:00"}'
            mock_redis.set_record.return_value = True

            session = await session_manager_instance.get_session(session_id)
            assert session is not None

            # Отзыв сессии
            mock_redis.del_record.return_value = True
            mock_redis.srem.return_value = 1

            result = await session_manager_instance.revoke_session(session_id)
            assert result is True

            # Проверка, что сессия больше не существует
            mock_redis.get_record.return_value = None
            session = await session_manager_instance.get_session(session_id)
            assert session is None


# Тесты для глобального экземпляра
class TestGlobalSessionManager:
    """Тесты для глобального экземпляра session_manager"""

    @pytest.mark.asyncio
    async def test_global_instance_exists(self):
        """Тест, что глобальный экземпляр существует"""
        assert session_manager is not None
        assert isinstance(session_manager, SessionManager)

    @pytest.mark.asyncio
    async def test_global_instance_configuration(self):
        """Тест конфигурации глобального экземпляра"""
        assert session_manager.session_prefix == "user_session:"
        assert session_manager.user_prefix == "user_data:"
        assert session_manager.default_session_ttl == 3600
        assert session_manager.max_sessions_per_user == 5


if __name__ == "__main__":
    pytest.main([__file__])
