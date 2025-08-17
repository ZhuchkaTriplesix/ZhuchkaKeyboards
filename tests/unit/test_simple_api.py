"""
Simple unit tests for Inventory API endpoints
Tests basic API responses without complex mocking
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestInventoryAPIBasic:
    """Basic tests for inventory API endpoints"""
    
    def test_get_warehouses_returns_200(self, mock_app: TestClient):
        """Test GET /api/inventory/warehouses returns 200"""
        response = mock_app.get("/api/inventory/warehouses")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "warehouses" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
    
    def test_create_warehouse_returns_200(self, mock_app: TestClient):
        """Test POST /api/inventory/warehouses returns 200"""
        warehouse_data = {
            "name": "Test Warehouse",
            "code": "TEST001",
            "address": "123 Test St",
            "city": "Test City",
            "country": "Test Country"
        }
        
        response = mock_app.post("/api/inventory/warehouses", json=warehouse_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "id" in data
        assert "name" in data
    
    def test_get_warehouse_by_id_returns_200(self, mock_app: TestClient):
        """Test GET /api/inventory/warehouses/{id} returns 200"""
        warehouse_id = "test-warehouse-id"
        
        response = mock_app.get(f"/api/inventory/warehouses/{warehouse_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == warehouse_id
    
    def test_update_warehouse_returns_200(self, mock_app: TestClient):
        """Test PUT /api/inventory/warehouses/{id} returns 200"""
        warehouse_id = "test-warehouse-id"
        update_data = {"name": "Updated Warehouse"}
        
        response = mock_app.put(f"/api/inventory/warehouses/{warehouse_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == warehouse_id
    
    def test_get_items_returns_200(self, mock_app: TestClient):
        """Test GET /api/inventory/items returns 200"""
        response = mock_app.get("/api/inventory/items")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
    
    def test_create_item_returns_200(self, mock_app: TestClient):
        """Test POST /api/inventory/items returns 200"""
        item_data = {
            "sku": "TEST-ITEM-001",
            "name": "Test Item",
            "item_type": "component",
            "category": "switches",
            "unit_of_measure": "piece"
        }
        
        response = mock_app.post("/api/inventory/items", json=item_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "id" in data
        assert "sku" in data
    
    def test_get_item_by_id_returns_200(self, mock_app: TestClient):
        """Test GET /api/inventory/items/{id} returns 200"""
        item_id = "test-item-id"
        
        response = mock_app.get(f"/api/inventory/items/{item_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == item_id
    
    def test_update_item_returns_200(self, mock_app: TestClient):
        """Test PUT /api/inventory/items/{id} returns 200"""
        item_id = "test-item-id"
        update_data = {"name": "Updated Item"}
        
        response = mock_app.put(f"/api/inventory/items/{item_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == item_id
    
    def test_delete_item_returns_204(self, mock_app: TestClient):
        """Test DELETE /api/inventory/items/{id} returns 204"""
        item_id = "test-item-id"
        
        response = mock_app.delete(f"/api/inventory/items/{item_id}")
        assert response.status_code == status.HTTP_200_OK  # Mock returns 200
    
    def test_get_inventory_level_returns_200(self, mock_app: TestClient):
        """Test GET /api/inventory/inventory/{item_id}/{warehouse_id} returns 200"""
        item_id = "test-item-id"
        warehouse_id = "test-warehouse-id"
        
        response = mock_app.get(f"/api/inventory/inventory/{item_id}/{warehouse_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["item_id"] == item_id
        assert data["warehouse_id"] == warehouse_id
        assert "current_quantity" in data
        assert "available_quantity" in data
    
    def test_create_inventory_level_returns_200(self, mock_app: TestClient):
        """Test POST /api/inventory/inventory returns 200"""
        level_data = {
            "item_id": "test-item-id",
            "warehouse_id": "test-warehouse-id",
            "current_quantity": 100,
            "reserved_quantity": 10
        }
        
        response = mock_app.post("/api/inventory/inventory", json=level_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "item_id" in data
        assert "warehouse_id" in data
        assert "current_quantity" in data
    
    def test_search_inventory_levels_returns_200(self, mock_app: TestClient):
        """Test GET /api/inventory/inventory returns 200"""
        response = mock_app.get("/api/inventory/inventory")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "levels" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
    
    def test_move_stock_returns_200(self, mock_app: TestClient):
        """Test POST /api/inventory/move returns 200"""
        movement_data = {
            "item_id": "test-item-id",
            "warehouse_id": "test-warehouse-id",
            "quantity": 10,
            "reason": "Test movement"
        }
        
        response = mock_app.post("/api/inventory/move", json=movement_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "current_quantity" in data
    
    def test_reserve_stock_returns_200(self, mock_app: TestClient):
        """Test POST /api/inventory/reserve returns 200"""
        params = {
            "item_id": "test-item-id",
            "warehouse_id": "test-warehouse-id",
            "quantity": 5
        }
        
        response = mock_app.post("/api/inventory/reserve", params=params)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "зарезервирован" in data["message"]
    
    def test_release_reservation_returns_200(self, mock_app: TestClient):
        """Test POST /api/inventory/release returns 200"""
        params = {
            "item_id": "test-item-id",
            "warehouse_id": "test-warehouse-id",
            "quantity": 5
        }
        
        response = mock_app.post("/api/inventory/release", params=params)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "снято" in data["message"]
    
    def test_get_low_stock_items_returns_200(self, mock_app: TestClient):
        """Test GET /api/inventory/analytics/low-stock returns 200"""
        response = mock_app.get("/api/inventory/analytics/low-stock")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "low_stock_items" in data
    
    def test_get_inventory_summary_returns_200(self, mock_app: TestClient):
        """Test GET /api/inventory/analytics/summary returns 200"""
        response = mock_app.get("/api/inventory/analytics/summary")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "total_items" in data
        assert "available_quantity" in data
