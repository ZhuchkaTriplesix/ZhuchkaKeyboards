"""
Модели для управления складом и инвентаризации
"""

import uuid
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy import (
    types,
    String,
    Boolean,
    Integer,
    Float,
    DateTime,
    Text,
    Enum,
    Numeric,
<<<<<<< HEAD
    ForeignKey,
=======
>>>>>>> performance-optimizations
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from database.core import Base
import enum


class ItemType(str, enum.Enum):
    """Типы товаров на складе"""

    COMPONENT = "component"  # Компонент клавиатуры
    FINISHED_PRODUCT = "finished_product"  # Готовое изделие
    PACKAGING = "packaging"  # Упаковка
    TOOL = "tool"  # Инструмент
    SUPPLY = "supply"  # Расходный материал


class ItemCategory(str, enum.Enum):
    """Категории товаров"""

    KEYCAPS = "keycaps"  # Клавиши
    SWITCHES = "switches"  # Переключатели
    PCB = "pcb"  # Печатная плата
    CASE = "case"  # Корпус
    CABLE = "cable"  # Кабель
    STABILIZERS = "stabilizers"  # Стабилизаторы
    LUBRICANT = "lubricant"  # Смазка
    OTHER = "other"  # Прочее


class UnitOfMeasure(str, enum.Enum):
    """Единицы измерения"""

    PIECE = "piece"  # Штука
    METER = "meter"  # Метр
    KILOGRAM = "kilogram"  # Килограмм
    LITER = "liter"  # Литр
    BOX = "box"  # Коробка
    ROLL = "roll"  # Рулон


class TransactionType(str, enum.Enum):
    """Типы складских операций"""

    INBOUND = "inbound"  # Поступление
    OUTBOUND = "outbound"  # Отгрузка
    TRANSFER = "transfer"  # Перемещение
    ADJUSTMENT = "adjustment"  # Корректировка
    RETURN = "return"  # Возврат
    DAMAGED = "damaged"  # Брак


class SupplierStatus(str, enum.Enum):
    """Статусы поставщиков"""

    ACTIVE = "active"  # Активный
    INACTIVE = "inactive"  # Неактивный
    SUSPENDED = "suspended"  # Приостановлен
    BLACKLISTED = "blacklisted"  # В черном списке


class Item(Base):
    """Товар на складе"""

    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Основная информация
    sku: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )  # Артикул
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Классификация
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False)
    category: Mapped[ItemCategory] = mapped_column(Enum(ItemCategory), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Физические характеристики
    unit_of_measure: Mapped[UnitOfMeasure] = mapped_column(
        Enum(UnitOfMeasure), nullable=False
    )
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dimensions: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # "LxWxH см"

    # Складские характеристики
    min_stock_level: Mapped[int] = mapped_column(Integer, default=0)
    max_stock_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reorder_point: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Ценовая информация
    unit_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    selling_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_tracked: Mapped[bool] = mapped_column(
        Boolean, default=True
    )  # Отслеживается ли количество

    # Связи
    inventory_levels: Mapped[List["InventoryLevel"]] = relationship(
        "InventoryLevel", back_populates="item"
    )
    transactions: Mapped[List["InventoryTransaction"]] = relationship(
        "InventoryTransaction", back_populates="item"
    )
<<<<<<< HEAD
    # supplier_items: Mapped[List["SupplierItem"]] = relationship(
    #     "SupplierItem", back_populates="item"
    # )
=======
    supplier_items: Mapped[List["SupplierItem"]] = relationship(
        "SupplierItem", back_populates="item"
    )
>>>>>>> performance-optimizations

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Warehouse(Base):
    """Склад"""

    __tablename__ = "warehouses"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Основная информация
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Адрес
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)

    # Контактная информация
    contact_person: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    inventory_levels: Mapped[List["InventoryLevel"]] = relationship(
        "InventoryLevel", back_populates="warehouse"
    )
    zones: Mapped[List["WarehouseZone"]] = relationship(
        "WarehouseZone", back_populates="warehouse"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class WarehouseZone(Base):
    """Зона склада"""

    __tablename__ = "warehouse_zones"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    warehouse_id: Mapped[UUID] = mapped_column(
<<<<<<< HEAD
        PostgresUUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
=======
        PostgresUUID(as_uuid=True), nullable=False
>>>>>>> performance-optimizations
    )

    # Основная информация
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Характеристики зоны
    zone_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # "storage", "receiving", "shipping", etc.
    temperature_controlled: Mapped[bool] = mapped_column(Boolean, default=False)
    humidity_controlled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Связи
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="zones")
    inventory_levels: Mapped[List["InventoryLevel"]] = relationship(
        "InventoryLevel", back_populates="zone"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class InventoryLevel(Base):
    """Уровень запасов товара на складе"""

    __tablename__ = "inventory_levels"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
<<<<<<< HEAD
    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("items.id"), nullable=False
    )
    warehouse_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
    )
    zone_id: Mapped[Optional[UUID]] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("warehouse_zones.id"), nullable=True
=======
    item_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
    warehouse_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), nullable=False
    )
    zone_id: Mapped[Optional[UUID]] = mapped_column(
        PostgresUUID(as_uuid=True), nullable=True
>>>>>>> performance-optimizations
    )

    # Количества
    current_quantity: Mapped[int] = mapped_column(Integer, default=0)
    reserved_quantity: Mapped[int] = mapped_column(
        Integer, default=0
    )  # Зарезервировано
