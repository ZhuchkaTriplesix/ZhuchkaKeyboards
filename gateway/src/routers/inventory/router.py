"""
REST API роутер для модуля inventory
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import ORJSONResponse
import uuid
from datetime import datetime

from database.dependencies import DbSession
from utils.responses import api_responses
from routers.inventory import crud
from routers.inventory.schemas import (
    # Item schemas
    ItemCreate, ItemUpdate, ItemResponse, ItemListResponse, ItemSearchFilter,
    # Warehouse schemas
    WarehouseCreate, WarehouseUpdate, WarehouseResponse, WarehouseListResponse,
    # Inventory schemas
    InventoryLevelCreate, InventoryLevelResponse, 
    InventoryLevelListResponse, InventorySearchFilter,
    # Movement schemas
    StockMovementRequest
)

router = APIRouter()


@router.post("/debug/warehouse")
async def debug_create_warehouse(session: DbSession):
    """Debug endpoint to test warehouse creation"""
    from routers.inventory.schemas import WarehouseCreate
    
    warehouse_data = WarehouseCreate(
        name="Debug Test Warehouse",
        code=f"DEBUG-{uuid.uuid4().hex[:8].upper()}",
        address="Debug St 1",
        city="Debug City", 
        country="Debug Country"
    )
    
    try:
        warehouse = await crud.create_warehouse(session, warehouse_data)
        # Manual serialization to see what happens
        manual_data = {
            "id": str(warehouse.id),
            "name": warehouse.name,
            "code": warehouse.code,
            "address": warehouse.address,
            "city": warehouse.city,
            "country": warehouse.country,
            "created_at": warehouse.created_at.isoformat(),
            "updated_at": warehouse.updated_at.isoformat()
        }
        return {"status": "success", "warehouse": manual_data}
    except Exception as e:
        return {"status": "error", "error": str(e), "type": str(type(e))}


def serialize_model(model_instance, response_model):
    """Serialize model with custom UUID and datetime handling"""
    if hasattr(model_instance, '__dict__'):
        data = {}
        for key, value in model_instance.__dict__.items():
            if key.startswith('_'):
                continue
            if hasattr(value, 'hex'):  # UUID
                data[key] = str(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
            else:
                data[key] = value
        
        # Add computed properties
        if hasattr(model_instance, 'available_quantity'):
            data['available_quantity'] = model_instance.available_quantity
            
        return data
    return model_instance


def serialize_models_list(models_list, response_model):
    """Serialize list of models"""
    return [serialize_model(model, response_model) for model in models_list]


# ===== Item Endpoints =====

@router.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    responses=api_responses(ItemResponse),
    summary="Создать товар",
    description="Создает новый товар в системе. SKU должен быть уникальным."
)
async def create_item(
    item_data: ItemCreate,
    session: DbSession
):
    """Создать новый товар"""
    # Проверяем уникальность SKU
    existing_item = await crud.get_item_by_sku(session, item_data.sku)
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Товар с SKU '{item_data.sku}' уже существует"
        )
    
    try:
        item = await crud.create_item(session, item_data)
        return ORJSONResponse(
            content=serialize_model(item, ItemResponse),
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания товара: {str(e)}"
        )


@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    responses=api_responses(ItemResponse),
    summary="Получить товар по ID",
    description="Возвращает информацию о товаре по его ID."
)
async def get_item(
    item_id: UUID,
    session: DbSession
):
    """Получить товар по ID"""
    item = await crud.get_item_by_id(session, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    return ORJSONResponse(content=serialize_model(item, ItemResponse))


@router.put(
    "/items/{item_id}",
    response_model=ItemResponse,
    responses=api_responses(ItemResponse),
    summary="Обновить товар",
    description="Обновляет информацию о товаре."
)
async def update_item(
    item_id: UUID,
    item_data: ItemUpdate,
    session: DbSession
):
    """Обновить товар"""
    item = await crud.update_item(session, item_id, item_data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    return ORJSONResponse(content=serialize_model(item, ItemResponse))


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить товар",
    description="Деактивирует товар (мягкое удаление)."
)
async def delete_item(
    item_id: UUID,
    session: DbSession
):
    """Удалить товар (деактивировать)"""
    success = await crud.delete_item(session, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )


@router.get(
    "/items",
    response_model=ItemListResponse,
    responses=api_responses(ItemListResponse),
    summary="Поиск товаров",
    description="Поиск товаров с фильтрами и пагинацией."
)
async def search_items(
    session: DbSession,
    search: Optional[str] = Query(None, description="Поиск по названию, SKU, описанию"),
    item_type: Optional[str] = Query(None, description="Тип товара"),
    category: Optional[str] = Query(None, description="Категория товара"),
    brand: Optional[str] = Query(None, description="Бренд"),
    is_active: Optional[bool] = Query(None, description="Активен ли товар"),
    low_stock: Optional[bool] = Query(None, description="Товары с низким остатком"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы")
):
    """Поиск товаров с фильтрами"""
    filters = ItemSearchFilter(
        search=search,
        item_type=item_type,
        category=category,
        brand=brand,
        is_active=is_active,
        low_stock=low_stock
    )
    
    result = await crud.search_items(session, filters, page, size)
    
    response_data = {
        "items": serialize_models_list(result["items"], ItemResponse),
        "total": result["total"],
        "page": result["page"],
        "size": result["size"],
        "pages": result["pages"]
    }
    
    return ORJSONResponse(content=response_data)


# ===== Warehouse Endpoints =====

@router.post(
    "/warehouses",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED,
    responses=api_responses(WarehouseResponse),
    summary="Создать склад",
    description="Создает новый склад. Код склада должен быть уникальным."
)
async def create_warehouse(
    warehouse_data: WarehouseCreate,
    session: DbSession
):
    """Создать новый склад"""
    # Проверяем уникальность кода
    existing_warehouse = await crud.get_warehouse_by_code(session, warehouse_data.code)
    if existing_warehouse:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Склад с кодом '{warehouse_data.code}' уже существует"
        )
    
    try:
        warehouse = await crud.create_warehouse(session, warehouse_data)
        response_data = serialize_model(warehouse, WarehouseResponse)
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания склада: {str(e)}"
        )


@router.get(
    "/warehouses/{warehouse_id}",
    response_model=WarehouseResponse,
    responses=api_responses(WarehouseResponse),
    summary="Получить склад по ID",
    description="Возвращает информацию о складе по его ID."
)
async def get_warehouse(
    warehouse_id: UUID,
    session: DbSession
):
    """Получить склад по ID"""
    warehouse = await crud.get_warehouse_by_id(session, warehouse_id)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Склад не найден"
        )
    
    return ORJSONResponse(content=serialize_model(warehouse, WarehouseResponse))


@router.get(
    "/warehouses",
    response_model=WarehouseListResponse,
    responses=api_responses(WarehouseListResponse),
    summary="Получить все склады",
    description="Возвращает список всех складов."
)
async def get_warehouses(
    session: DbSession,
    active_only: bool = Query(True, description="Только активные склады")
):
    """Получить все склады"""
    warehouses = await crud.get_all_warehouses(session, active_only)
    
    response_data = {
        "warehouses": serialize_models_list(warehouses, WarehouseResponse),
        "total": len(warehouses),
        "page": 1,
        "size": len(warehouses),
        "pages": 1
    }
    
    return ORJSONResponse(content=response_data)


@router.put(
    "/warehouses/{warehouse_id}",
    response_model=WarehouseResponse,
    responses=api_responses(WarehouseResponse),
    summary="Обновить склад",
    description="Обновляет информацию о складе."
)
async def update_warehouse(
    warehouse_id: UUID,
    warehouse_data: WarehouseUpdate,
    session: DbSession
):
    """Обновить склад"""
    warehouse = await crud.update_warehouse(session, warehouse_id, warehouse_data)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Склад не найден"
        )
    
    return ORJSONResponse(content=serialize_model(warehouse, WarehouseResponse))


# ===== Inventory Level Endpoints =====

@router.get(
    "/inventory/{item_id}/{warehouse_id}",
    response_model=InventoryLevelResponse,
    responses=api_responses(InventoryLevelResponse),
    summary="Получить уровень запасов",
    description="Возвращает уровень запасов товара на складе."
)
async def get_inventory_level(
    item_id: UUID,
    warehouse_id: UUID,
    session: DbSession
):
    """Получить уровень запасов товара на складе"""
    level = await crud.get_inventory_level(session, item_id, warehouse_id)
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уровень запасов не найден"
        )
    
    response_data = serialize_model(level, InventoryLevelResponse)
    return ORJSONResponse(content=response_data)


@router.post(
    "/inventory",
    response_model=InventoryLevelResponse,
    status_code=status.HTTP_201_CREATED,
    responses=api_responses(InventoryLevelResponse),
    summary="Создать уровень запасов",
    description="Создает новый уровень запасов товара на складе."
)
async def create_inventory_level(
    level_data: InventoryLevelCreate,
    session: DbSession
):
    """Создать уровень запасов"""
    # Проверяем, что такого уровня еще нет
    existing_level = await crud.get_inventory_level(
        session, level_data.item_id, level_data.warehouse_id
    )
    if existing_level:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Уровень запасов для этого товара на данном складе уже существует"
        )
    
    try:
        level = await crud.create_inventory_level(session, level_data)
        return ORJSONResponse(
            content=InventoryLevelResponse.from_orm(level).dict(),
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания уровня запасов: {str(e)}"
        )


@router.get(
    "/inventory",
    response_model=InventoryLevelListResponse,
    responses=api_responses(InventoryLevelListResponse),
    summary="Поиск уровней запасов",
    description="Поиск уровней запасов с фильтрами и пагинацией."
)
async def search_inventory_levels(
    session: DbSession,
    warehouse_id: Optional[UUID] = Query(None, description="ID склада"),
    item_id: Optional[UUID] = Query(None, description="ID товара"),
    min_quantity: Optional[int] = Query(None, description="Минимальное количество"),
    max_quantity: Optional[int] = Query(None, description="Максимальное количество"),
    zero_stock: Optional[bool] = Query(None, description="Только нулевые остатки"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы")
):
    """Поиск уровней запасов с фильтрами"""
    filters = InventorySearchFilter(
        warehouse_id=warehouse_id,
        item_id=item_id,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        zero_stock=zero_stock
    )
    
    result = await crud.search_inventory_levels(session, filters, page, size)
    
    response_data = InventoryLevelListResponse(
        levels=[InventoryLevelResponse.from_orm(level) for level in result["levels"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )
    
    return ORJSONResponse(content=response_data.dict())


# ===== Stock Movement Endpoints =====

@router.post(
    "/inventory/move",
    response_model=InventoryLevelResponse,
    responses=api_responses(InventoryLevelResponse),
    summary="Движение товара",
    description="Приход/расход товара на складе. Положительное число - приход, отрицательное - расход."
)
async def move_stock(
    movement_data: StockMovementRequest,
    session: DbSession
):
    """Движение товара на складе"""
    try:
        level = await crud.move_stock(session, movement_data)
        response_data = serialize_model(level, InventoryLevelResponse)
        return ORJSONResponse(content=response_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка движения товара: {str(e)}"
        )


@router.post(
    "/inventory/reserve",
    summary="Резервировать товар",
    description="Резервирует указанное количество товара на складе."
)
async def reserve_stock(
    item_id: UUID,
    warehouse_id: UUID,
    session: DbSession,
    quantity: int = Query(..., ge=1, description="Количество для резервирования")
):
    """Резервирование товара"""
    success = await crud.reserve_stock(session, item_id, warehouse_id, quantity)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно товара для резервирования"
        )
    
    return ORJSONResponse(content={"message": "Товар успешно зарезервирован"})


@router.post(
    "/inventory/release",
    summary="Снять резервирование",
    description="Снимает резервирование с указанного количества товара."
)
async def release_reservation(
    item_id: UUID,
    warehouse_id: UUID,
    session: DbSession,
    quantity: int = Query(..., ge=1, description="Количество для снятия резервирования")
):
    """Снятие резервирования товара"""
    success = await crud.release_reservation(session, item_id, warehouse_id, quantity)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка снятия резервирования"
        )
    
    return ORJSONResponse(content={"message": "Резервирование успешно снято"})


# ===== Analytics Endpoints =====

@router.get(
    "/analytics/low-stock",
    summary="Товары с низким остатком",
    description="Возвращает список товаров с остатком ниже минимального уровня."
)
async def get_low_stock_items(
    session: DbSession,
    warehouse_id: Optional[UUID] = Query(None, description="ID склада (если не указан, поиск по всем складам)")
):
    """Получить товары с низким остатком"""
    items = await crud.get_low_stock_items(session, warehouse_id)
    return ORJSONResponse(content={"low_stock_items": items})


@router.get(
    "/analytics/summary",
    summary="Сводка по запасам",
    description="Возвращает общую сводку по запасам склада или всех складов."
)
async def get_inventory_summary(
    session: DbSession,
    warehouse_id: Optional[UUID] = Query(None, description="ID склада (если не указан, сводка по всем складам)")
):
    """Получить сводку по запасам"""
    summary = await crud.get_inventory_summary(session, warehouse_id)
    return ORJSONResponse(content=summary)
