"""
Бизнес-логика для управления производством клавиатур
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from .models import (
    Order,
    ProductionTask,
    QualityCheck,
    QualityChecklistItem,
    Resource,
    TaskResource,
    OrderStatus,
    ProductionStage,
    QualityStatus,
)
from .schemas import (
    OrderCreate,
    OrderUpdate,
    ProductionTaskCreate,
    ProductionTaskUpdate,
    QualityCheckCreate,
    QualityCheckUpdate,
    ResourceCreate,
    ResourceUpdate,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class ProductionService:
    """Сервис управления производством"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== ЗАКАЗЫ ====================

    async def create_order(self, order_data: OrderCreate) -> Order:
        """Создает новый заказ на производство"""
        try:
            # Генерируем номер заказа
            order_number = await self._generate_order_number()

            # Рассчитываем общую стоимость
            total_price = order_data.quantity * order_data.unit_price

            # Создаем заказ
            order = Order(
                order_number=order_number,
                customer_name=order_data.customer_name,
                customer_email=order_data.customer_email,
                customer_phone=order_data.customer_phone,
                keyboard_model=order_data.keyboard_model,
                quantity=order_data.quantity,
                unit_price=order_data.unit_price,
                total_price=total_price,
                priority=order_data.priority,
                description=order_data.description,
                special_requirements=order_data.special_requirements,
                planned_start_date=order_data.planned_start_date,
                planned_completion_date=order_data.planned_completion_date,
            )

            self.db.add(order)
            await self.db.commit()
            await self.db.refresh(order)

            logger.info(
                f"Created order {order_number} for customer {order_data.customer_name}"
            )
            return order

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating order: {e}")
            raise

    async def get_order(self, order_id: uuid.UUID) -> Optional[Order]:
        """Получает заказ по ID"""
        try:
            result = await self.db.execute(
                select(Order)
                .options(
                    selectinload(Order.production_tasks),
                    selectinload(Order.quality_checks),
                )
                .where(Order.id == order_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            return None

    async def get_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[OrderStatus] = None,
        priority: Optional[int] = None,
    ) -> List[Order]:
        """Получает список заказов с фильтрацией"""
        try:
            query = select(Order)

            if status:
                query = query.where(Order.status == status)
            if priority:
                query = query.where(Order.priority == priority)

            query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []

    async def update_order(
        self, order_id: uuid.UUID, order_data: OrderUpdate
    ) -> Optional[Order]:
        """Обновляет заказ"""
        try:
            order = await self.get_order(order_id)
            if not order:
                return None

            # Обновляем поля
            update_data = order_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(order, field, value)

            # Пересчитываем общую стоимость если изменилось количество или цена
            if "quantity" in update_data or "unit_price" in update_data:
                order.total_price = order.quantity * order.unit_price

            order.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(order)

            logger.info(f"Updated order {order.order_number}")
            return order

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating order {order_id}: {e}")
            return None

    async def change_order_status(
        self, order_id: uuid.UUID, new_status: OrderStatus
    ) -> bool:
        """Изменяет статус заказа"""
        try:
            order = await self.get_order(order_id)
            if not order:
                return False

            old_status = order.status
            order.status = new_status

            # Обновляем даты в зависимости от статуса
            if new_status == OrderStatus.IN_PRODUCTION and not order.actual_start_date:
                order.actual_start_date = datetime.utcnow()
            elif (
                new_status == OrderStatus.COMPLETED and not order.actual_completion_date
            ):
                order.actual_completion_date = datetime.utcnow()

            order.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(
                f"Changed order {order.order_number} status from {old_status} to {new_status}"
            )
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error changing order status {order_id}: {e}")
            return False

    # ==================== ЗАДАЧИ ПРОИЗВОДСТВА ====================

    async def create_production_task(
        self, task_data: ProductionTaskCreate
    ) -> ProductionTask:
        """Создает задачу производства"""
        try:
            task = ProductionTask(
                order_id=task_data.order_id,
                name=task_data.name,
                description=task_data.description,
                stage=task_data.stage,
                planned_duration_hours=task_data.planned_duration_hours,
                planned_start_date=task_data.planned_start_date,
                planned_end_date=task_data.planned_end_date,
            )

            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)

            logger.info(
                f"Created production task '{task.name}' for order {task.order_id}"
            )
            return task

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating production task: {e}")
            raise

    async def update_task_progress(
        self,
        task_id: uuid.UUID,
        progress_percentage: int,
        actual_hours: Optional[float] = None,
    ) -> bool:
        """Обновляет прогресс задачи"""
        try:
            result = await self.db.execute(
                select(ProductionTask).where(ProductionTask.id == task_id)
            )
            task = result.scalar_one_or_none()

            if not task:
                return False

            task.progress_percentage = progress_percentage

            if actual_hours:
                task.actual_duration_hours = actual_hours

            # Проверяем завершение задачи
            if progress_percentage >= 100:
                task.is_completed = True
                task.actual_end_date = datetime.utcnow()

            task.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Updated task {task_id} progress to {progress_percentage}%")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating task progress {task_id}: {e}")
            return False

    # ==================== ПРОВЕРКА КАЧЕСТВА ====================

    async def create_quality_check(
        self, check_data: QualityCheckCreate
    ) -> QualityCheck:
        """Создает проверку качества"""
        try:
            # Создаем основную проверку
            quality_check = QualityCheck(
                order_id=check_data.order_id,
                check_name=check_data.check_name,
                description=check_data.description,
            )

            self.db.add(quality_check)
            await self.db.flush()  # Получаем ID для создания элементов чек-листа

            # Создаем элементы чек-листа
            for item_data in check_data.checklist_items:
                checklist_item = QualityChecklistItem(
                    quality_check_id=quality_check.id,
                    item_name=item_data.item_name,
                    description=item_data.description,
                    is_required=item_data.is_required,
                )
                self.db.add(checklist_item)

            await self.db.commit()
            await self.db.refresh(quality_check)

            logger.info(
                f"Created quality check '{check_data.check_name}' for order {check_data.order_id}"
            )
            return quality_check

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating quality check: {e}")
            raise

    async def update_quality_check_status(
        self,
        check_id: uuid.UUID,
        status: QualityStatus,
        inspector_name: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """Обновляет статус проверки качества"""
        try:
            result = await self.db.execute(
                select(QualityCheck).where(QualityCheck.id == check_id)
            )
            check = result.scalar_one_or_none()

            if not check:
                return False

            check.status = status
            if inspector_name:
                check.inspector_name = inspector_name
            if notes:
                check.notes = notes

            if status in [
                QualityStatus.PASSED,
                QualityStatus.FAILED,
                QualityStatus.REWORK,
            ]:
                check.inspection_date = datetime.utcnow()

            check.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Updated quality check {check_id} status to {status}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating quality check status {check_id}: {e}")
            return False

    # ==================== РЕСУРСЫ ====================

    async def create_resource(self, resource_data: ResourceCreate) -> Resource:
        """Создает ресурс производства"""
        try:
            resource = Resource(**resource_data.model_dump())

            self.db.add(resource)
            await self.db.commit()
            await self.db.refresh(resource)

            logger.info(
                f"Created resource '{resource.name}' of type {resource.resource_type}"
            )
            return resource

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating resource: {e}")
            raise

    async def assign_resource_to_task(
        self, task_id: uuid.UUID, resource_id: uuid.UUID, assigned_hours: float
    ) -> bool:
        """Назначает ресурс на задачу"""
        try:
            # Проверяем доступность ресурса
            result = await self.db.execute(
                select(Resource).where(Resource.id == resource_id)
            )
            resource = result.scalar_one_or_none()

            if not resource or not resource.is_available:
                return False

            # Создаем назначение
            task_resource = TaskResource(
                task_id=task_id, resource_id=resource_id, assigned_hours=assigned_hours
            )

            self.db.add(task_resource)
            await self.db.commit()

            logger.info(
                f"Assigned resource {resource.name} to task {task_id} for {assigned_hours} hours"
            )
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error assigning resource to task: {e}")
            return False

    # ==================== СТАТИСТИКА И АНАЛИТИКА ====================

    async def get_production_stats(self) -> Dict[str, Any]:
        """Получает статистику производства"""
        try:
            # Общее количество заказов
            total_orders_result = await self.db.execute(select(func.count(Order.id)))
            total_orders = total_orders_result.scalar()

            # Заказы в производстве
            in_production_result = await self.db.execute(
                select(func.count(Order.id)).where(
                    Order.status == OrderStatus.IN_PRODUCTION
                )
            )
            orders_in_production = in_production_result.scalar()

            # Завершенные заказы
            completed_result = await self.db.execute(
                select(func.count(Order.id)).where(
                    Order.status == OrderStatus.COMPLETED
                )
            )
            orders_completed = completed_result.scalar()

            # Задержанные заказы
            delayed_result = await self.db.execute(
                select(Order).where(
                    and_(
                        Order.planned_completion_date < datetime.utcnow(),
                        Order.status.in_(
                            [OrderStatus.IN_PRODUCTION, OrderStatus.QUALITY_CHECK]
                        ),
                    )
                )
            )
            orders_delayed = len(delayed_result.scalars().all())

            # Среднее время выполнения
            avg_time_result = await self.db.execute(
                select(
                    func.avg(
                        func.extract(
                            "epoch",
                            Order.actual_completion_date - Order.actual_start_date,
                        )
                        / 86400
                    )
                ).where(Order.actual_completion_date.isnot(None))
            )
            avg_completion_time = avg_time_result.scalar() or 0

            # Процент прохождения качества
            quality_stats_result = await self.db.execute(
                select(
                    func.count(QualityCheck.id),
                    func.count(QualityCheck.id).filter(
                        QualityCheck.status == QualityStatus.PASSED
                    ),
                )
            )
            quality_stats = quality_stats_result.first()
            total_checks = quality_stats[0] or 0
            passed_checks = quality_stats[1] or 0
            quality_pass_rate = (
                (passed_checks / total_checks * 100) if total_checks > 0 else 0
            )

            return {
                "total_orders": total_orders,
                "orders_in_production": orders_in_production,
                "orders_completed": orders_completed,
                "orders_delayed": orders_delayed,
                "average_completion_time_days": round(avg_completion_time, 1),
                "quality_pass_rate": round(quality_pass_rate, 1),
            }

        except Exception as e:
            logger.error(f"Error getting production stats: {e}")
            return {}

    async def get_order_timeline(self, order_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Получает временную линию заказа"""
        try:
            order = await self.get_order(order_id)
            if not order:
                return None

            # Получаем задачи с их временными рамками
            tasks_result = await self.db.execute(
                select(ProductionTask).where(ProductionTask.order_id == order_id)
            )
            tasks = tasks_result.scalars().all()

            stages = []
            for task in tasks:
                stages.append(
                    {
                        "stage": task.stage.value,
                        "name": task.name,
                        "planned_start": task.planned_start_date,
                        "planned_end": task.planned_end_date,
                        "actual_start": task.actual_start_date,
                        "actual_end": task.actual_end_date,
                        "progress": task.progress_percentage,
                        "is_completed": task.is_completed,
                    }
                )

            # Рассчитываем общую продолжительность
            total_duration = 0
            if order.actual_start_date and order.actual_completion_date:
                total_duration = (
                    order.actual_completion_date - order.actual_start_date
                ).days
            elif order.planned_start_date and order.planned_completion_date:
                total_duration = (
                    order.planned_completion_date - order.planned_start_date
                ).days

            # Проверяем соответствие графику
            is_on_schedule = True
            if order.planned_completion_date and order.actual_completion_date:
                is_on_schedule = (
                    order.actual_completion_date <= order.planned_completion_date
                )

            return {
                "order_id": str(order.id),
                "order_number": order.order_number,
                "customer_name": order.customer_name,
                "stages": stages,
                "total_duration_days": total_duration,
                "is_on_schedule": is_on_schedule,
            }

        except Exception as e:
            logger.error(f"Error getting order timeline {order_id}: {e}")
            return None

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    async def _generate_order_number(self) -> str:
        """Генерирует уникальный номер заказа"""
        try:
            # Получаем последний номер заказа
            result = await self.db.execute(
                select(Order.order_number).order_by(Order.order_number.desc()).limit(1)
            )
            last_number = result.scalar_one_or_none()

            if last_number:
                # Извлекаем номер и увеличиваем на 1
                try:
                    last_num = int(last_number.split("-")[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1

            # Форматируем номер: ORD-YYYY-XXXX
            year = datetime.utcnow().year
            return f"ORD-{year}-{new_num:04d}"

        except Exception as e:
            logger.error(f"Error generating order number: {e}")
            # Fallback номер
            return f"ORD-{datetime.utcnow().year}-{uuid.uuid4().hex[:4].upper()}"
