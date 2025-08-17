"""
CRUD операции для модуля inventory
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from routers.inventory.models import Item, Warehouse, InventoryLevel, InventoryTransaction
from routers.inventory.schemas import (
    ItemCreate, ItemUpdate, ItemSearchFilter,
    WarehouseCreate, WarehouseUpdate,
    InventoryLevelCreate, InventoryLevelUpdate, InventorySearchFilter,
    StockMovementRequest
)


# ===== Item CRUD =====

async def get_item_by_id(session: AsyncSession, item_id: UUID) -> Optional[Item]:
    """Получить товар по ID"""
    result = await session.execute(
        select(Item).where(Item.id == item_id)
    )
    return result.scalar_one_or_none()


async def get_item_by_sku(session: AsyncSession, sku: str) -> Optional[Item]:
    """Получить товар по SKU"""
    result = await session.execute(
        select(Item).where(Item.sku == sku)
    )
    return result.scalar_one_or_none()


async def create_item(session: AsyncSession, item_data: ItemCreate) -> Item:
    """Создать новый товар"""
    item = Item(**item_data.dict())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def update_item(session: AsyncSession, item_id: UUID, item_data: ItemUpdate) -> Optional[Item]:
    """Обновить товар"""
    item = await get_item_by_id(session, item_id)
    if not item:
        return None
    
    update_data = item_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await session.commit()
    await session.refresh(item)
    return item


async def delete_item(session: AsyncSession, item_id: UUID) -> bool:
    """Удалить товар (мягкое удаление - деактивация)"""
    item = await get_item_by_id(session, item_id)
    if not item:
        return False
    
    item.is_active = False
    await session.commit()
    return True


async def search_items(
    session: AsyncSession,
    filters: ItemSearchFilter,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """Поиск товаров с фильтрами"""
    query = select(Item)
    
    # Применяем фильтры
    conditions = []
    
    if filters.search:
        search_term = f"%{filters.search}%"
        conditions.append(
            or_(
                Item.name.ilike(search_term),
                Item.sku.ilike(search_term),
                Item.description.ilike(search_term)
            )
        )
    
    if filters.item_type:
        conditions.append(Item.item_type == filters.item_type)
    
    if filters.category:
        conditions.append(Item.category == filters.category)
    
    if filters.brand:
        conditions.append(Item.brand.ilike(f"%{filters.brand}%"))
    
    if filters.is_active is not None:
        conditions.append(Item.is_active == filters.is_active)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Подзапрос для товаров с низким остатком
    if filters.low_stock:
        # Получаем товары, где сумма остатков меньше min_stock_level
        low_stock_subquery = (
            select(InventoryLevel.item_id)
            .group_by(InventoryLevel.item_id)
            .having(func.sum(InventoryLevel.current_quantity) < Item.min_stock_level)
        )
        query = query.where(Item.id.in_(low_stock_subquery))
    
    # Подсчет общего количества
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    # Пагинация
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Выполняем запрос
    result = await session.execute(query)
    items = result.scalars().all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


# ===== Warehouse CRUD =====

async def get_warehouse_by_id(session: AsyncSession, warehouse_id: UUID) -> Optional[Warehouse]:
    """Получить склад по ID"""
    result = await session.execute(
        select(Warehouse).where(Warehouse.id == warehouse_id)
    )
    return result.scalar_one_or_none()


async def get_warehouse_by_code(session: AsyncSession, code: str) -> Optional[Warehouse]:
    """Получить склад по коду"""
    result = await session.execute(
        select(Warehouse).where(Warehouse.code == code)
    )
    return result.scalar_one_or_none()


async def create_warehouse(session: AsyncSession, warehouse_data: WarehouseCreate) -> Warehouse:
    """Создать новый склад"""
    warehouse = Warehouse(**warehouse_data.dict())
    session.add(warehouse)
    await session.commit()
    await session.refresh(warehouse)
    return warehouse


async def update_warehouse(session: AsyncSession, warehouse_id: UUID, warehouse_data: WarehouseUpdate) -> Optional[Warehouse]:
    """Обновить склад"""
    warehouse = await get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        return None
    
    update_data = warehouse_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(warehouse, field, value)
    
    await session.commit()
    await session.refresh(warehouse)
    return warehouse


async def get_all_warehouses(session: AsyncSession, active_only: bool = True) -> List[Warehouse]:
    """Получить все склады"""
    query = select(Warehouse)
    if active_only:
        query = query.where(Warehouse.is_active == True)
    
    result = await session.execute(query)
    return result.scalars().all()


# ===== Inventory Level CRUD =====

async def get_inventory_level(session: AsyncSession, item_id: UUID, warehouse_id: UUID) -> Optional[InventoryLevel]:
    """Получить уровень запасов товара на складе"""
    result = await session.execute(
        select(InventoryLevel)
        .where(
            and_(
                InventoryLevel.item_id == item_id,
                InventoryLevel.warehouse_id == warehouse_id
            )
        )
        .options(selectinload(InventoryLevel.item), selectinload(InventoryLevel.warehouse))
    )
    return result.scalar_one_or_none()


async def create_inventory_level(session: AsyncSession, level_data: InventoryLevelCreate) -> InventoryLevel:
    """Создать уровень запасов"""
    level = InventoryLevel(**level_data.dict())
    session.add(level)
    await session.commit()
    await session.refresh(level)
    return level


async def update_inventory_level(
    session: AsyncSession,
    item_id: UUID,
    warehouse_id: UUID,
    level_data: InventoryLevelUpdate
) -> Optional[InventoryLevel]:
    """Обновить уровень запасов"""
    level = await get_inventory_level(session, item_id, warehouse_id)
    if not level:
        return None
    
    update_data = level_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(level, field, value)
    
    await session.commit()
    await session.refresh(level)
    return level


async def search_inventory_levels(
    session: AsyncSession,
    filters: InventorySearchFilter,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """Поиск уровней запасов с фильтрами"""
    query = select(InventoryLevel).options(
        selectinload(InventoryLevel.item),
        selectinload(InventoryLevel.warehouse)
    )
    
    # Применяем фильтры
    conditions = []
    
    if filters.warehouse_id:
        conditions.append(InventoryLevel.warehouse_id == filters.warehouse_id)
    
    if filters.item_id:
        conditions.append(InventoryLevel.item_id == filters.item_id)
    
    if filters.min_quantity is not None:
        conditions.append(InventoryLevel.current_quantity >= filters.min_quantity)
    
    if filters.max_quantity is not None:
        conditions.append(InventoryLevel.current_quantity <= filters.max_quantity)
    
    if filters.zero_stock:
        conditions.append(InventoryLevel.current_quantity == 0)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Подсчет общего количества
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    # Пагинация
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Выполняем запрос
    result = await session.execute(query)
    levels = result.scalars().all()
    
    return {
        "levels": levels,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


# ===== Stock Movement Operations =====

async def move_stock(session: AsyncSession, movement_data: StockMovementRequest) -> InventoryLevel:
    """Движение товара на складе"""
    # Получаем или создаем уровень запасов
    level = await get_inventory_level(session, movement_data.item_id, movement_data.warehouse_id)
    
    if not level:
        # Создаем новый уровень запасов
        level_data = InventoryLevelCreate(
            item_id=movement_data.item_id,
            warehouse_id=movement_data.warehouse_id,
            current_quantity=max(0, movement_data.quantity)
        )
        level = await create_inventory_level(session, level_data)
    else:
        # Обновляем существующий
        new_quantity = level.current_quantity + movement_data.quantity
        if new_quantity < 0:
            raise ValueError(f"Недостаточно товара на складе. Доступно: {level.current_quantity}")
        
        level.current_quantity = new_quantity
        await session.commit()
        await session.refresh(level)
    
    # Создаем запись о движении
    transaction = InventoryTransaction(
        item_id=movement_data.item_id,
        warehouse_id=movement_data.warehouse_id,
        quantity=movement_data.quantity,
        transaction_type="in" if movement_data.quantity > 0 else "out",
        reason=movement_data.reason,
        reference_number=movement_data.reference_number
    )
    session.add(transaction)
    await session.commit()
    
    return level


async def reserve_stock(session: AsyncSession, item_id: UUID, warehouse_id: UUID, quantity: int) -> bool:
    """Резервирование товара"""
    level = await get_inventory_level(session, item_id, warehouse_id)
    if not level:
        return False
    
    available = level.current_quantity - level.reserved_quantity
    if available < quantity:
        return False
    
    level.reserved_quantity += quantity
    await session.commit()
    return True


async def release_reservation(session: AsyncSession, item_id: UUID, warehouse_id: UUID, quantity: int) -> bool:
    """Снятие резервирования товара"""
    level = await get_inventory_level(session, item_id, warehouse_id)
    if not level:
        return False
    
    if level.reserved_quantity < quantity:
        return False
    
    level.reserved_quantity -= quantity
    await session.commit()
    return True


# ===== Analytics =====

async def get_low_stock_items(session: AsyncSession, warehouse_id: Optional[UUID] = None) -> List[Dict]:
    """Получить товары с низким остатком"""
    query = (
        select(
            Item.id,
            Item.sku,
            Item.name,
            Item.min_stock_level,
            func.sum(InventoryLevel.current_quantity).label('total_quantity')
        )
        .join(InventoryLevel, Item.id == InventoryLevel.item_id)
        .where(Item.is_active == True)
    )
    
    if warehouse_id:
        query = query.where(InventoryLevel.warehouse_id == warehouse_id)
    
    query = query.group_by(
        Item.id, Item.sku, Item.name, Item.min_stock_level
    ).having(
        func.sum(InventoryLevel.current_quantity) < Item.min_stock_level
    )
    
    result = await session.execute(query)
    return [dict(row._mapping) for row in result]


async def get_inventory_summary(session: AsyncSession, warehouse_id: Optional[UUID] = None) -> Dict:
    """Сводка по запасам"""
    base_query = select(InventoryLevel)
    
    if warehouse_id:
        base_query = base_query.where(InventoryLevel.warehouse_id == warehouse_id)
    
    # Общее количество позиций
    total_items_result = await session.execute(
        select(func.count(func.distinct(InventoryLevel.item_id))).select_from(base_query.subquery())
    )
    total_items = total_items_result.scalar()
    
    # Общее количество товаров
    total_quantity_result = await session.execute(
        select(func.sum(InventoryLevel.current_quantity)).select_from(base_query.subquery())
    )
    total_quantity = total_quantity_result.scalar() or 0
    
    # Количество зарезервированных товаров
    reserved_quantity_result = await session.execute(
        select(func.sum(InventoryLevel.reserved_quantity)).select_from(base_query.subquery())
    )
    reserved_quantity = reserved_quantity_result.scalar() or 0
    
    # Количество позиций с нулевым остатком
    zero_stock_result = await session.execute(
        select(func.count()).select_from(
            base_query.where(InventoryLevel.current_quantity == 0).subquery()
        )
    )
    zero_stock_items = zero_stock_result.scalar()
    
    return {
        "total_items": total_items,
        "total_quantity": total_quantity,
        "reserved_quantity": reserved_quantity,
        "available_quantity": total_quantity - reserved_quantity,
        "zero_stock_items": zero_stock_items
    }
