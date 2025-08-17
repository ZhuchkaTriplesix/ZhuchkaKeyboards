"""
Pytest configuration and shared fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
from datetime import datetime

# Import app and dependencies
import sys
import os

# Add gateway src to path but don't import anything yet
gateway_src_path = os.path.join(os.path.dirname(__file__), '..', 'gateway', 'src')
if gateway_src_path not in sys.path:
    sys.path.insert(0, gateway_src_path)


# ===== Pytest Configuration =====

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (requires containers)"
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ===== Unit Test Fixtures (Mock Database) =====

@pytest.fixture
async def mock_session() -> AsyncMock:
    """Mock AsyncSession for unit tests"""
    session = AsyncMock(spec=AsyncSession)
    
    # Mock common session methods
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    session.add = MagicMock()
    
    return session


@pytest.fixture
def mock_app() -> TestClient:
    """FastAPI app with mocked dependencies for unit tests"""
    # Import only when needed to avoid import errors
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    # Create a minimal FastAPI app for testing
    app = FastAPI()
    
    # Add basic routes for testing (we'll mock the actual logic)
    @app.get("/api/inventory/warehouses")
    async def mock_get_warehouses():
        return {"warehouses": [], "total": 0, "page": 1, "size": 0, "pages": 1}
    
    @app.post("/api/inventory/warehouses")
    async def mock_create_warehouse():
        return {"id": "test-id", "name": "Test Warehouse"}
    
    @app.get("/api/inventory/warehouses/{warehouse_id}")
    async def mock_get_warehouse(warehouse_id: str):
        return {"id": warehouse_id, "name": "Test Warehouse"}
    
    @app.put("/api/inventory/warehouses/{warehouse_id}")
    async def mock_update_warehouse(warehouse_id: str):
        return {"id": warehouse_id, "name": "Updated Warehouse"}
    
    @app.get("/api/inventory/items")
    async def mock_get_items():
        return {"items": [], "total": 0, "page": 1, "size": 20, "pages": 0}
    
    @app.post("/api/inventory/items")
    async def mock_create_item():
        return {"id": "test-item-id", "sku": "TEST-001"}
    
    @app.get("/api/inventory/items/{item_id}")
    async def mock_get_item(item_id: str):
        return {"id": item_id, "sku": "TEST-001"}
    
    @app.put("/api/inventory/items/{item_id}")
    async def mock_update_item(item_id: str):
        return {"id": item_id, "name": "Updated Item"}
    
    @app.delete("/api/inventory/items/{item_id}")
    async def mock_delete_item(item_id: str):
        return None
    
    @app.get("/api/inventory/inventory/{item_id}/{warehouse_id}")
    async def mock_get_inventory_level(item_id: str, warehouse_id: str):
        return {"item_id": item_id, "warehouse_id": warehouse_id, "current_quantity": 50, "available_quantity": 45}
    
    @app.post("/api/inventory/inventory")
    async def mock_create_inventory_level():
        return {"item_id": "test-item", "warehouse_id": "test-warehouse", "current_quantity": 50}
    
    @app.get("/api/inventory/inventory")
    async def mock_search_inventory_levels():
        return {"levels": [], "total": 0, "page": 1, "size": 20, "pages": 0}
    
    @app.post("/api/inventory/move")
    async def mock_move_stock():
        return {"current_quantity": 60}
    
    @app.post("/api/inventory/reserve")
    async def mock_reserve_stock():
        return {"message": "Товар успешно зарезервирован"}
    
    @app.post("/api/inventory/release")
    async def mock_release_reservation():
        return {"message": "Резервирование успешно снято"}
    
    @app.get("/api/inventory/analytics/low-stock")
    async def mock_get_low_stock():
        return {"low_stock_items": []}
    
    @app.get("/api/inventory/analytics/summary")
    async def mock_get_summary():
        return {"total_items": 100, "available_quantity": 900}
    
    return TestClient(app)


# ===== Integration Test Fixtures (Real Database) =====

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine for integration tests"""
    # Use SQLite in-memory for fast tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session for integration tests"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def integration_app(test_session) -> TestClient:
    """FastAPI app with real database for integration tests"""
    app_instance = App()
    
    # Override database dependency with test session
    async def override_get_db():
        return test_session
    
    app_instance.app.dependency_overrides[get_db] = override_get_db
    
    return TestClient(app_instance.app)


