"""
Конфигурация Pydantic для использования orjson
"""
import orjson
from pydantic import ConfigDict


def get_pydantic_config() -> ConfigDict:
    """
    Возвращает конфигурацию Pydantic с настройками orjson
    """
    return ConfigDict(
        # Используем orjson для сериализации
        json_encoders={
            # Настройки для orjson
            dict: lambda v: orjson.dumps(v, option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY),
            list: lambda v: orjson.dumps(v, option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY),
        },
        # Другие настройки Pydantic
        validate_assignment=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        str_min_length=0,
        str_max_length=None,
        extra="ignore",
    )


# Глобальная конфигурация по умолчанию
default_config = get_pydantic_config()
