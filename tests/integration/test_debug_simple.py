"""
Debug test for simple warehouse creation
"""

import pytest
import requests
import json


BASE_URL = "http://localhost:8001"


@pytest.mark.integration
def test_debug_warehouse_simple():
    """Test debug warehouse creation endpoint"""
    response = requests.post(f"{BASE_URL}/api/inventory/debug/warehouse")
    
    print(f"Status code: {response.status_code}")
    print(f"Response content: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response JSON: {json.dumps(data, indent=2)}")
            
            if data.get("status") == "success":
                warehouse = data.get("warehouse", {})
                print(f"Warehouse created successfully!")
                print(f"ID: {warehouse.get('id')}")
                print(f"Name: {warehouse.get('name')}")
                print(f"Code: {warehouse.get('code')}")
            else:
                print(f"Error: {data.get('error')}")
                print(f"Error type: {data.get('type')}")
        except:
            print("Could not parse JSON response")
    
    assert response.status_code == 200