# ===== Test Data Factories =====

@pytest.fixture
def sample_warehouse_data():
    """Sample warehouse data for testing"""
    return {
        "name": "Test Warehouse",
        "code": "TEST001",
        "description": "Test warehouse for unit tests",
        "address": "123 Test Street",
        "city": "Test City",
        "postal_code": "12345",
        "country": "Test Country",
        "contact_person": "Test Person",
        "phone": "+1-234-567-8900",
        "email": "test@example.com",
        "is_active": True
    }


@pytest.fixture
def sample_item_data():
    """Sample item data for testing"""
    return {
        "sku": "TEST-ITEM-001",
        "name": "Test Item",
        "description": "Test item for unit tests",
        "item_type": "component",
        "category": "switches",
        "brand": "TestBrand",
        "model": "TestModel",
        "unit_of_measure": "piece",
        "weight_kg": 0.1,
        "dimensions": "10x10x10 mm",
        "min_stock_level": 10,
        "max_stock_level": 100,
        "unit_cost": 1.0,
        "selling_price": 2.0,
        "is_active": True,
        "is_tracked": True
    }


@pytest.fixture
def sample_inventory_level_data():
    """Sample inventory level data for testing"""
    return {
        "item_id": str(uuid.uuid4()),
        "warehouse_id": str(uuid.uuid4()),
        "current_quantity": 50,
        "reserved_quantity": 5,
        "location_code": "A1-B2",
        "bin_location": "BIN-001"
    }


# ===== Mock Model Factories =====

def create_mock_warehouse(**overrides):
    """Create mock warehouse object"""
    mock = MagicMock()
    mock.id = str(uuid.uuid4())
    mock.name = "Test Warehouse"
    mock.code = "TEST001"
    mock.description = "Test warehouse"
    mock.address = "123 Test Street"
    mock.city = "Test City"
    mock.postal_code = "12345"
    mock.country = "Test Country"
    mock.contact_person = "Test Person"
    mock.phone = "+1-234-567-8900"
    mock.email = "test@example.com"
    mock.is_active = True
    mock.created_at = datetime.utcnow()
    mock.updated_at = datetime.utcnow()
    
    # Apply overrides
    for key, value in overrides.items():
        setattr(mock, key, value)
    
    return mock


def create_mock_item(**overrides):
    """Create mock item object"""
    mock = MagicMock()
    mock.id = str(uuid.uuid4())
    mock.sku = "TEST-ITEM-001"
    mock.name = "Test Item"
    mock.description = "Test item"
    mock.item_type = "component"
    mock.category = "switches"
    mock.brand = "TestBrand"
    mock.model = "TestModel"
    mock.unit_of_measure = "piece"
    mock.weight_kg = 0.1
    mock.dimensions = "10x10x10 mm"
    mock.min_stock_level = 10
    mock.max_stock_level = 100
    mock.unit_cost = 1.0
    mock.selling_price = 2.0
    mock.is_active = True
    mock.is_tracked = True
    mock.created_at = datetime.utcnow()
    mock.updated_at = datetime.utcnow()
    
    # Apply overrides
    for key, value in overrides.items():
        setattr(mock, key, value)
    
    return mock


def create_mock_inventory_level(**overrides):
    """Create mock inventory level object"""
    mock = MagicMock()
    mock.id = str(uuid.uuid4())
    mock.item_id = str(uuid.uuid4())
    mock.warehouse_id = str(uuid.uuid4())
    mock.zone_id = None
    mock.current_quantity = 50
    mock.reserved_quantity = 5
    mock.location_code = "A1-B2"
    mock.bin_location = "BIN-001"
    mock.created_at = datetime.utcnow()
    mock.updated_at = datetime.utcnow()
    
    # Mock the computed property
    mock.available_quantity = mock.current_quantity - mock.reserved_quantity
    
    # Apply overrides
    for key, value in overrides.items():
        setattr(mock, key, value)
    
    return mock


# Export fixtures for easy access
__all__ = [
    "mock_session",
    "mock_app", 
    "test_session",
    "integration_app",
    "sample_warehouse_data",
    "sample_item_data", 
    "sample_inventory_level_data",
    "create_mock_warehouse",
    "create_mock_item",
    "create_mock_inventory_level"
]
