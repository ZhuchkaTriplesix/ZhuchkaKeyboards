"""
Unit tests for Inventory API endpoints
Tests API logic without database dependencies using mocks
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestWarehouseAPI:
    """Unit tests for Warehouse API endpoints"""

    def test_get_warehouses_empty(self, mock_app: TestClient):
        """Test GET /api/inventory/warehouses with empty result"""
        response = mock_app.get("/api/inventory/warehouses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["warehouses"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 0
        assert data["pages"] == 1

    def test_get_warehouses_with_data(self, mock_app: TestClient):
        """Test GET /api/inventory/warehouses with data"""
        mock_warehouses = [
            create_mock_warehouse(name="Warehouse 1"),
            create_mock_warehouse(name="Warehouse 2"),
        ]

        with patch("routers.inventory.crud.get_all_warehouses") as mock_crud:
            mock_crud.return_value = mock_warehouses

            response = mock_app.get("/api/inventory/warehouses")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["warehouses"]) == 2
            assert data["total"] == 2
            assert data["warehouses"][0]["name"] == "Warehouse 1"
            assert data["warehouses"][1]["name"] == "Warehouse 2"

    def test_get_warehouse_by_id_success(self, mock_app: TestClient):
        """Test GET /api/inventory/warehouses/{id} - success"""
        mock_warehouse = create_mock_warehouse()
        warehouse_id = mock_warehouse.id

        with patch("routers.inventory.crud.get_warehouse_by_id") as mock_crud:
            mock_crud.return_value = mock_warehouse

            response = mock_app.get(f"/api/inventory/warehouses/{warehouse_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == warehouse_id
            assert data["name"] == mock_warehouse.name

    def test_get_warehouse_by_id_not_found(self, mock_app: TestClient):
        """Test GET /api/inventory/warehouses/{id} - not found"""
        warehouse_id = "non-existent-id"

        with patch("routers.inventory.crud.get_warehouse_by_id") as mock_crud:
            mock_crud.return_value = None

            response = mock_app.get(f"/api/inventory/warehouses/{warehouse_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "не найден" in response.json()["detail"]

    def test_create_warehouse_success(
        self, mock_app: TestClient, sample_warehouse_data
    ):
        """Test POST /api/inventory/warehouses - success"""
        mock_warehouse = create_mock_warehouse(**sample_warehouse_data)

        with (
            patch("routers.inventory.crud.get_warehouse_by_code") as mock_get,
            patch("routers.inventory.crud.create_warehouse") as mock_create,
        ):
            mock_get.return_value = None  # No existing warehouse
            mock_create.return_value = mock_warehouse

            response = mock_app.post(
                "/api/inventory/warehouses", json=sample_warehouse_data
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["name"] == sample_warehouse_data["name"]
            assert data["code"] == sample_warehouse_data["code"]

    def test_create_warehouse_duplicate_code(
        self, mock_app: TestClient, sample_warehouse_data
    ):
        """Test POST /api/inventory/warehouses - duplicate code"""
        existing_warehouse = create_mock_warehouse()

        with patch("routers.inventory.crud.get_warehouse_by_code") as mock_get:
            mock_get.return_value = existing_warehouse  # Existing warehouse

            response = mock_app.post(
                "/api/inventory/warehouses", json=sample_warehouse_data
            )

            assert response.status_code == status.HTTP_409_CONFLICT
            assert "уже существует" in response.json()["detail"]

    def test_update_warehouse_success(self, mock_app: TestClient):
        """Test PUT /api/inventory/warehouses/{id} - success"""
        warehouse_id = "test-warehouse-id"
        update_data = {"name": "Updated Warehouse"}
        mock_warehouse = create_mock_warehouse(**update_data)

        with patch("routers.inventory.crud.update_warehouse") as mock_crud:
            mock_crud.return_value = mock_warehouse

            response = mock_app.put(
                f"/api/inventory/warehouses/{warehouse_id}", json=update_data
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Updated Warehouse"

    def test_update_warehouse_not_found(self, mock_app: TestClient):
        """Test PUT /api/inventory/warehouses/{id} - not found"""
        warehouse_id = "non-existent-id"
        update_data = {"name": "Updated Warehouse"}

        with patch("routers.inventory.crud.update_warehouse") as mock_crud:
            mock_crud.return_value = None

            response = mock_app.put(
                f"/api/inventory/warehouses/{warehouse_id}", json=update_data
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
class TestItemAPI:
    """Unit tests for Item API endpoints"""

    def test_get_items_empty(self, mock_app: TestClient):
        """Test GET /api/inventory/items with empty result"""
        mock_result = {"items": [], "total": 0, "page": 1, "size": 20, "pages": 0}

        with patch("routers.inventory.crud.search_items") as mock_crud:
            mock_crud.return_value = mock_result

            response = mock_app.get("/api/inventory/items")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["items"] == []
            assert data["total"] == 0

    def test_get_items_with_filters(self, mock_app: TestClient):
        """Test GET /api/inventory/items with filters"""
        mock_items = [create_mock_item(item_type="component")]
        mock_result = {
            "items": mock_items,
            "total": 1,
            "page": 1,
            "size": 20,
            "pages": 1,
        }

        with patch("routers.inventory.crud.search_items") as mock_crud:
            mock_crud.return_value = mock_result

            response = mock_app.get(
                "/api/inventory/items?item_type=component&search=test"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["items"]) == 1
            assert data["items"][0]["item_type"] == "component"

    def test_create_item_success(self, mock_app: TestClient, sample_item_data):
        """Test POST /api/inventory/items - success"""
        mock_item = create_mock_item(**sample_item_data)

        with (
            patch("routers.inventory.crud.get_item_by_sku") as mock_get,
            patch("routers.inventory.crud.create_item") as mock_create,
        ):
            mock_get.return_value = None  # No existing item
            mock_create.return_value = mock_item

            response = mock_app.post("/api/inventory/items", json=sample_item_data)

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["sku"] == sample_item_data["sku"]
            assert data["name"] == sample_item_data["name"]

    def test_create_item_duplicate_sku(self, mock_app: TestClient, sample_item_data):
        """Test POST /api/inventory/items - duplicate SKU"""
        existing_item = create_mock_item()

        with patch("routers.inventory.crud.get_item_by_sku") as mock_get:
            mock_get.return_value = existing_item  # Existing item

            response = mock_app.post("/api/inventory/items", json=sample_item_data)

            assert response.status_code == status.HTTP_409_CONFLICT
            assert "уже существует" in response.json()["detail"]

    def test_get_item_by_id_success(self, mock_app: TestClient):
        """Test GET /api/inventory/items/{id} - success"""
        mock_item = create_mock_item()
        item_id = mock_item.id

        with patch("routers.inventory.crud.get_item_by_id") as mock_crud:
            mock_crud.return_value = mock_item

            response = mock_app.get(f"/api/inventory/items/{item_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == item_id
            assert data["sku"] == mock_item.sku

    def test_update_item_success(self, mock_app: TestClient):
        """Test PUT /api/inventory/items/{id} - success"""
        item_id = "test-item-id"
        update_data = {"name": "Updated Item"}
        mock_item = create_mock_item(**update_data)

        with patch("routers.inventory.crud.update_item") as mock_crud:
            mock_crud.return_value = mock_item

            response = mock_app.put(f"/api/inventory/items/{item_id}", json=update_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Updated Item"

    def test_delete_item_success(self, mock_app: TestClient):
        """Test DELETE /api/inventory/items/{id} - success"""
        item_id = "test-item-id"

        with patch("routers.inventory.crud.delete_item") as mock_crud:
            mock_crud.return_value = True

            response = mock_app.delete(f"/api/inventory/items/{item_id}")

            assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.unit
class TestInventoryLevelAPI:
    """Unit tests for Inventory Level API endpoints"""

    def test_get_inventory_level_success(self, mock_app: TestClient):
        """Test GET /api/inventory/{item_id}/{warehouse_id} - success"""
        mock_level = create_mock_inventory_level()
        item_id = mock_level.item_id
        warehouse_id = mock_level.warehouse_id

        with patch("routers.inventory.crud.get_inventory_level") as mock_crud:
            mock_crud.return_value = mock_level

            response = mock_app.get(
                f"/api/inventory/inventory/{item_id}/{warehouse_id}"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["item_id"] == item_id
            assert data["warehouse_id"] == warehouse_id
            assert data["available_quantity"] == mock_level.available_quantity

    def test_create_inventory_level_success(
        self, mock_app: TestClient, sample_inventory_level_data
    ):
        """Test POST /api/inventory/inventory - success"""
        mock_level = create_mock_inventory_level(**sample_inventory_level_data)

        with (
            patch("routers.inventory.crud.get_inventory_level") as mock_get,
            patch("routers.inventory.crud.create_inventory_level") as mock_create,
        ):
            mock_get.return_value = None  # No existing level
            mock_create.return_value = mock_level

            response = mock_app.post(
                "/api/inventory/inventory", json=sample_inventory_level_data
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert (
                data["current_quantity"]
                == sample_inventory_level_data["current_quantity"]
            )

    def test_search_inventory_levels(self, mock_app: TestClient):
        """Test GET /api/inventory/inventory with filters"""
        mock_levels = [create_mock_inventory_level()]
        mock_result = {
            "levels": mock_levels,
            "total": 1,
            "page": 1,
            "size": 20,
            "pages": 1,
        }

        with patch("routers.inventory.crud.search_inventory_levels") as mock_crud:
            mock_crud.return_value = mock_result

            response = mock_app.get("/api/inventory/inventory?min_quantity=10")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["levels"]) == 1


@pytest.mark.unit
class TestStockMovementAPI:
    """Unit tests for Stock Movement API endpoints"""

    def test_move_stock_success(self, mock_app: TestClient):
        """Test POST /api/inventory/move - success"""
        movement_data = {
            "item_id": "test-item-id",
            "warehouse_id": "test-warehouse-id",
            "quantity": 10,
            "reason": "Test movement",
            "reference_number": "REF-001",
        }
        mock_level = create_mock_inventory_level()

        with patch("routers.inventory.crud.move_stock") as mock_crud:
            mock_crud.return_value = mock_level

            response = mock_app.post("/api/inventory/move", json=movement_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "current_quantity" in data

    def test_reserve_stock_success(self, mock_app: TestClient):
        """Test POST /api/inventory/reserve - success"""
        params = {
            "item_id": "test-item-id",
            "warehouse_id": "test-warehouse-id",
            "quantity": 5,
        }

        with patch("routers.inventory.crud.reserve_stock") as mock_crud:
            mock_crud.return_value = True

            response = mock_app.post("/api/inventory/reserve", params=params)

            assert response.status_code == status.HTTP_200_OK
            assert "успешно зарезервирован" in response.json()["message"]

    def test_reserve_stock_insufficient(self, mock_app: TestClient):
        """Test POST /api/inventory/reserve - insufficient stock"""
        params = {
            "item_id": "test-item-id",
            "warehouse_id": "test-warehouse-id",
            "quantity": 1000,
        }

        with patch("routers.inventory.crud.reserve_stock") as mock_crud:
            mock_crud.return_value = False

            response = mock_app.post("/api/inventory/reserve", params=params)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Недостаточно товара" in response.json()["detail"]

    def test_release_reservation_success(self, mock_app: TestClient):
        """Test POST /api/inventory/release - success"""
        params = {
            "item_id": "test-item-id",
            "warehouse_id": "test-warehouse-id",
            "quantity": 5,
        }

        with patch("routers.inventory.crud.release_reservation") as mock_crud:
            mock_crud.return_value = True

            response = mock_app.post("/api/inventory/release", params=params)

            assert response.status_code == status.HTTP_200_OK
            assert "успешно снято" in response.json()["message"]


@pytest.mark.unit
class TestAnalyticsAPI:
    """Unit tests for Analytics API endpoints"""

    def test_get_low_stock_items(self, mock_app: TestClient):
        """Test GET /api/inventory/analytics/low-stock"""
        mock_items = [
            {
                "id": "item-1",
                "sku": "TEST-001",
                "name": "Test Item 1",
                "min_stock_level": 10,
                "total_quantity": 5,
            }
        ]

        with patch("routers.inventory.crud.get_low_stock_items") as mock_crud:
            mock_crud.return_value = mock_items

            response = mock_app.get("/api/inventory/analytics/low-stock")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "low_stock_items" in data
            assert len(data["low_stock_items"]) == 1

    def test_get_inventory_summary(self, mock_app: TestClient):
        """Test GET /api/inventory/analytics/summary"""
        mock_summary = {
            "total_items": 100,
            "total_quantity": 1000,
            "reserved_quantity": 100,
            "available_quantity": 900,
            "zero_stock_items": 5,
        }

        with patch("routers.inventory.crud.get_inventory_summary") as mock_crud:
            mock_crud.return_value = mock_summary

            response = mock_app.get("/api/inventory/analytics/summary")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_items"] == 100
            assert data["available_quantity"] == 900
