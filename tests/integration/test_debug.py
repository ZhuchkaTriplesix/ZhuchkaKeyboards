"""
Debug test to see what's happening with API
"""

import pytest
import requests
import json
import uuid


BASE_URL = "http://localhost:8001"


@pytest.mark.integration
def test_debug_warehouse_creation():
    """Debug warehouse creation"""
    warehouse_data = {
        "name": "Debug Test Warehouse",
        "code": f"DEBUG-{uuid.uuid4().hex[:8].upper()}",
        "description": "Created by debug test",
        "address": "123 Debug St",
        "city": "Debug City",
        "postal_code": "12345",
        "country": "Debug Country",
        "contact_person": "Debug Manager",
        "phone": "+1-555-0123",
        "email": "debug@test.com",
        "is_active": True,
    }

    print(f"Sending warehouse data: {json.dumps(warehouse_data, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/api/inventory/warehouses", json=warehouse_data
    )

    print(f"Status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response content: {response.text}")

    if response.status_code != 201:
        try:
            error_data = response.json()
            print(f"Error JSON: {json.dumps(error_data, indent=2)}")
        except:
            print("Could not parse error as JSON")


@pytest.mark.integration
def test_debug_item_creation():
    """Debug item creation"""
    item_data = {
        "sku": f"DEBUG-{uuid.uuid4().hex[:8].upper()}",
        "name": "Debug Test Item",
        "description": "Debug test item",
        "item_type": "component",
        "category": "switches",
        "brand": "DebugBrand",
        "model": "DebugModel",
        "unit_of_measure": "piece",
        "weight_kg": 0.01,
        "dimensions": "10x10x10 mm",
        "min_stock_level": 10,
        "max_stock_level": 100,
        "unit_cost": 1.0,
        "selling_price": 2.0,
        "is_active": True,
        "is_tracked": True,
    }

    print(f"Sending item data: {json.dumps(item_data, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/inventory/items", json=item_data)

    print(f"Status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response content: {response.text}")

    if response.status_code != 201:
        try:
            error_data = response.json()
            print(f"Error JSON: {json.dumps(error_data, indent=2)}")
        except:
            print("Could not parse error as JSON")


@pytest.mark.integration
def test_debug_endpoints_exist():
    """Check which endpoints exist"""
    endpoints_to_check = [
        "/api/inventory/warehouses",
        "/api/inventory/items",
        "/api/inventory/inventory",
        "/api/inventory/analytics/summary",
        "/docs",
    ]

    for endpoint in endpoints_to_check:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"GET {endpoint}: {response.status_code}")

            if endpoint == "/docs":
                print(f"  Content length: {len(response.content)}")
            elif response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"  List length: {len(data)}")
                except:
                    print("  Could not parse JSON")
        except Exception as e:
            print(f"GET {endpoint}: ERROR - {e}")


@pytest.mark.integration
def test_debug_options_request():
    """Check if CORS/OPTIONS works"""
    response = requests.options(f"{BASE_URL}/api/inventory/warehouses")
    print(f"OPTIONS /api/inventory/warehouses: {response.status_code}")
    print(f"Allow header: {response.headers.get('Allow', 'Not present')}")
    print(f"All headers: {dict(response.headers)}")
