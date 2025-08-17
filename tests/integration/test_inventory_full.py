"""
Integration tests for Inventory API
Tests full workflow with real database and backend services
"""

import pytest
import asyncio
import uuid
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from routers.inventory.models import Item, Warehouse, InventoryLevel


@pytest.mark.integration
class TestInventoryIntegration:
    """Integration tests for complete inventory workflow"""
    
    def test_complete_warehouse_lifecycle(self, integration_app: TestClient):
        """Test complete warehouse CRUD lifecycle"""
        # 1. Create warehouse
        warehouse_data = {
            "name": "Integration Test Warehouse",
            "code": "INT-TEST-001",
            "description": "Warehouse for integration testing",
            "address": "123 Integration St",
            "city": "Test City",
            "postal_code": "12345",
            "country": "Test Country",
            "contact_person": "Test Manager",
            "phone": "+1-555-0123",
            "email": "test@integration.com",
            "is_active": True
        }
        
        # Create
        response = integration_app.post("/api/inventory/warehouses", json=warehouse_data)
        assert response.status_code == status.HTTP_201_CREATED
        created_warehouse = response.json()
        warehouse_id = created_warehouse["id"]
        assert created_warehouse["name"] == warehouse_data["name"]
        assert created_warehouse["code"] == warehouse_data["code"]
        
        # Read
        response = integration_app.get(f"/api/inventory/warehouses/{warehouse_id}")
        assert response.status_code == status.HTTP_200_OK
        retrieved_warehouse = response.json()
        assert retrieved_warehouse["id"] == warehouse_id
        assert retrieved_warehouse["name"] == warehouse_data["name"]
        
        # Update
        update_data = {"name": "Updated Integration Warehouse"}
        response = integration_app.put(f"/api/inventory/warehouses/{warehouse_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        updated_warehouse = response.json()
        assert updated_warehouse["name"] == "Updated Integration Warehouse"
        
        # List all warehouses
        response = integration_app.get("/api/inventory/warehouses")
        assert response.status_code == status.HTTP_200_OK
        warehouses = response.json()
        assert warehouses["total"] >= 1
        warehouse_ids = [w["id"] for w in warehouses["warehouses"]]
        assert warehouse_id in warehouse_ids
    
    def test_complete_item_lifecycle(self, integration_app: TestClient):
        """Test complete item CRUD lifecycle"""
        # 1. Create item
        item_data = {
            "sku": "INT-TEST-SWITCH-001",
            "name": "Integration Test Switch",
            "description": "Cherry MX switch for integration testing",
            "item_type": "component",
            "category": "switches",
            "brand": "TestCherry",
            "model": "MX Integration",
            "unit_of_measure": "piece",
            "weight_kg": 0.008,
            "dimensions": "15x15x11 mm",
            "min_stock_level": 50,
            "max_stock_level": 500,
            "unit_cost": 1.25,
            "selling_price": 2.50,
            "is_active": True,
            "is_tracked": True
        }
        
        # Create
        response = integration_app.post("/api/inventory/items", json=item_data)
        assert response.status_code == status.HTTP_201_CREATED
        created_item = response.json()
        item_id = created_item["id"]
        assert created_item["sku"] == item_data["sku"]
        assert created_item["name"] == item_data["name"]
        
        # Read
        response = integration_app.get(f"/api/inventory/items/{item_id}")
        assert response.status_code == status.HTTP_200_OK
        retrieved_item = response.json()
        assert retrieved_item["id"] == item_id
        assert retrieved_item["sku"] == item_data["sku"]
        
        # Update
        update_data = {"name": "Updated Integration Switch", "unit_cost": 1.50}
        response = integration_app.put(f"/api/inventory/items/{item_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        updated_item = response.json()
        assert updated_item["name"] == "Updated Integration Switch"
        assert updated_item["unit_cost"] == 1.50
        
        # Search items
        response = integration_app.get("/api/inventory/items?search=Integration")
        assert response.status_code == status.HTTP_200_OK
        search_results = response.json()
        assert search_results["total"] >= 1
        found_item = next((item for item in search_results["items"] if item["id"] == item_id), None)
        assert found_item is not None
        
        # Search by filters
        response = integration_app.get("/api/inventory/items?item_type=component&category=switches")
        assert response.status_code == status.HTTP_200_OK
        filtered_results = response.json()
        assert filtered_results["total"] >= 1
        
        # Delete (soft delete)
        response = integration_app.delete(f"/api/inventory/items/{item_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify item is deactivated
        response = integration_app.get(f"/api/inventory/items/{item_id}")
        assert response.status_code == status.HTTP_200_OK
        deleted_item = response.json()
        assert deleted_item["is_active"] is False
    
    def test_inventory_level_and_movements(self, integration_app: TestClient):
        """Test inventory levels and stock movements"""
        # First create warehouse and item
        warehouse_data = {
            "name": "Movement Test Warehouse",
            "code": "MOVE-TEST-001",
            "address": "Movement St 1",
            "city": "Test City",
            "country": "Test Country"
        }
        warehouse_response = integration_app.post("/api/inventory/warehouses", json=warehouse_data)
        warehouse_id = warehouse_response.json()["id"]
        
        item_data = {
            "sku": "MOVE-TEST-001",
            "name": "Movement Test Item",
            "item_type": "component",
            "category": "switches",
            "unit_of_measure": "piece",
            "min_stock_level": 10,
            "max_stock_level": 100,
            "unit_cost": 1.0,
            "selling_price": 2.0
        }
        item_response = integration_app.post("/api/inventory/items", json=item_data)
        item_id = item_response.json()["id"]
        
        # Create initial inventory level
        level_data = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "current_quantity": 0,
            "reserved_quantity": 0,
            "location_code": "A1-B1",
            "bin_location": "BIN-001"
        }
        response = integration_app.post("/api/inventory/inventory", json=level_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Stock in movement (+50)
        movement_data = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "quantity": 50,
            "reason": "Initial stock",
            "reference_number": "IN-001"
        }
        response = integration_app.post("/api/inventory/move", json=movement_data)
        assert response.status_code == status.HTTP_200_OK
        level_after_in = response.json()
        assert level_after_in["current_quantity"] == 50
        assert level_after_in["available_quantity"] == 50
        
        # Reserve stock (10 units)
        reserve_params = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "quantity": 10
        }
        response = integration_app.post("/api/inventory/reserve", params=reserve_params)
        assert response.status_code == status.HTTP_200_OK
        
        # Check inventory level after reservation
        response = integration_app.get(f"/api/inventory/inventory/{item_id}/{warehouse_id}")
        assert response.status_code == status.HTTP_200_OK
        level_after_reserve = response.json()
        assert level_after_reserve["current_quantity"] == 50
        assert level_after_reserve["reserved_quantity"] == 10
        assert level_after_reserve["available_quantity"] == 40
        
        # Stock out movement (-20)
        movement_data = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "quantity": -20,
            "reason": "Sale",
            "reference_number": "OUT-001"
        }
        response = integration_app.post("/api/inventory/move", json=movement_data)
        assert response.status_code == status.HTTP_200_OK
        level_after_out = response.json()
        assert level_after_out["current_quantity"] == 30
        assert level_after_out["available_quantity"] == 20  # 30 - 10 reserved
        
        # Release reservation (5 units)
        release_params = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "quantity": 5
        }
        response = integration_app.post("/api/inventory/release", params=release_params)
        assert response.status_code == status.HTTP_200_OK
        
        # Check final inventory level
        response = integration_app.get(f"/api/inventory/inventory/{item_id}/{warehouse_id}")
        assert response.status_code == status.HTTP_200_OK
        final_level = response.json()
        assert final_level["current_quantity"] == 30
        assert final_level["reserved_quantity"] == 5
        assert final_level["available_quantity"] == 25
        
        # Search inventory levels
        response = integration_app.get(f"/api/inventory/inventory?warehouse_id={warehouse_id}")
        assert response.status_code == status.HTTP_200_OK
        inventory_search = response.json()
        assert inventory_search["total"] >= 1
        
        # Try to reserve more than available (should fail)
        over_reserve_params = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "quantity": 30  # More than available (25)
        }
        response = integration_app.post("/api/inventory/reserve", params=over_reserve_params)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Try to move out more than current (should fail)
        over_out_movement = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "quantity": -50,  # More than current (30)
            "reason": "Over sale",
            "reference_number": "OVER-001"
        }
        response = integration_app.post("/api/inventory/move", json=over_out_movement)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_analytics_endpoints(self, integration_app: TestClient):
        """Test analytics endpoints with real data"""
        # Create test data first
        warehouse_data = {
            "name": "Analytics Test Warehouse",
            "code": "ANALYTICS-001",
            "address": "Analytics St 1",
            "city": "Test City",
            "country": "Test Country"
        }
        warehouse_response = integration_app.post("/api/inventory/warehouses", json=warehouse_data)
        warehouse_id = warehouse_response.json()["id"]
        
        # Create low stock item
        low_stock_item = {
            "sku": "LOW-STOCK-001",
            "name": "Low Stock Item",
            "item_type": "component",
            "category": "switches",
            "unit_of_measure": "piece",
            "min_stock_level": 100,  # High minimum
            "max_stock_level": 1000,
            "unit_cost": 1.0,
            "selling_price": 2.0
        }
        item_response = integration_app.post("/api/inventory/items", json=low_stock_item)
        item_id = item_response.json()["id"]
        
        # Create inventory with low stock
        level_data = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "current_quantity": 10,  # Below minimum
            "reserved_quantity": 0
        }
        integration_app.post("/api/inventory/inventory", json=level_data)
        
        # Test low stock analytics
        response = integration_app.get("/api/inventory/analytics/low-stock")
        assert response.status_code == status.HTTP_200_OK
        low_stock_data = response.json()
        assert "low_stock_items" in low_stock_data
        # Should find our low stock item
        low_stock_items = low_stock_data["low_stock_items"]
        assert len(low_stock_items) >= 1
        
        # Test inventory summary
        response = integration_app.get("/api/inventory/analytics/summary")
        assert response.status_code == status.HTTP_200_OK
        summary = response.json()
        assert "total_items" in summary
        assert "total_quantity" in summary
        assert "available_quantity" in summary
        assert summary["total_items"] >= 1
        
        # Test warehouse-specific summary
        response = integration_app.get(f"/api/inventory/analytics/summary?warehouse_id={warehouse_id}")
        assert response.status_code == status.HTTP_200_OK
        warehouse_summary = response.json()
        assert warehouse_summary["total_items"] >= 1
    
    def test_error_handling(self, integration_app: TestClient):
        """Test error handling in integration environment"""
        # Test 404 errors
        non_existent_id = str(uuid.uuid4())
        
        response = integration_app.get(f"/api/inventory/items/{non_existent_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = integration_app.get(f"/api/inventory/warehouses/{non_existent_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = integration_app.get(f"/api/inventory/inventory/{non_existent_id}/{non_existent_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test duplicate creation errors
        warehouse_data = {
            "name": "Duplicate Test Warehouse",
            "code": "DUPLICATE-001",
            "address": "Duplicate St 1",
            "city": "Test City",
            "country": "Test Country"
        }
        
        # Create first warehouse
        response = integration_app.post("/api/inventory/warehouses", json=warehouse_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to create duplicate
        response = integration_app.post("/api/inventory/warehouses", json=warehouse_data)
        assert response.status_code == status.HTTP_409_CONFLICT
        
        # Same for items
        item_data = {
            "sku": "DUPLICATE-ITEM-001",
            "name": "Duplicate Item",
            "item_type": "component",
            "category": "switches",
            "unit_of_measure": "piece"
        }
        
        # Create first item
        response = integration_app.post("/api/inventory/items", json=item_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to create duplicate
        response = integration_app.post("/api/inventory/items", json=item_data)
        assert response.status_code == status.HTTP_409_CONFLICT
    
    def test_pagination_and_search(self, integration_app: TestClient):
        """Test pagination and search functionality"""
        # Create multiple items for pagination testing
        for i in range(25):
            item_data = {
                "sku": f"PAGINATION-{i:03d}",
                "name": f"Pagination Item {i}",
                "item_type": "component",
                "category": "switches" if i % 2 == 0 else "keycaps",
                "unit_of_measure": "piece",
                "min_stock_level": 10,
                "unit_cost": 1.0,
                "selling_price": 2.0
            }
            response = integration_app.post("/api/inventory/items", json=item_data)
            assert response.status_code == status.HTTP_201_CREATED
        
        # Test pagination
        response = integration_app.get("/api/inventory/items?page=1&size=10")
        assert response.status_code == status.HTTP_200_OK
        page1 = response.json()
        assert len(page1["items"]) == 10
        assert page1["page"] == 1
        assert page1["size"] == 10
        assert page1["total"] >= 25
        
        response = integration_app.get("/api/inventory/items?page=2&size=10")
        assert response.status_code == status.HTTP_200_OK
        page2 = response.json()
        assert len(page2["items"]) == 10
        assert page2["page"] == 2
        
        # Ensure different items on different pages
        page1_ids = {item["id"] for item in page1["items"]}
        page2_ids = {item["id"] for item in page2["items"]}
        assert len(page1_ids.intersection(page2_ids)) == 0
        
        # Test search
        response = integration_app.get("/api/inventory/items?search=Pagination")
        assert response.status_code == status.HTTP_200_OK
        search_results = response.json()
        assert search_results["total"] >= 25
        
        # Test category filter
        response = integration_app.get("/api/inventory/items?category=switches")
        assert response.status_code == status.HTTP_200_OK
        switches_results = response.json()
        # Should be about half the items (due to i % 2 == 0 condition)
        assert switches_results["total"] >= 10
        
        # Verify all returned items are switches
        for item in switches_results["items"]:
            assert item["category"] == "switches"
