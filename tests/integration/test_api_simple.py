"""
Simple integration tests for Inventory API
Tests real API endpoints with requests library
"""

import pytest
import requests
import uuid


BASE_URL = "http://localhost:8001"


@pytest.mark.integration
class TestInventoryAPIIntegration:
    """Integration tests using real API endpoints"""

    def test_health_endpoint(self):
        """Test basic health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data

    def test_warehouse_crud_workflow(self):
        """Test complete warehouse CRUD workflow"""
        # 1. Create warehouse
        warehouse_data = {
            "name": "Integration Test Warehouse",
            "code": f"INT-TEST-{uuid.uuid4().hex[:8].upper()}",
            "description": "Created by integration test",
            "address": "123 Integration St",
            "city": "Test City",
            "postal_code": "12345",
            "country": "Test Country",
            "contact_person": "Test Manager",
            "phone": "+1-555-0123",
            "email": "test@integration.com",
            "is_active": True,
        }

        response = requests.post(
            f"{BASE_URL}/api/inventory/warehouses", json=warehouse_data
        )
        assert response.status_code == 201

        created_warehouse = response.json()
        warehouse_id = created_warehouse["id"]
        assert created_warehouse["name"] == warehouse_data["name"]
        assert created_warehouse["code"] == warehouse_data["code"]
        print(f"✅ Created warehouse: {warehouse_id}")

        # 2. Read warehouse
        response = requests.get(f"{BASE_URL}/api/inventory/warehouses/{warehouse_id}")
        assert response.status_code == 200

        retrieved_warehouse = response.json()
        assert retrieved_warehouse["id"] == warehouse_id
        assert retrieved_warehouse["name"] == warehouse_data["name"]
        print(f"✅ Retrieved warehouse: {warehouse_id}")

        # 3. Update warehouse
        update_data = {
            "name": "Updated Integration Warehouse",
            "description": "Updated by integration test",
        }

        response = requests.put(
            f"{BASE_URL}/api/inventory/warehouses/{warehouse_id}", json=update_data
        )
        assert response.status_code == 200

        updated_warehouse = response.json()
        assert updated_warehouse["name"] == "Updated Integration Warehouse"
        print(f"✅ Updated warehouse: {warehouse_id}")

        # 4. List warehouses
        response = requests.get(f"{BASE_URL}/api/inventory/warehouses")
        assert response.status_code == 200

        warehouses = response.json()
        assert warehouses["total"] >= 1
        warehouse_ids = [w["id"] for w in warehouses["warehouses"]]
        assert warehouse_id in warehouse_ids
        print(f"✅ Listed warehouses: found {warehouses['total']} warehouses")

    def test_item_crud_workflow(self):
        """Test complete item CRUD workflow"""
        # 1. Create item
        item_data = {
            "sku": f"INT-TEST-{uuid.uuid4().hex[:8].upper()}",
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
            "is_tracked": True,
        }

        response = requests.post(f"{BASE_URL}/api/inventory/items", json=item_data)
        assert response.status_code == 201

        created_item = response.json()
        item_id = created_item["id"]
        assert created_item["sku"] == item_data["sku"]
        assert created_item["name"] == item_data["name"]
        print(f"✅ Created item: {item_id}")

        # 2. Read item
        response = requests.get(f"{BASE_URL}/api/inventory/items/{item_id}")
        assert response.status_code == 200

        retrieved_item = response.json()
        assert retrieved_item["id"] == item_id
        assert retrieved_item["sku"] == item_data["sku"]
        print(f"✅ Retrieved item: {item_id}")

        # 3. Update item
        update_data = {
            "name": "Updated Integration Switch",
            "unit_cost": 1.50,
            "selling_price": 3.00,
        }

        response = requests.put(
            f"{BASE_URL}/api/inventory/items/{item_id}", json=update_data
        )
        assert response.status_code == 200

        updated_item = response.json()
        assert updated_item["name"] == "Updated Integration Switch"
        assert updated_item["unit_cost"] == 1.50
        print(f"✅ Updated item: {item_id}")

        # 4. Search items
        response = requests.get(f"{BASE_URL}/api/inventory/items?search=Integration")
        assert response.status_code == 200

        search_results = response.json()
        assert search_results["total"] >= 1
        found_item = next(
            (item for item in search_results["items"] if item["id"] == item_id), None
        )
        assert found_item is not None
        print(f"✅ Found item in search: {item_id}")

        # 5. Delete (soft delete)
        response = requests.delete(f"{BASE_URL}/api/inventory/items/{item_id}")
        assert response.status_code == 204
        print(f"✅ Deleted item: {item_id}")

        # 6. Verify item is deactivated
        response = requests.get(f"{BASE_URL}/api/inventory/items/{item_id}")
        assert response.status_code == 200

        deleted_item = response.json()
        assert deleted_item["is_active"] is False
        print(f"✅ Verified item is deactivated: {item_id}")

    def test_inventory_level_workflow(self):
        """Test inventory level management"""
        # First create warehouse and item
        warehouse_data = {
            "name": "Inventory Test Warehouse",
            "code": f"INV-TEST-{uuid.uuid4().hex[:6].upper()}",
            "address": "Inventory St 1",
            "city": "Test City",
            "country": "Test Country",
        }
        warehouse_response = requests.post(
            f"{BASE_URL}/api/inventory/warehouses", json=warehouse_data
        )
        warehouse_id = warehouse_response.json()["id"]
        print(f"✅ Created test warehouse: {warehouse_id}")

        item_data = {
            "sku": f"INV-ITEM-{uuid.uuid4().hex[:6].upper()}",
            "name": "Inventory Test Item",
            "item_type": "component",
            "category": "switches",
            "unit_of_measure": "piece",
            "min_stock_level": 10,
            "max_stock_level": 100,
            "unit_cost": 1.0,
            "selling_price": 2.0,
        }
        item_response = requests.post(f"{BASE_URL}/api/inventory/items", json=item_data)
        item_id = item_response.json()["id"]
        print(f"✅ Created test item: {item_id}")

        # Create inventory level
        level_data = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "current_quantity": 0,
            "reserved_quantity": 0,
            "location_code": "A1-B1",
            "bin_location": "BIN-001",
        }

        response = requests.post(f"{BASE_URL}/api/inventory/inventory", json=level_data)
        assert response.status_code == 201

        created_level = response.json()
        assert created_level["current_quantity"] == 0
        assert created_level["item_id"] == item_id
        assert created_level["warehouse_id"] == warehouse_id
        print("✅ Created inventory level")

        # Stock in movement (+50)
        movement_data = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "quantity": 50,
            "reason": "Initial stock",
            "reference_number": "IN-001",
        }

        response = requests.post(f"{BASE_URL}/api/inventory/move", json=movement_data)
        assert response.status_code == 200

        level_after_in = response.json()
        assert level_after_in["current_quantity"] == 50
        assert level_after_in["available_quantity"] == 50
        print("✅ Stock in: +50 units")

        # Reserve stock (10 units)
        reserve_params = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "quantity": 10,
        }

        response = requests.post(
            f"{BASE_URL}/api/inventory/reserve", params=reserve_params
        )
        assert response.status_code == 200
        print("✅ Reserved 10 units")

        # Check inventory level after reservation
        response = requests.get(
            f"{BASE_URL}/api/inventory/inventory/{item_id}/{warehouse_id}"
        )
        assert response.status_code == 200

        level_after_reserve = response.json()
        assert level_after_reserve["current_quantity"] == 50
        assert level_after_reserve["reserved_quantity"] == 10
        assert level_after_reserve["available_quantity"] == 40
        print("✅ Inventory after reservation: 50 current, 10 reserved, 40 available")

        # Stock out movement (-20)
        movement_data = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "quantity": -20,
            "reason": "Sale",
            "reference_number": "OUT-001",
        }

        response = requests.post(f"{BASE_URL}/api/inventory/move", json=movement_data)
        assert response.status_code == 200

        level_after_out = response.json()
        assert level_after_out["current_quantity"] == 30
        assert level_after_out["available_quantity"] == 20  # 30 - 10 reserved
        print("✅ Stock out: -20 units")

        # Release reservation (5 units)
        release_params = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "quantity": 5,
        }

        response = requests.post(
            f"{BASE_URL}/api/inventory/release", params=release_params
        )
        assert response.status_code == 200
        print("✅ Released 5 units from reservation")

        # Check final inventory level
        response = requests.get(
            f"{BASE_URL}/api/inventory/inventory/{item_id}/{warehouse_id}"
        )
        assert response.status_code == 200

        final_level = response.json()
        assert final_level["current_quantity"] == 30
        assert final_level["reserved_quantity"] == 5
        assert final_level["available_quantity"] == 25
        print("✅ Final inventory: 30 current, 5 reserved, 25 available")

    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        # Test inventory summary
        response = requests.get(f"{BASE_URL}/api/inventory/analytics/summary")
        assert response.status_code == 200

        summary = response.json()
        assert "total_items" in summary
        assert "total_quantity" in summary
        assert "available_quantity" in summary
        assert isinstance(summary["total_items"], int)
        print(f"✅ Inventory summary: {summary['total_items']} items")

        # Test low stock items
        response = requests.get(f"{BASE_URL}/api/inventory/analytics/low-stock")
        assert response.status_code == 200

        low_stock_data = response.json()
        assert "low_stock_items" in low_stock_data
        assert isinstance(low_stock_data["low_stock_items"], list)
        print(f"✅ Low stock analysis: {len(low_stock_data['low_stock_items'])} items")

    def test_error_handling(self):
        """Test error handling"""
        # Test 404 errors
        non_existent_id = str(uuid.uuid4())

        response = requests.get(f"{BASE_URL}/api/inventory/items/{non_existent_id}")
        assert response.status_code == 404
        print("✅ 404 error handling works for items")

        response = requests.get(
            f"{BASE_URL}/api/inventory/warehouses/{non_existent_id}"
        )
        assert response.status_code == 404
        print("✅ 404 error handling works for warehouses")

        response = requests.get(
            f"{BASE_URL}/api/inventory/inventory/{non_existent_id}/{non_existent_id}"
        )
        assert response.status_code == 404
        print("✅ 404 error handling works for inventory levels")

    def test_pagination(self):
        """Test pagination functionality"""
        # Test items pagination
        response = requests.get(f"{BASE_URL}/api/inventory/items?page=1&size=5")
        assert response.status_code == 200

        page_data = response.json()
        assert "items" in page_data
        assert "total" in page_data
        assert "page" in page_data
        assert "size" in page_data
        assert "pages" in page_data
        assert page_data["page"] == 1
        assert len(page_data["items"]) <= 5
        print(f"✅ Pagination works: page 1, size 5, total {page_data['total']}")

        # Test warehouses pagination
        response = requests.get(f"{BASE_URL}/api/inventory/warehouses?page=1&size=10")
        assert response.status_code == 200

        warehouse_data = response.json()
        assert "warehouses" in warehouse_data
        assert "total" in warehouse_data
        print(f"✅ Warehouse pagination: total {warehouse_data['total']}")

    def test_search_functionality(self):
        """Test search and filtering"""
        # Test item search by type
        response = requests.get(f"{BASE_URL}/api/inventory/items?item_type=component")
        assert response.status_code == 200

        search_results = response.json()
        print(f"✅ Search by item_type=component: {search_results['total']} results")

        # Test item search by category
        response = requests.get(f"{BASE_URL}/api/inventory/items?category=switches")
        assert response.status_code == 200

        category_results = response.json()
        print(f"✅ Search by category=switches: {category_results['total']} results")

        # Test text search
        response = requests.get(f"{BASE_URL}/api/inventory/items?search=Test")
        assert response.status_code == 200

        text_results = response.json()
        print(f"✅ Text search for 'Test': {text_results['total']} results")
