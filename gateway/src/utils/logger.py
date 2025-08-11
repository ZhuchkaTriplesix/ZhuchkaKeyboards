import logging
import sys
from typing import Optional

# Настраиваем root logger для вывода всех сообщений
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True,
)


def setup_logger(
    name: str = __name__,
    level: int = logging.DEBUG,
    format_string: Optional[str] = None,
    log_to_file: bool = False,
    log_file_path: str = "app.log",
) -> logging.Logger:
    """
    Централизованная настройка логгера

    Args:
        name: Имя логгера (обычно __name__)
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Формат сообщений лога
        log_to_file: Логировать ли в файл
        log_file_path: Путь к файлу лога

    Returns:
        Настроенный логгер

    Raises:
        OSError: Если не удается создать файл лога
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Хендлеры не добавляем, root logger уже настроен
    if log_to_file:
        try:
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(level)
            formatter = logging.Formatter(
                format_string or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError as e:
            logger.error(f"Не удалось создать файл лога {log_file_path}: {e}")
            # Продолжаем работу без файлового логгера

    return logger


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Получить логгер по имени

    Args:
        name: Имя логгера

    Returns:
        Логгер
    """
    return logging.getLogger(name)


def init_root_logger() -> logging.Logger:
    """
    Инициализация корневого логгера с настройками для приложения

    Returns:
        Настроенный корневой логгер
    """
    # Отключаем логи от uvicorn и других библиотек на уровне INFO
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)  # Включаем access-логи
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    # Отключаем логи MongoDB драйвера
    logging.getLogger("pymongo").setLevel(logging.ERROR)
    logging.getLogger("motor").setLevel(logging.ERROR)
    logging.getLogger("asyncio").setLevel(logging.ERROR)

    # Настройка логов для PostgreSQL
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)

    # Настройка логов для Redis
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("aioredis").setLevel(logging.WARNING)

    return logging.getLogger("Gateway")


# Создаем корневой логгер при импорте модуля
root_logger = init_root_logger()
