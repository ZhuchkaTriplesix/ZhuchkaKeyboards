"""
Pydantic схемы для управления производством
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr
from pydantic_config import default_config

from .models import OrderStatus, ProductionStage, QualityStatus, ResourceType


# ==================== ЗАКАЗЫ ====================

class OrderBase(BaseModel):
    """Базовая схема заказа"""
    customer_name: str = Field(..., min_length=1, max_length=200, description="Имя заказчика")
    customer_email: EmailStr = Field(..., description="Email заказчика")
    customer_phone: str = Field(..., min_length=1, max_length=50, description="Телефон заказчика")
    keyboard_model: str = Field(..., min_length=1, max_length=100, description="Модель клавиатуры")
    quantity: int = Field(..., gt=0, description="Количество")
    unit_price: float = Field(..., gt=0, description="Цена за единицу")
    priority: int = Field(1, ge=1, le=5, description="Приоритет (1-5)")
    description: Optional[str] = Field(None, max_length=1000, description="Описание заказа")
    special_requirements: Optional[str] = Field(None, max_length=1000, description="Особые требования")
    planned_start_date: Optional[datetime] = Field(None, description="Планируемая дата начала")
    planned_completion_date: Optional[datetime] = Field(None, description="Планируемая дата завершения")

    model_config = default_config


class OrderCreate(OrderBase):
    """Схема создания заказа"""
    pass


class OrderUpdate(BaseModel):
    """Схема обновления заказа"""
    customer_name: Optional[str] = Field(None, min_length=1, max_length=200)
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = Field(None, min_length=1, max_length=50)
    keyboard_model: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, gt=0)
    priority: Optional[int] = Field(None, ge=1, le=5)
    description: Optional[str] = Field(None, max_length=1000)
    special_requirements: Optional[str] = Field(None, max_length=1000)
    planned_start_date: Optional[datetime] = None
    planned_completion_date: Optional[datetime] = None
    status: Optional[OrderStatus] = None
    current_stage: Optional[ProductionStage] = None

    model_config = default_config


class OrderResponse(OrderBase):
    """Схема ответа заказа"""
    id: UUID
    order_number: str
    status: OrderStatus
    current_stage: ProductionStage
    total_price: float
    order_date: datetime
    actual_start_date: Optional[datetime]
    actual_completion_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = default_config


class OrderListResponse(BaseModel):
    """Схема списка заказов"""
    orders: List[OrderResponse]
    total: int
    page: int
    size: int

    model_config = default_config


# ==================== ЗАДАЧИ ПРОИЗВОДСТВА ====================

class ProductionTaskBase(BaseModel):
    """Базовая схема задачи производства"""
    name: str = Field(..., min_length=1, max_length=200, description="Название задачи")
    description: Optional[str] = Field(None, max_length=1000, description="Описание задачи")
    stage: ProductionStage = Field(..., description="Этап производства")
    planned_duration_hours: float = Field(..., gt=0, description="Планируемая продолжительность в часах")
    planned_start_date: Optional[datetime] = Field(None, description="Планируемая дата начала")
    planned_end_date: Optional[datetime] = Field(None, description="Планируемая дата завершения")

    model_config = default_config


class ProductionTaskCreate(ProductionTaskBase):
    """Схема создания задачи производства"""
    order_id: UUID = Field(..., description="ID заказа")


class ProductionTaskUpdate(BaseModel):
    """Схема обновления задачи производства"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    stage: Optional[ProductionStage] = None
    planned_duration_hours: Optional[float] = Field(None, gt=0)
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_duration_hours: Optional[float] = Field(None, gt=0)
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)

    model_config = default_config


class ProductionTaskResponse(ProductionTaskBase):
    """Схема ответа задачи производства"""
    id: UUID
    order_id: UUID
    actual_duration_hours: Optional[float]
    actual_start_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    is_completed: bool
    progress_percentage: int
    created_at: datetime
    updated_at: datetime

    model_config = default_config


# ==================== ПРОВЕРКА КАЧЕСТВА ====================

class QualityChecklistItemBase(BaseModel):
    """Базовая схема элемента чек-листа качества"""
    item_name: str = Field(..., min_length=1, max_length=200, description="Название элемента")
    description: Optional[str] = Field(None, max_length=1000, description="Описание элемента")
    is_required: bool = Field(True, description="Обязательный элемент")

    model_config = default_config


