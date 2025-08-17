"""
Performance and load tests for Inventory API
Tests API performance under various load conditions
"""

import pytest
import time
import concurrent.futures
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestInventoryPerformance:
    """Performance tests for inventory API"""

    def test_warehouse_creation_performance(self, integration_app: TestClient):
        """Test warehouse creation performance"""
        warehouses_to_create = 50
        start_time = time.time()

        created_warehouses = []
        for i in range(warehouses_to_create):
            warehouse_data = {
                "name": f"Performance Warehouse {i}",
                "code": f"PERF-{i:03d}",
                "address": f"{i} Performance St",
                "city": "Performance City",
                "country": "Performance Country",
            }

            response = integration_app.post(
                "/api/inventory/warehouses", json=warehouse_data
            )
            assert response.status_code == 201
            created_warehouses.append(response.json())

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_creation = total_time / warehouses_to_create

        print(f"Created {warehouses_to_create} warehouses in {total_time:.2f}s")
        print(f"Average time per creation: {avg_time_per_creation:.3f}s")

        # Performance assertions
        assert avg_time_per_creation < 0.5  # Should be less than 500ms per creation
        assert total_time < 25  # Should complete all in under 25 seconds

    def test_item_search_performance(self, integration_app: TestClient):
        """Test item search performance with large dataset"""
        # First create a reasonable dataset
        items_to_create = 100

        # Create test items
        for i in range(items_to_create):
            item_data = {
                "sku": f"SEARCH-PERF-{i:04d}",
                "name": f"Search Performance Item {i}",
                "description": f"Performance test item number {i}",
                "item_type": "component" if i % 3 == 0 else "finished_product",
                "category": "switches" if i % 4 == 0 else "keycaps",
                "brand": f"Brand{i % 5}",
                "unit_of_measure": "piece",
                "min_stock_level": 10,
                "unit_cost": 1.0 + (i * 0.01),
                "selling_price": 2.0 + (i * 0.02),
            }
            response = integration_app.post("/api/inventory/items", json=item_data)
            assert response.status_code == 201

        # Test various search scenarios
        search_scenarios = [
            {"params": "", "description": "List all items"},
            {"params": "?search=Performance", "description": "Text search"},
            {"params": "?item_type=component", "description": "Filter by type"},
            {"params": "?category=switches", "description": "Filter by category"},
            {"params": "?brand=Brand1", "description": "Filter by brand"},
            {
                "params": "?search=Item&item_type=component",
                "description": "Combined filters",
            },
            {"params": "?page=1&size=20", "description": "Paginated results"},
        ]

        performance_results = []

        for scenario in search_scenarios:
            start_time = time.time()

            response = integration_app.get(f"/api/inventory/items{scenario['params']}")

            end_time = time.time()
            response_time = end_time - start_time

            assert response.status_code == 200
            results = response.json()

            performance_results.append(
                {
                    "scenario": scenario["description"],
                    "response_time": response_time,
                    "results_count": results["total"],
                }
            )

            print(
                f"{scenario['description']}: {response_time:.3f}s ({results['total']} results)"
            )

            # Performance assertion - searches should be fast
            assert response_time < 2.0  # Should complete in under 2 seconds

        # Overall performance check
        avg_response_time = sum(r["response_time"] for r in performance_results) / len(
            performance_results
        )
        assert avg_response_time < 1.0  # Average should be under 1 second

    def test_concurrent_stock_movements(self, integration_app: TestClient):
        """Test concurrent stock movements for race condition handling"""
        # Create warehouse and item first
        warehouse_data = {
            "name": "Concurrent Test Warehouse",
            "code": "CONCURRENT-001",
            "address": "Concurrent St 1",
            "city": "Test City",
            "country": "Test Country",
        }
        warehouse_response = integration_app.post(
            "/api/inventory/warehouses", json=warehouse_data
        )
        warehouse_id = warehouse_response.json()["id"]

        item_data = {
            "sku": "CONCURRENT-ITEM-001",
            "name": "Concurrent Test Item",
            "item_type": "component",
            "category": "switches",
            "unit_of_measure": "piece",
            "min_stock_level": 10,
            "unit_cost": 1.0,
            "selling_price": 2.0,
        }
        item_response = integration_app.post("/api/inventory/items", json=item_data)
        item_id = item_response.json()["id"]

        # Create initial inventory
        level_data = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "current_quantity": 1000,
            "reserved_quantity": 0,
        }
        integration_app.post("/api/inventory/inventory", json=level_data)

        def perform_stock_movement(movement_id):
            """Perform a single stock movement"""
            movement_data = {
                "item_id": item_id,
                "warehouse_id": warehouse_id,
                "quantity": -1,  # Remove 1 item
                "reason": f"Concurrent test {movement_id}",
                "reference_number": f"CONC-{movement_id:03d}",
            }

            try:
                response = integration_app.post(
                    "/api/inventory/move", json=movement_data
                )
                return {
                    "movement_id": movement_id,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                }
            except Exception as e:
                return {
                    "movement_id": movement_id,
                    "status_code": 500,
                    "success": False,
                    "error": str(e),
                }

        # Perform concurrent movements
        concurrent_movements = 50
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(perform_stock_movement, i)
                for i in range(concurrent_movements)
            ]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        end_time = time.time()
        total_time = end_time - start_time

        # Analyze results
        successful_movements = sum(1 for r in results if r["success"])
        failed_movements = concurrent_movements - successful_movements

        print(f"Concurrent movements completed in {total_time:.2f}s")
        print(f"Successful: {successful_movements}, Failed: {failed_movements}")

        # Check final inventory state
        response = integration_app.get(
            f"/api/inventory/inventory/{item_id}/{warehouse_id}"
        )
        final_level = response.json()
        expected_quantity = 1000 - successful_movements

        print(
            f"Final quantity: {final_level['current_quantity']}, Expected: {expected_quantity}"
        )

        # Assertions
        assert successful_movements > 0  # At least some should succeed
        assert (
            final_level["current_quantity"] == expected_quantity
        )  # Quantity should be consistent
        assert total_time < 30  # Should complete reasonably fast

    def test_reservation_performance(self, integration_app: TestClient):
        """Test reservation/release performance under load"""
        # Setup
        warehouse_data = {
            "name": "Reservation Test Warehouse",
            "code": "RESERVE-001",
            "address": "Reserve St 1",
            "city": "Test City",
            "country": "Test Country",
        }
        warehouse_response = integration_app.post(
            "/api/inventory/warehouses", json=warehouse_data
        )
        warehouse_id = warehouse_response.json()["id"]

        item_data = {
            "sku": "RESERVE-ITEM-001",
            "name": "Reservation Test Item",
            "item_type": "component",
            "category": "switches",
            "unit_of_measure": "piece",
            "min_stock_level": 10,
            "unit_cost": 1.0,
            "selling_price": 2.0,
        }
        item_response = integration_app.post("/api/inventory/items", json=item_data)
        item_id = item_response.json()["id"]

        # Create inventory with enough stock
        level_data = {
            "item_id": item_id,
            "warehouse_id": warehouse_id,
            "current_quantity": 1000,
            "reserved_quantity": 0,
        }
        integration_app.post("/api/inventory/inventory", json=level_data)

        # Test reservation performance
        reservations_to_make = 100
        reservation_quantity = 1

        start_time = time.time()

        # Make reservations
        for i in range(reservations_to_make):
            reserve_params = {
                "item_id": item_id,
                "warehouse_id": warehouse_id,
                "quantity": reservation_quantity,
            }
            response = integration_app.post(
                "/api/inventory/reserve", params=reserve_params
            )
            assert response.status_code == 200

        reservation_time = time.time() - start_time

        # Release reservations
        start_release_time = time.time()

        for i in range(reservations_to_make):
            release_params = {
                "item_id": item_id,
                "warehouse_id": warehouse_id,
                "quantity": reservation_quantity,
            }
            response = integration_app.post(
                "/api/inventory/release", params=release_params
            )
            assert response.status_code == 200

        release_time = time.time() - start_release_time

        total_time = reservation_time + release_time
        avg_reservation_time = reservation_time / reservations_to_make
        avg_release_time = release_time / reservations_to_make

        print("Reservation performance:")
        print(f"  Total reservations: {reservations_to_make}")
        print(
            f"  Reservation time: {reservation_time:.2f}s ({avg_reservation_time:.3f}s avg)"
        )
        print(f"  Release time: {release_time:.2f}s ({avg_release_time:.3f}s avg)")
        print(f"  Total time: {total_time:.2f}s")

        # Performance assertions
        assert avg_reservation_time < 0.1  # Should be fast
        assert avg_release_time < 0.1  # Should be fast
        assert total_time < 20  # Should complete in reasonable time

        # Verify final state
        response = integration_app.get(
            f"/api/inventory/inventory/{item_id}/{warehouse_id}"
        )
        final_level = response.json()
        assert final_level["current_quantity"] == 1000  # Unchanged
        assert final_level["reserved_quantity"] == 0  # All released
        assert final_level["available_quantity"] == 1000  # Back to original

    def test_analytics_performance(self, integration_app: TestClient):
        """Test analytics endpoints performance with large dataset"""
        # Create test data - multiple warehouses and items
        warehouses = []
        items = []

        # Create warehouses
        for i in range(10):
            warehouse_data = {
                "name": f"Analytics Warehouse {i}",
                "code": f"ANALYTICS-{i:02d}",
                "address": f"{i} Analytics St",
                "city": "Analytics City",
                "country": "Analytics Country",
            }
            response = integration_app.post(
                "/api/inventory/warehouses", json=warehouse_data
            )
            warehouses.append(response.json())

        # Create items
        for i in range(200):
            item_data = {
                "sku": f"ANALYTICS-ITEM-{i:04d}",
                "name": f"Analytics Item {i}",
                "item_type": "component" if i % 3 == 0 else "finished_product",
                "category": "switches" if i % 4 == 0 else "keycaps",
                "unit_of_measure": "piece",
                "min_stock_level": 50 if i % 5 == 0 else 10,  # Some will be low stock
                "unit_cost": 1.0 + (i * 0.01),
                "selling_price": 2.0 + (i * 0.02),
            }
            response = integration_app.post("/api/inventory/items", json=item_data)
            items.append(response.json())

        # Create inventory levels (some low stock)
        for item in items[:100]:  # Only for first 100 items
            for warehouse in warehouses[:5]:  # Only for first 5 warehouses
                current_qty = (
                    5 if item["min_stock_level"] == 50 else 100
                )  # Create low stock
                level_data = {
                    "item_id": item["id"],
                    "warehouse_id": warehouse["id"],
                    "current_quantity": current_qty,
                    "reserved_quantity": 0,
                }
                integration_app.post("/api/inventory/inventory", json=level_data)

        # Test analytics performance
        analytics_tests = [
            {
                "endpoint": "/api/inventory/analytics/summary",
                "description": "Overall summary",
            },
            {
                "endpoint": f"/api/inventory/analytics/summary?warehouse_id={warehouses[0]['id']}",
                "description": "Warehouse-specific summary",
            },
            {
                "endpoint": "/api/inventory/analytics/low-stock",
                "description": "Low stock analysis",
            },
            {
                "endpoint": f"/api/inventory/analytics/low-stock?warehouse_id={warehouses[0]['id']}",
                "description": "Warehouse-specific low stock",
            },
        ]

        for test in analytics_tests:
            start_time = time.time()

            response = integration_app.get(test["endpoint"])

            end_time = time.time()
            response_time = end_time - start_time

            assert response.status_code == 200

            print(f"{test['description']}: {response_time:.3f}s")

            # Analytics should be reasonably fast even with large datasets
            assert response_time < 5.0  # Should complete in under 5 seconds