<<<<<<< HEAD
=======
    available_quantity: Mapped[int] = mapped_column(
        Integer, computed="current_quantity - reserved_quantity"
    )
>>>>>>> performance-optimizations

    # Локация
    location_code: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # Код места хранения
    bin_location: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # Номер ячейки

    # Связи
    item: Mapped["Item"] = relationship("Item", back_populates="inventory_levels")
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", back_populates="inventory_levels"
    )
    zone: Mapped[Optional["WarehouseZone"]] = relationship(
        "WarehouseZone", back_populates="inventory_levels"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
<<<<<<< HEAD
    
    @property
    def available_quantity(self) -> int:
        """Calculate available quantity"""
        return self.current_quantity - self.reserved_quantity
=======
>>>>>>> performance-optimizations


class InventoryTransaction(Base):
    """Складская операция"""

    __tablename__ = "inventory_transactions"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
<<<<<<< HEAD
    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("items.id"), nullable=False
    )
    warehouse_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
=======
    item_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
    warehouse_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), nullable=False
>>>>>>> performance-optimizations
    )

    # Детали операции
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
<<<<<<< HEAD
=======
    total_cost: Mapped[Optional[float]] = mapped_column(
        Float, computed="quantity * unit_cost"
    )
>>>>>>> performance-optimizations

    # Ссылки на документы
    reference_number: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # Номер документа
    reference_type: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # Тип документа

    # Комментарии
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Связи
    item: Mapped["Item"] = relationship("Item", back_populates="transactions")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
<<<<<<< HEAD
    
    @property
    def total_cost(self) -> Optional[float]:
        """Calculate total cost"""
        if self.unit_cost is not None:
            return self.quantity * self.unit_cost
        return None
=======
>>>>>>> performance-optimizations


class Supplier(Base):
    """Поставщик"""

    __tablename__ = "suppliers"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Основная информация
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Контактная информация
    contact_person: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Адрес
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Бизнес информация
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    credit_limit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Статус
    status: Mapped[SupplierStatus] = mapped_column(
        Enum(SupplierStatus), default=SupplierStatus.ACTIVE
    )
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5

    # Связи
    supplier_items: Mapped[List["SupplierItem"]] = relationship(
        "SupplierItem", back_populates="supplier"
    )
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship(
        "PurchaseOrder", back_populates="supplier"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class SupplierItem(Base):
    """Товар поставщика"""

    __tablename__ = "supplier_items"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    supplier_id: Mapped[UUID] = mapped_column(
<<<<<<< HEAD
        PostgresUUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False
    )
    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("items.id"), nullable=False
    )
=======
        PostgresUUID(as_uuid=True), nullable=False
    )
    item_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
>>>>>>> performance-optimizations

    # Информация о товаре у поставщика
    supplier_sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    supplier_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Цены и условия
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    minimum_order_quantity: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Статус
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    supplier: Mapped["Supplier"] = relationship(
        "Supplier", back_populates="supplier_items"
    )
<<<<<<< HEAD
    # item: Mapped["Item"] = relationship("Item", back_populates="supplier_items")
=======
    item: Mapped["Item"] = relationship("Item", back_populates="supplier_items")
>>>>>>> performance-optimizations

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PurchaseOrder(Base):
    """Заказ на поставку"""

    __tablename__ = "purchase_orders"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    supplier_id: Mapped[UUID] = mapped_column(
<<<<<<< HEAD
        PostgresUUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False
=======
        PostgresUUID(as_uuid=True), nullable=False
>>>>>>> performance-optimizations
    )

    # Основная информация
    po_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Статус
    status: Mapped[str] = mapped_column(
        String(50), default="draft"
    )  # draft, sent, confirmed, received, cancelled

    # Даты
    expected_delivery_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    actual_delivery_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # Стоимость
    total_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Комментарии
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Связи
    supplier: Mapped["Supplier"] = relationship(
        "Supplier", back_populates="purchase_orders"
    )
    po_items: Mapped[List["PurchaseOrderItem"]] = relationship(
        "PurchaseOrderItem", back_populates="purchase_order"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PurchaseOrderItem(Base):
    """Элемент заказа на поставку"""

    __tablename__ = "purchase_order_items"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    purchase_order_id: Mapped[UUID] = mapped_column(
<<<<<<< HEAD
        PostgresUUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False
    )
    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("items.id"), nullable=False
    )
=======
        PostgresUUID(as_uuid=True), nullable=False
    )
    item_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
>>>>>>> performance-optimizations

    # Количество и цена
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
<<<<<<< HEAD

    # Статус получения
    received_quantity: Mapped[int] = mapped_column(Integer, default=0)
=======
    total_cost: Mapped[float] = mapped_column(Float, computed="quantity * unit_cost")

    # Статус получения
    received_quantity: Mapped[int] = mapped_column(Integer, default=0)
    is_fully_received: Mapped[bool] = mapped_column(
        Boolean, computed="received_quantity >= quantity"
    )
>>>>>>> performance-optimizations

    # Связи
    purchase_order: Mapped["PurchaseOrder"] = relationship(
        "PurchaseOrder", back_populates="po_items"
    )
    item: Mapped["Item"] = relationship("Item")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
<<<<<<< HEAD
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost"""
        return self.quantity * self.unit_cost
    
    @property
    def is_fully_received(self) -> bool:
        """Check if item is fully received"""
        return self.received_quantity >= self.quantity
=======
>>>>>>> performance-optimizations