class QualityChecklistItemCreate(QualityChecklistItemBase):
    """Схема создания элемента чек-листа качества"""
    pass


class QualityChecklistItemUpdate(BaseModel):
    """Схема обновления элемента чек-листа качества"""
    item_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_required: Optional[bool] = None
    is_passed: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)

    model_config = default_config


class QualityChecklistItemResponse(QualityChecklistItemBase):
    """Схема ответа элемента чек-листа качества"""
    id: UUID
    is_passed: Optional[bool]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = default_config


class QualityCheckBase(BaseModel):
    """Базовая схема проверки качества"""
    check_name: str = Field(..., min_length=1, max_length=200, description="Название проверки")
    description: Optional[str] = Field(None, max_length=1000, description="Описание проверки")
    checklist_items: List[QualityChecklistItemCreate] = Field(..., description="Элементы чек-листа")

    model_config = default_config


class QualityCheckCreate(QualityCheckBase):
    """Схема создания проверки качества"""
    order_id: UUID = Field(..., description="ID заказа")


class QualityCheckUpdate(BaseModel):
    """Схема обновления проверки качества"""
    check_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[QualityStatus] = None
    inspector_name: Optional[str] = Field(None, max_length=100)
    inspection_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)
    rework_instructions: Optional[str] = Field(None, max_length=1000)

    model_config = default_config


class QualityCheckResponse(QualityCheckBase):
    """Схема ответа проверки качества"""
    id: UUID
    order_id: UUID
    status: QualityStatus
    inspector_name: Optional[str]
    inspection_date: Optional[datetime]
    notes: Optional[str]
    rework_instructions: Optional[str]
    checklist_items: List[QualityChecklistItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = default_config


# ==================== РЕСУРСЫ ====================

class ResourceBase(BaseModel):
    """Базовая схема ресурса"""
    name: str = Field(..., min_length=1, max_length=200, description="Название ресурса")
    resource_type: ResourceType = Field(..., description="Тип ресурса")
    description: Optional[str] = Field(None, max_length=1000, description="Описание ресурса")
    capacity: Optional[float] = Field(None, gt=0, description="Производительность/мощность")
    unit: Optional[str] = Field(None, max_length=50, description="Единица измерения")
    cost_per_hour: Optional[float] = Field(None, gt=0, description="Стоимость в час")

    model_config = default_config


class ResourceCreate(ResourceBase):
    """Схема создания ресурса"""
    pass


class ResourceUpdate(BaseModel):
    """Схема обновления ресурса"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    resource_type: Optional[ResourceType] = None
    description: Optional[str] = Field(None, max_length=1000)
    capacity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    cost_per_hour: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None

    model_config = default_config


class ResourceResponse(ResourceBase):
    """Схема ответа ресурса"""
    id: UUID
    is_available: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = default_config


# ==================== НАЗНАЧЕНИЕ РЕСУРСОВ ====================

class TaskResourceBase(BaseModel):
    """Базовая схема назначения ресурса на задачу"""
    assigned_hours: float = Field(..., gt=0, description="Назначенные часы")
    start_time: Optional[datetime] = Field(None, description="Время начала")
    end_time: Optional[datetime] = Field(None, description="Время завершения")

    model_config = default_config


class TaskResourceCreate(TaskResourceBase):
    """Схема создания назначения ресурса"""
    task_id: UUID = Field(..., description="ID задачи")
    resource_id: UUID = Field(..., description="ID ресурса")


class TaskResourceUpdate(BaseModel):
    """Схема обновления назначения ресурса"""
    assigned_hours: Optional[float] = Field(None, gt=0)
    actual_hours: Optional[float] = Field(None, gt=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    model_config = default_config


class TaskResourceResponse(TaskResourceBase):
    """Схема ответа назначения ресурса"""
    id: UUID
    task_id: UUID
    resource_id: UUID
    actual_hours: Optional[float]
    assigned_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = default_config


# ==================== СТАТИСТИКА ====================

class ProductionStats(BaseModel):
    """Статистика производства"""
    total_orders: int
    orders_in_production: int
    orders_completed: int
    orders_delayed: int
    average_completion_time_days: float
    quality_pass_rate: float
    resource_utilization: float

    model_config = default_config


class OrderTimeline(BaseModel):
    """Временная линия заказа"""
    order_id: UUID
    order_number: str
    customer_name: str
    stages: List[dict]  # Список этапов с датами
    total_duration_days: float
    is_on_schedule: bool

    model_config = default_config
