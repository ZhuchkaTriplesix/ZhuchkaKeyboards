"""
Pydantic схемы для модуля inventory
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator

from routers.inventory.models import ItemType, ItemCategory, UnitOfMeasure


# ===== Item Schemas =====


class ItemBase(BaseModel):
    """Базовая схема товара"""

    sku: str = Field(..., min_length=1, max_length=100, description="Артикул товара")
    name: str = Field(..., min_length=1, max_length=200, description="Название товара")
    description: Optional[str] = Field(None, description="Описание товара")

    item_type: ItemType = Field(..., description="Тип товара")
    category: ItemCategory = Field(..., description="Категория товара")
    brand: Optional[str] = Field(None, max_length=100, description="Бренд")
    model: Optional[str] = Field(None, max_length=100, description="Модель")

    unit_of_measure: UnitOfMeasure = Field(..., description="Единица измерения")
    weight_kg: Optional[float] = Field(None, ge=0, description="Вес в кг")
    dimensions: Optional[str] = Field(
        None, max_length=100, description="Размеры (ДxШxВ см)"
    )

    min_stock_level: int = Field(0, ge=0, description="Минимальный уровень запасов")
    max_stock_level: Optional[int] = Field(
        None, ge=0, description="Максимальный уровень запасов"
    )
    reorder_point: Optional[int] = Field(None, ge=0, description="Точка перезаказа")
    lead_time_days: Optional[int] = Field(
        None, ge=0, description="Время поставки в днях"
    )

    unit_cost: Optional[float] = Field(None, ge=0, description="Себестоимость")
    selling_price: Optional[float] = Field(None, ge=0, description="Цена продажи")

    is_active: bool = Field(True, description="Активен ли товар")
    is_tracked: bool = Field(True, description="Отслеживается ли количество")

    @validator("max_stock_level")
    def max_greater_than_min(cls, v, values):
        if v is not None and "min_stock_level" in values:
            if v <= values["min_stock_level"]:
                raise ValueError("max_stock_level должен быть больше min_stock_level")
        return v


class ItemCreate(ItemBase):
    """Схема для создания товара"""

    pass


class ItemUpdate(BaseModel):
    """Схема для обновления товара"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)

    weight_kg: Optional[float] = Field(None, ge=0)
    dimensions: Optional[str] = Field(None, max_length=100)

    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    reorder_point: Optional[int] = Field(None, ge=0)
    lead_time_days: Optional[int] = Field(None, ge=0)

    unit_cost: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)

    is_active: Optional[bool] = None
    is_tracked: Optional[bool] = None


class ItemResponse(ItemBase):
    """Схема ответа с товаром"""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {UUID: str, datetime: lambda v: v.isoformat()}


# ===== Warehouse Schemas =====


class WarehouseBase(BaseModel):
    """Базовая схема склада"""

    name: str = Field(..., min_length=1, max_length=200, description="Название склада")
    code: str = Field(..., min_length=1, max_length=50, description="Код склада")
    description: Optional[str] = Field(None, description="Описание склада")

    address: str = Field(..., min_length=1, max_length=500, description="Адрес")
    city: str = Field(..., min_length=1, max_length=100, description="Город")
    postal_code: Optional[str] = Field(
        None, max_length=20, description="Почтовый индекс"
    )
    country: str = Field(..., min_length=1, max_length=100, description="Страна")

    contact_person: Optional[str] = Field(
        None, max_length=100, description="Контактное лицо"
    )
    phone: Optional[str] = Field(None, max_length=50, description="Телефон")
    email: Optional[str] = Field(None, max_length=100, description="Email")

    is_active: bool = Field(True, description="Активен ли склад")


class WarehouseCreate(WarehouseBase):
    """Схема для создания склада"""

    pass


class WarehouseUpdate(BaseModel):
    """Схема для обновления склада"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

    address: Optional[str] = Field(None, min_length=1, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, min_length=1, max_length=100)

    contact_person: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)

    is_active: Optional[bool] = None


class WarehouseResponse(WarehouseBase):
    """Схема ответа со складом"""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {UUID: str, datetime: lambda v: v.isoformat()}


# ===== Inventory Level Schemas =====


class InventoryLevelBase(BaseModel):
    """Базовая схема уровня запасов"""

    item_id: UUID = Field(..., description="ID товара")
    warehouse_id: UUID = Field(..., description="ID склада")
    zone_id: Optional[UUID] = Field(None, description="ID зоны склада")

    current_quantity: int = Field(0, ge=0, description="Текущее количество")
    reserved_quantity: int = Field(0, ge=0, description="Зарезервированное количество")

    location_code: Optional[str] = Field(
        None, max_length=100, description="Код места хранения"
    )
    bin_location: Optional[str] = Field(
        None, max_length=100, description="Номер ячейки"
    )

    @validator("reserved_quantity")
    def reserved_not_greater_than_current(cls, v, values):
        if "current_quantity" in values and v > values["current_quantity"]:
            raise ValueError("Зарезервированное количество не может превышать текущее")
        return v


class InventoryLevelCreate(InventoryLevelBase):
    """Схема для создания уровня запасов"""

    pass


class InventoryLevelUpdate(BaseModel):
    """Схема для обновления уровня запасов"""

    current_quantity: Optional[int] = Field(None, ge=0)
    reserved_quantity: Optional[int] = Field(None, ge=0)
    location_code: Optional[str] = Field(None, max_length=100)
    bin_location: Optional[str] = Field(None, max_length=100)


class InventoryLevelResponse(InventoryLevelBase):
    """Схема ответа с уровнем запасов"""

    id: UUID
    available_quantity: int  # Вычисляемое поле
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {UUID: str, datetime: lambda v: v.isoformat()}


# ===== Stock Movement Schemas =====


class StockMovementRequest(BaseModel):
    """Схема для движения товара"""

    item_id: UUID = Field(..., description="ID товара")
    warehouse_id: UUID = Field(..., description="ID склада")
    quantity: int = Field(..., description="Количество (+ приход, - расход)")
    reason: str = Field(
        ..., min_length=1, max_length=200, description="Причина движения"
    )
    reference_number: Optional[str] = Field(
        None, max_length=100, description="Номер документа"
    )


# ===== Search and Filter Schemas =====


class ItemSearchFilter(BaseModel):
    """Фильтры для поиска товаров"""

    search: Optional[str] = Field(None, description="Поиск по названию, SKU, описанию")
    item_type: Optional[ItemType] = None
    category: Optional[ItemCategory] = None
    brand: Optional[str] = None
    is_active: Optional[bool] = None
    low_stock: Optional[bool] = Field(None, description="Товары с низким остатком")


class InventorySearchFilter(BaseModel):
    """Фильтры для поиска запасов"""

    warehouse_id: Optional[UUID] = None
    item_id: Optional[UUID] = None
    min_quantity: Optional[int] = Field(None, ge=0)
    max_quantity: Optional[int] = Field(None, ge=0)
    zero_stock: Optional[bool] = Field(None, description="Только нулевые остатки")


# ===== Response Lists =====


class ItemListResponse(BaseModel):
    """Список товаров с пагинацией"""

    items: List[ItemResponse]
    total: int
    page: int
    size: int
    pages: int


class InventoryLevelListResponse(BaseModel):
    """Список уровней запасов с пагинацией"""

    levels: List[InventoryLevelResponse]
    total: int
    page: int
    size: int
    pages: int


class WarehouseListResponse(BaseModel):
    """Список складов с пагинацией"""

    warehouses: List[WarehouseResponse]
    total: int
    page: int
    size: int
    pages: int
