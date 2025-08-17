"""
Модуль управления складом и инвентаризацией
"""

from .router import router
from .models import Item, Warehouse, InventoryLevel, InventoryTransaction
from .schemas import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse,
    InventoryLevelCreate,
    InventoryLevelUpdate,
    InventoryLevelResponse,
    StockMovementRequest,
)

__all__ = [
    "router",
    "Item",
    "Warehouse",
    "InventoryLevel",
    "InventoryTransaction",
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    "WarehouseCreate",
    "WarehouseUpdate",
    "WarehouseResponse",
    "InventoryLevelCreate",
    "InventoryLevelUpdate",
    "InventoryLevelResponse",
    "StockMovementRequest",
]
