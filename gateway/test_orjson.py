#!/usr/bin/env python3
"""
Тест для проверки работы orjson
"""

import time
import orjson
from pydantic import BaseModel
from pydantic_config import default_config


class TestModel(BaseModel):
    id: int
    name: str
    data: dict
    items: list

    model_config = default_config


def test_orjson_performance():
    """Тест производительности orjson vs стандартного json"""

    # Тестовые данные
    test_data = {
        "id": 1,
        "name": "test",
        "data": {"key": "value", "nested": {"deep": "data"}},
        "items": [1, 2, 3, 4, 5, "string", True, None],
        "timestamp": time.time(),
    }

    # Создаем Pydantic модель
    model = TestModel(**test_data)

    print("Тестируем orjson...")

    # Тест сериализации
    start_time = time.time()
    for _ in range(10000):
        orjson.dumps(test_data)
    orjson_time = time.time() - start_time

    print(f"orjson сериализация: {orjson_time:.4f} сек")

    # Тест Pydantic с orjson
    start_time = time.time()
    for _ in range(10000):
        model.model_dump_json()
    pydantic_orjson_time = time.time() - start_time

    print(f"Pydantic + orjson: {pydantic_orjson_time:.4f} сек")

    # Тест десериализации
    json_str = orjson.dumps(test_data)

    start_time = time.time()
    for _ in range(10000):
        orjson.loads(json_str)
    orjson_deserialize_time = time.time() - start_time

    print(f"orjson десериализация: {orjson_deserialize_time:.4f} сек")

    print(f"\nОбщее время orjson: {orjson_time + orjson_deserialize_time:.4f} сек")
    print(f"Общее время Pydantic + orjson: {pydantic_orjson_time:.4f} сек")


if __name__ == "__main__":
    test_orjson_performance()
