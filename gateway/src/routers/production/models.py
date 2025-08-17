"""
Модели для управления производством клавиатур
"""

import uuid
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy import String, Boolean, Integer, Float, DateTime, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from database.core import Base
import enum


class OrderStatus(str, enum.Enum):
    """Статусы заказов"""

    DRAFT = "draft"  # Черновик
    CONFIRMED = "confirmed"  # Подтвержден
    IN_PRODUCTION = "in_production"  # В производстве
    QUALITY_CHECK = "quality_check"  # Проверка качества
    COMPLETED = "completed"  # Завершен
    CANCELLED = "cancelled"  # Отменен
    SHIPPED = "shipped"  # Отправлен


class ProductionStage(str, enum.Enum):
    """Этапы производства"""

    PLANNING = "planning"  # Планирование
    COMPONENT_PREP = "component_prep"  # Подготовка компонентов
    ASSEMBLY = "assembly"  # Сборка
    TESTING = "testing"  # Тестирование
    QUALITY_INSPECTION = "quality_inspection"  # Проверка качества
    PACKAGING = "packaging"  # Упаковка
    READY = "ready"  # Готов к отправке


class QualityStatus(str, enum.Enum):
    """Статусы качества"""

    PENDING = "pending"  # Ожидает проверки
    PASSED = "passed"  # Прошел проверку
    FAILED = "failed"  # Не прошел проверку
    REWORK = "rework"  # Требует доработки


class ResourceType(str, enum.Enum):
    """Типы ресурсов"""

    HUMAN = "human"  # Человеческие ресурсы
    EQUIPMENT = "equipment"  # Оборудование
    MATERIAL = "material"  # Материалы
    TIME = "time"  # Время


class Order(Base):
    """Заказ на производство"""

    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(50), nullable=False)

    # Детали заказа
    keyboard_model: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    # Статусы и даты
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.DRAFT
    )
    current_stage: Mapped[ProductionStage] = mapped_column(
        Enum(ProductionStage), default=ProductionStage.PLANNING
    )

    # Даты
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    planned_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    planned_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    actual_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    actual_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # Приоритет и описание
    priority: Mapped[int] = mapped_column(Integer, default=1)  # 1-5, где 5 - высший
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    special_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Связи
    production_tasks: Mapped[List["ProductionTask"]] = relationship(
        "ProductionTask", back_populates="order"
    )
    quality_checks: Mapped[List["QualityCheck"]] = relationship(
        "QualityCheck", back_populates="order"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ProductionTask(Base):
    """Задача производства"""

    __tablename__ = "production_tasks"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)

    # Детали задачи
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stage: Mapped[ProductionStage] = mapped_column(
        Enum(ProductionStage), nullable=False
    )

    # Временные рамки
    planned_duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    actual_duration_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    planned_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    planned_end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    actual_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    actual_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Статус и прогресс
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)  # 0-100

    # Связи
    order: Mapped["Order"] = relationship("Order", back_populates="production_tasks")
    assigned_resources: Mapped[List["TaskResource"]] = relationship(
        "TaskResource", back_populates="task"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class QualityCheck(Base):
    """Проверка качества"""

    __tablename__ = "quality_checks"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)

    # Детали проверки
    check_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    checklist_items: Mapped[List["QualityChecklistItem"]] = relationship(
        "QualityChecklistItem", back_populates="quality_check"
    )

    # Статус и результаты
    status: Mapped[QualityStatus] = mapped_column(
        Enum(QualityStatus), default=QualityStatus.PENDING
    )
    inspector_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    inspection_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Комментарии
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rework_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Связи
    order: Mapped["Order"] = relationship("Order", back_populates="quality_checks")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class QualityChecklistItem(Base):
    """Элемент чек-листа качества"""

    __tablename__ = "quality_checklist_items"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quality_check_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), nullable=False
    )

    # Детали элемента
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)

    # Результат проверки
    is_passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Связи
    quality_check: Mapped["QualityCheck"] = relationship(
        "QualityCheck", back_populates="checklist_items"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Resource(Base):
    """Ресурс производства"""

    __tablename__ = "resources"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Детали ресурса
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    resource_type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Характеристики
    capacity: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # Производительность/мощность
    unit: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # Единица измерения
    cost_per_hour: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # Стоимость в час

    # Статус
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    task_assignments: Mapped[List["TaskResource"]] = relationship(
        "TaskResource", back_populates="resource"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class TaskResource(Base):
    """Связь задачи с ресурсом"""

    __tablename__ = "task_resources"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
    resource_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), nullable=False
    )

    # Детали назначения
    assigned_hours: Mapped[float] = mapped_column(Float, nullable=False)
    actual_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Даты назначения
    assigned_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Связи
    task: Mapped["ProductionTask"] = relationship(
        "ProductionTask", back_populates="assigned_resources"
    )
    resource: Mapped["Resource"] = relationship(
        "Resource", back_populates="task_assignments"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
