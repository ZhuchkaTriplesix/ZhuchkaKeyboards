"""
Script to load massive realistic test data into the API
Creates thousands of records for performance testing
"""

import asyncio
import aiohttp
import json
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any, Optional

from tests.performance.data_generators import (
    generate_small_dataset, 
    generate_medium_dataset, 
    generate_large_dataset
)


BASE_URL = "http://localhost:8001"


class TestDataLoader:
    """Loads massive amounts of test data into the API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.loaded_resources = {
            "warehouses": [],
            "items": [],
            "suppliers": []
        }
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_time": 0,
            "errors": []
        }
    
    async def test_api_connection(self) -> bool:
        """Test if API is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health") as response:
                    if response.status == 200:
                        print("✅ API connection successful")
                        return True
                    else:
                        print(f"❌ API returned status {response.status}")
                        return False
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False
    
    async def load_warehouses(self, warehouses_data: List[Dict[str, Any]], 
                             batch_size: int = 10, delay_between_batches: float = 0.5) -> List[Dict]:
        """Load warehouses in batches"""
        print(f"📦 Loading {len(warehouses_data)} warehouses in batches of {batch_size}...")
        
        connector = aiohttp.TCPConnector(limit=batch_size*2, limit_per_host=batch_size*2)
        timeout = aiohttp.ClientTimeout(total=30)
        loaded_warehouses = []
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i in range(0, len(warehouses_data), batch_size):
                batch = warehouses_data[i:i+batch_size]
                batch_start = time.time()
                
                print(f"  Batch {i//batch_size + 1}/{(len(warehouses_data)-1)//batch_size + 1}: {len(batch)} warehouses")
                
                tasks = []
                for warehouse in batch:
                    task = self._create_warehouse(session, warehouse)
                    tasks.append(task)
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                batch_end = time.time()
                
                # Обработка результатов batch
                successful_in_batch = 0
                for result in batch_results:
                    self.stats["total_requests"] += 1
                    
                    if isinstance(result, dict) and result.get("success"):
                        successful_in_batch += 1
                        self.stats["successful_requests"] += 1
                        loaded_warehouses.append(result["data"])
                        self.loaded_resources["warehouses"].append(result["data"])
                    else:
                        self.stats["failed_requests"] += 1
                        if isinstance(result, dict):
                            self.stats["errors"].append(f"Warehouse: {result.get('error', 'Unknown error')}")
                        else:
                            self.stats["errors"].append(f"Warehouse: {str(result)}")
                
                batch_time = batch_end - batch_start
                batch_rps = len(batch) / batch_time if batch_time > 0 else 0
                
                print(f"    ✅ {successful_in_batch}/{len(batch)} successful, {batch_rps:.1f} RPS")
                
                # Пауза между батчами
                if delay_between_batches > 0:
                    await asyncio.sleep(delay_between_batches)
        
        print(f"📦 Warehouses loading complete: {len(loaded_warehouses)}/{len(warehouses_data)} loaded")
        return loaded_warehouses
    
    async def load_items(self, items_data: List[Dict[str, Any]], 
                        batch_size: int = 20, delay_between_batches: float = 0.3) -> List[Dict]:
        """Load items in batches"""
        print(f"🔧 Loading {len(items_data)} items in batches of {batch_size}...")
        
        connector = aiohttp.TCPConnector(limit=batch_size*2, limit_per_host=batch_size*2)
        timeout = aiohttp.ClientTimeout(total=30)
        loaded_items = []
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i in range(0, len(items_data), batch_size):
                batch = items_data[i:i+batch_size]
                batch_start = time.time()
                
                print(f"  Batch {i//batch_size + 1}/{(len(items_data)-1)//batch_size + 1}: {len(batch)} items")
                
                tasks = []
                for item in batch:
                    task = self._create_item(session, item)
                    tasks.append(task)
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                batch_end = time.time()
                
                # Обработка результатов batch
                successful_in_batch = 0
                for result in batch_results:
                    self.stats["total_requests"] += 1
                    
                    if isinstance(result, dict) and result.get("success"):
                        successful_in_batch += 1
                        self.stats["successful_requests"] += 1
                        loaded_items.append(result["data"])
                        self.loaded_resources["items"].append(result["data"])
                    else:
                        self.stats["failed_requests"] += 1
                        if isinstance(result, dict):
                            self.stats["errors"].append(f"Item: {result.get('error', 'Unknown error')}")
                        else:
                            self.stats["errors"].append(f"Item: {str(result)}")
                
                batch_time = batch_end - batch_start
                batch_rps = len(batch) / batch_time if batch_time > 0 else 0
                
                print(f"    ✅ {successful_in_batch}/{len(batch)} successful, {batch_rps:.1f} RPS")
                
                # Пауза между батчами
                if delay_between_batches > 0:
                    await asyncio.sleep(delay_between_batches)
        
        print(f"🔧 Items loading complete: {len(loaded_items)}/{len(items_data)} loaded")
        return loaded_items
    
    async def _create_warehouse(self, session: aiohttp.ClientSession, warehouse_data: Dict) -> Dict:
        """Create a single warehouse"""
        try:
            async with session.post(
                f"{self.base_url}/api/inventory/warehouses",
                json=warehouse_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if 200 <= response.status < 300:
                    data = await response.json()
                    return {"success": True, "data": data}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Status {response.status}: {error_text[:200]}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_item(self, session: aiohttp.ClientSession, item_data: Dict) -> Dict:
        """Create a single item"""
        try:
            async with session.post(
                f"{self.base_url}/api/inventory/items",
                json=item_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if 200 <= response.status < 300:
                    data = await response.json()
                    return {"success": True, "data": data}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Status {response.status}: {error_text[:200]}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def verify_loaded_data(self) -> Dict[str, Any]:
        """Verify that data was loaded correctly"""
        print("\n🔍 Verifying loaded data...")
        
        verification_results = {}
        
        async with aiohttp.ClientSession() as session:
            # Проверяем warehouses
            async with session.get(f"{self.base_url}/api/inventory/warehouses") as response:
                if response.status == 200:
                    data = await response.json()
                    warehouses_count = len(data) if isinstance(data, list) else data.get("total", 0)
                    verification_results["warehouses"] = {
                        "api_count": warehouses_count,
                        "loaded_count": len(self.loaded_resources["warehouses"]),
                        "status": "✅" if warehouses_count > 0 else "❌"
                    }
                else:
                    verification_results["warehouses"] = {"status": "❌", "error": f"Status {response.status}"}
            
            # Проверяем items
            async with session.get(f"{self.base_url}/api/inventory/items") as response:
                if response.status == 200:
                    data = await response.json()
                    items_count = len(data) if isinstance(data, list) else data.get("total", 0)
                    verification_results["items"] = {
                        "api_count": items_count,
                        "loaded_count": len(self.loaded_resources["items"]),
                        "status": "✅" if items_count > 0 else "❌"
                    }
                else:
                    verification_results["items"] = {"status": "❌", "error": f"Status {response.status}"}
        
        # Печатаем результаты
        for resource_type, result in verification_results.items():
            print(f"  {result['status']} {resource_type.title()}:")
            if "api_count" in result:
                print(f"    API count: {result['api_count']}")
                print(f"    Loaded count: {result['loaded_count']}")
            elif "error" in result:
                print(f"    Error: {result['error']}")
        
        return verification_results
    
    def print_final_stats(self):
        """Print final loading statistics"""
        print(f"\n📊 FINAL LOADING STATISTICS")
        print(f"=" * 50)
        print(f"Total requests: {self.stats['total_requests']}")
        print(f"Successful: {self.stats['successful_requests']}")
        print(f"Failed: {self.stats['failed_requests']}")
        
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
            print(f"Success rate: {success_rate:.2f}%")
        
        print(f"\nLoaded resources:")
        print(f"  Warehouses: {len(self.loaded_resources['warehouses'])}")
        print(f"  Items: {len(self.loaded_resources['items'])}")
        
        if self.stats['errors']:
            print(f"\nFirst 5 errors:")
            for i, error in enumerate(self.stats['errors'][:5]):
                print(f"  {i+1}. {error}")
            
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more errors")


async def load_small_dataset():
    """Load small dataset for quick testing"""
    print("🔧 Loading SMALL dataset...")
    
    loader = TestDataLoader()
    
    if not await loader.test_api_connection():
        print("❌ Cannot connect to API")
        return
    
    # Генерируем данные
    generator = generate_small_dataset()
    warehouses = generator.generate_warehouses()
    items = generator.generate_items()
    
    print(f"Generated: {len(warehouses)} warehouses, {len(items)} items")
    
    start_time = time.time()
    
    # Загружаем данные
    await loader.load_warehouses(warehouses, batch_size=5, delay_between_batches=0.2)
    await loader.load_items(items[:50], batch_size=10, delay_between_batches=0.2)  # Только 50 items для small
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Проверяем
    await loader.verify_loaded_data()
    
    print(f"⏱️  Total loading time: {total_time:.2f}s")
    loader.print_final_stats()


async def load_medium_dataset():
    """Load medium dataset for moderate testing"""
    print("🏭 Loading MEDIUM dataset...")
    
    loader = TestDataLoader()
    
    if not await loader.test_api_connection():
        print("❌ Cannot connect to API")
        return
    
    # Генерируем данные
    generator = generate_medium_dataset()
    warehouses = generator.generate_warehouses()
    items = generator.generate_items()
    
    print(f"Generated: {len(warehouses)} warehouses, {len(items)} items")
    
    start_time = time.time()
    
    # Загружаем данные с большими batch size
    await loader.load_warehouses(warehouses, batch_size=10, delay_between_batches=0.3)
    await loader.load_items(items[:500], batch_size=20, delay_between_batches=0.2)  # 500 items для medium
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Проверяем
    await loader.verify_loaded_data()
    
    print(f"⏱️  Total loading time: {total_time:.2f}s")
    loader.print_final_stats()


async def load_large_dataset():
    """Load large dataset for stress testing"""
    print("🚀 Loading LARGE dataset...")
    
    loader = TestDataLoader()
    
    if not await loader.test_api_connection():
        print("❌ Cannot connect to API")
        return
    
    # Генерируем данные
    generator = generate_large_dataset()
    warehouses = generator.generate_warehouses()
    items = generator.generate_items()
    
    print(f"Generated: {len(warehouses)} warehouses, {len(items)} items")
    print(f"WARNING: This will create {len(warehouses)} + {len(items)} records!")
    
    start_time = time.time()
    
    # Загружаем данные с оптимальными batch sizes
    await loader.load_warehouses(warehouses, batch_size=15, delay_between_batches=0.1)
    await loader.load_items(items[:2000], batch_size=30, delay_between_batches=0.1)  # 2000 items для large
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Проверяем
    await loader.verify_loaded_data()
    
    print(f"⏱️  Total loading time: {total_time:.2f}s")
    loader.print_final_stats()
    
    # Рассчитываем производительность загрузки
    total_records = len(loader.loaded_resources["warehouses"]) + len(loader.loaded_resources["items"])
    if total_time > 0:
        loading_rps = total_records / total_time
        print(f"📈 Loading performance: {loading_rps:.2f} records/second")


async def stress_test_loading():
    """Stress test the loading process"""
    print("💥 STRESS TEST: Loading data as fast as possible...")
    
    loader = TestDataLoader()
    
    if not await loader.test_api_connection():
        print("❌ Cannot connect to API")
        return
    
    # Генерируем данные для stress test
    generator = generate_medium_dataset()
    warehouses = generator.generate_warehouses()[:30]  # 30 warehouses
    items = generator.generate_items()[:200]  # 200 items
    
    print(f"Stress testing with: {len(warehouses)} warehouses, {len(items)} items")
    print("Using aggressive batching and minimal delays...")
    
    start_time = time.time()
    
    # Агрессивные настройки
    await loader.load_warehouses(warehouses, batch_size=20, delay_between_batches=0.05)
    await loader.load_items(items, batch_size=50, delay_between_batches=0.05)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    await loader.verify_loaded_data()
    
    print(f"⏱️  Stress test time: {total_time:.2f}s")
    loader.print_final_stats()
    
    # Анализ stress performance
    total_records = len(loader.loaded_resources["warehouses"]) + len(loader.loaded_resources["items"])
    if total_time > 0:
        stress_rps = total_records / total_time
        print(f"💥 Stress loading RPS: {stress_rps:.2f} records/second")
        
        if stress_rps > 10:
            print("🟢 Excellent loading performance!")
        elif stress_rps > 5:
            print("🟡 Good loading performance")
        elif stress_rps > 2:
            print("🟠 Moderate loading performance")
        else:
            print("🔴 Slow loading performance - needs optimization")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load test data into API")
    parser.add_argument("--size", choices=["small", "medium", "large", "stress"], 
                       default="small", help="Dataset size to load")
    
    args = parser.parse_args()
    
    if args.size == "small":
        asyncio.run(load_small_dataset())
    elif args.size == "medium":
        asyncio.run(load_medium_dataset())
    elif args.size == "large":
        asyncio.run(load_large_dataset())
    elif args.size == "stress":
        asyncio.run(stress_test_loading())
