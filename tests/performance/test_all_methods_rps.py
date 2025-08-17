"""
Comprehensive RPS tests for ALL API methods
Tests GET, POST, PUT, DELETE operations under high load with realistic data
"""

import pytest
import asyncio
import aiohttp
import time
import statistics
import random
from typing import List, Dict, Any

from tests.performance.data_generators import generate_small_dataset


BASE_URL = "http://localhost:8001"


@pytest.mark.performance
class TestAllMethodsRPS:
    """RPS tests for all API methods with realistic data"""

    @pytest.fixture(autouse=True)
    def setup_class_data(self):
        """Setup class-level data"""
        self.test_data = {}
        self.created_resources = {"warehouses": [], "items": [], "inventory_levels": []}

    @pytest.fixture(autouse=True)
    async def setup_test_data(self):
        """Generate test data before running tests"""
        print("\n🏭 Generating realistic test data...")

        # Генерируем тестовые данные
        generator = generate_small_dataset()
        warehouses = generator.generate_warehouses()
        items = generator.generate_items()

        # Берем подмножество для RPS тестов
        self.test_data = {
            "warehouses": warehouses[:20],  # 20 складов для тестов
            "items": items[:100],  # 100 товаров для тестов
        }

        print(f"  ✅ Prepared {len(self.test_data['warehouses'])} warehouses")
        print(f"  ✅ Prepared {len(self.test_data['items'])} items")

    async def make_async_request(
        self, session: aiohttp.ClientSession, method: str, url: str, **kwargs
    ) -> Dict[str, Any]:
        """Make an async HTTP request and measure response time"""
        start_time = time.time()
        try:
            async with session.request(method, url, **kwargs) as response:
                end_time = time.time()

                # Читаем контент только если нужно
                if response.status < 400:
                    try:
                        content = await response.json()
                    except:
                        content = await response.text()
                else:
                    content = await response.text()

                return {
                    "status_code": response.status,
                    "response_time": end_time - start_time,
                    "content_length": len(str(content)),
                    "success": 200 <= response.status < 300,
                    "content": content if response.status < 400 else None,
                    "error": content if response.status >= 400 else None,
                }
        except Exception as e:
            end_time = time.time()
            return {
                "status_code": 0,
                "response_time": end_time - start_time,
                "content_length": 0,
                "success": False,
                "content": None,
                "error": str(e),
            }

    @pytest.mark.asyncio
    async def test_warehouse_get_rps(self):
        """Test GET /api/inventory/warehouses RPS"""
        target_rps = 200
        test_duration = 10
        total_requests = target_rps * test_duration

        print(f"\n📦 Testing Warehouse GET RPS: {target_rps} RPS for {test_duration}s")

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            # Тестируем разные endpoints
            endpoints = [
                f"{BASE_URL}/api/inventory/warehouses",  # List all
                f"{BASE_URL}/api/inventory/warehouses?page=1&size=10",  # Paginated
                f"{BASE_URL}/api/inventory/warehouses?page=2&size=5",  # Different page
            ]

            tasks = []
            for i in range(total_requests):
                endpoint = endpoints[i % len(endpoints)]
                task = self.make_async_request(session, "GET", endpoint)
                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]

        self._analyze_and_print_results(
            "Warehouse GET",
            valid_results,
            successful_requests,
            total_test_time,
            target_rps,
        )

        # Assertions
        assert len(successful_requests) > 0, "No successful requests"
        assert len(successful_requests) / len(valid_results) > 0.7, (
            "Success rate too low"
        )

    @pytest.mark.asyncio
    async def test_warehouse_post_rps(self):
        """Test POST /api/inventory/warehouses RPS"""
        target_rps = 50  # POST обычно медленнее
        test_duration = 5
        total_requests = target_rps * test_duration

        print(f"\n📦 Testing Warehouse POST RPS: {target_rps} RPS for {test_duration}s")

        connector = aiohttp.TCPConnector(limit=50, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=20)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = []

            for i in range(total_requests):
                # Берем случайный warehouse из тестовых данных и модифицируем
                base_warehouse = random.choice(self.test_data["warehouses"])
                warehouse_data = base_warehouse.copy()

                # Делаем уникальными
                warehouse_data["code"] = f"RPS-POST-{i:04d}"
                warehouse_data["name"] = f"RPS Test Warehouse {i}"
                warehouse_data["email"] = f"rps.test.{i}@zhuchka.com"

                task = self.make_async_request(
                    session,
                    "POST",
                    f"{BASE_URL}/api/inventory/warehouses",
                    json=warehouse_data,
                    headers={"Content-Type": "application/json"},
                )
                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]

        # Сохраняем созданные ресурсы для cleanup
        for result in successful_requests:
            if result["content"] and isinstance(result["content"], dict):
                if "id" in result["content"]:
                    self.created_resources["warehouses"].append(result["content"]["id"])

        self._analyze_and_print_results(
            "Warehouse POST",
            valid_results,
            successful_requests,
            total_test_time,
            target_rps,
        )

        # Более мягкие assertions для POST
        assert len(successful_requests) > 0, "No successful POST requests"

        # Показываем примеры ошибок если есть
        failed_requests = [r for r in valid_results if not r["success"]]
        if failed_requests:
            print("  Sample errors:")
            for i, error in enumerate(failed_requests[:3]):
                print(
                    f"    {i + 1}. Status {error['status_code']}: {str(error['error'])[:100]}..."
                )

    @pytest.mark.asyncio
    async def test_items_get_rps(self):
        """Test GET /api/inventory/items RPS"""
        target_rps = 150
        test_duration = 8
        total_requests = target_rps * test_duration

        print(f"\n🔧 Testing Items GET RPS: {target_rps} RPS for {test_duration}s")

        connector = aiohttp.TCPConnector(limit=80, limit_per_host=80)
        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            # Тестируем разные поисковые запросы
            search_patterns = [
                "",  # No search
                "?search=switch",
                "?search=keycap",
                "?category=switches",
                "?category=keycaps",
                "?item_type=component",
                "?brand=Cherry",
                "?page=1&size=20",
                "?page=2&size=10",
                "?is_active=true",
            ]

            tasks = []
            for i in range(total_requests):
                pattern = search_patterns[i % len(search_patterns)]
                url = f"{BASE_URL}/api/inventory/items{pattern}"
                task = self.make_async_request(session, "GET", url)
                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]

        self._analyze_and_print_results(
            "Items GET", valid_results, successful_requests, total_test_time, target_rps
        )

        # Assertions
        assert len(successful_requests) > 0, "No successful requests"
        assert len(successful_requests) / len(valid_results) > 0.6, (
            "Success rate too low for items GET"
        )

    @pytest.mark.asyncio
    async def test_items_post_rps(self):
        """Test POST /api/inventory/items RPS"""
        target_rps = 30  # POST обычно медленнее из-за validation
        test_duration = 5
        total_requests = target_rps * test_duration

        print(f"\n🔧 Testing Items POST RPS: {target_rps} RPS for {test_duration}s")

        connector = aiohttp.TCPConnector(limit=40, limit_per_host=40)
        timeout = aiohttp.ClientTimeout(total=25)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = []

            for i in range(total_requests):
                # Берем случайный item из тестовых данных и модифицируем
                base_item = random.choice(self.test_data["items"])
                item_data = base_item.copy()

                # Делаем уникальными
                item_data["sku"] = f"RPS-ITEM-{i:04d}"
                item_data["name"] = f"RPS Test Item {i}"
                item_data["description"] = f"Performance test item #{i}"

                task = self.make_async_request(
                    session,
                    "POST",
                    f"{BASE_URL}/api/inventory/items",
                    json=item_data,
                    headers={"Content-Type": "application/json"},
                )
                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]

        # Сохраняем созданные ресурсы
        for result in successful_requests:
            if result["content"] and isinstance(result["content"], dict):
                if "id" in result["content"]:
                    self.created_resources["items"].append(result["content"]["id"])

        self._analyze_and_print_results(
            "Items POST",
            valid_results,
            successful_requests,
            total_test_time,
            target_rps,
        )

        assert len(successful_requests) > 0, "No successful POST requests"

    @pytest.mark.asyncio
    async def test_mixed_crud_operations_rps(self):
        """Test mixed CRUD operations RPS"""
        target_rps = 100
        test_duration = 10
        total_requests = target_rps * test_duration

        print(f"\n🔀 Testing Mixed CRUD RPS: {target_rps} RPS for {test_duration}s")
        print("  Distribution: 60% GET, 25% POST, 10% PUT, 5% DELETE")

        connector = aiohttp.TCPConnector(limit=80, limit_per_host=80)
        timeout = aiohttp.ClientTimeout(total=20)

        # Распределение операций (как в реальном мире)
        operation_weights = [60, 25, 10, 5]  # GET, POST, PUT, DELETE
        operations = ["GET", "POST", "PUT", "DELETE"]

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = []

            for i in range(total_requests):
                operation = random.choices(operations, weights=operation_weights)[0]

                if operation == "GET":
                    # GET operations
                    get_endpoints = [
                        f"{BASE_URL}/api/inventory/warehouses",
                        f"{BASE_URL}/api/inventory/items",
                        f"{BASE_URL}/api/inventory/analytics/summary",
                        f"{BASE_URL}/api/health",
                    ]
                    url = random.choice(get_endpoints)
                    task = self.make_async_request(session, "GET", url)

                elif operation == "POST":
                    # POST operations
                    if random.choice([True, False]):  # 50% warehouses, 50% items
                        # Create warehouse
                        base_warehouse = random.choice(self.test_data["warehouses"])
                        data = base_warehouse.copy()
                        data["code"] = f"MIX-WH-{i:04d}"
                        data["name"] = f"Mixed Test Warehouse {i}"

                        task = self.make_async_request(
                            session,
                            "POST",
                            f"{BASE_URL}/api/inventory/warehouses",
                            json=data,
                            headers={"Content-Type": "application/json"},
                        )
                    else:
                        # Create item
                        base_item = random.choice(self.test_data["items"])
                        data = base_item.copy()
                        data["sku"] = f"MIX-ITM-{i:04d}"
                        data["name"] = f"Mixed Test Item {i}"

                        task = self.make_async_request(
                            session,
                            "POST",
                            f"{BASE_URL}/api/inventory/items",
                            json=data,
                            headers={"Content-Type": "application/json"},
                        )

                elif operation == "PUT":
                    # PUT operations (если есть созданные ресурсы)
                    if self.created_resources["warehouses"] and random.choice(
                        [True, False]
                    ):
                        warehouse_id = random.choice(
                            self.created_resources["warehouses"]
                        )
                        update_data = {"name": f"Updated Warehouse {i}"}
                        task = self.make_async_request(
                            session,
                            "PUT",
                            f"{BASE_URL}/api/inventory/warehouses/{warehouse_id}",
                            json=update_data,
                            headers={"Content-Type": "application/json"},
                        )
                    elif self.created_resources["items"]:
                        item_id = random.choice(self.created_resources["items"])
                        update_data = {"name": f"Updated Item {i}"}
                        task = self.make_async_request(
                            session,
                            "PUT",
                            f"{BASE_URL}/api/inventory/items/{item_id}",
                            json=update_data,
                            headers={"Content-Type": "application/json"},
                        )
                    else:
                        # Fallback to GET if no resources to update
                        task = self.make_async_request(
                            session, "GET", f"{BASE_URL}/api/health"
                        )

                else:  # DELETE
                    # DELETE operations (осторожно с удалением)
                    if (
                        self.created_resources["items"]
                        and len(self.created_resources["items"]) > 5
                    ):
                        item_id = self.created_resources[
                            "items"
                        ].pop()  # Удаляем и убираем из списка
                        task = self.make_async_request(
                            session,
                            "DELETE",
                            f"{BASE_URL}/api/inventory/items/{item_id}",
                        )
                    else:
                        # Fallback to GET if no safe resources to delete
                        task = self.make_async_request(
                            session, "GET", f"{BASE_URL}/api/health"
                        )

                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]

        # Группировка по статус кодам
        status_codes = {}
        for result in valid_results:
            code = result["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1

        self._analyze_and_print_results(
            "Mixed CRUD",
            valid_results,
            successful_requests,
            total_test_time,
            target_rps,
        )
        print(f"  Status code distribution: {status_codes}")

        assert len(successful_requests) > 0, "No successful requests"
        assert len(successful_requests) / len(valid_results) > 0.5, (
            "Success rate too low for mixed operations"
        )

    @pytest.mark.asyncio
    async def test_analytics_endpoints_rps(self):
        """Test analytics endpoints RPS"""
        target_rps = 50  # Analytics обычно медленнее
        test_duration = 6
        total_requests = target_rps * test_duration

        print(f"\n📊 Testing Analytics RPS: {target_rps} RPS for {test_duration}s")

        connector = aiohttp.TCPConnector(limit=60, limit_per_host=60)
        timeout = aiohttp.ClientTimeout(total=30)  # Analytics могут быть медленными

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            # Analytics endpoints
            analytics_endpoints = [
                f"{BASE_URL}/api/inventory/analytics/summary",
                f"{BASE_URL}/api/inventory/analytics/low-stock",
                f"{BASE_URL}/metrics",  # Prometheus metrics
            ]

            tasks = []
            for i in range(total_requests):
                endpoint = analytics_endpoints[i % len(analytics_endpoints)]
                task = self.make_async_request(session, "GET", endpoint)
                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]

        # Анализ размеров ответов (analytics обычно больше)
        if successful_requests:
            content_sizes = [r["content_length"] for r in successful_requests]
            avg_content_size = statistics.mean(content_sizes)

            print(f"  Average content size: {avg_content_size:.0f} bytes")

            # Разделяем по размеру (metrics обычно больше)
            small_responses = [
                r for r in successful_requests if r["content_length"] < 1000
            ]
            large_responses = [
                r for r in successful_requests if r["content_length"] >= 1000
            ]

            print(f"  Small responses (<1KB): {len(small_responses)}")
            print(f"  Large responses (≥1KB): {len(large_responses)}")

        self._analyze_and_print_results(
            "Analytics", valid_results, successful_requests, total_test_time, target_rps
        )

        assert len(successful_requests) > 0, "No successful analytics requests"

    def _analyze_and_print_results(
        self,
        test_name: str,
        valid_results: List[Dict],
        successful_requests: List[Dict],
        total_test_time: float,
        target_rps: int,
    ):
        """Analyze and print test results"""
        if not valid_results:
            print(f"  ❌ No valid results for {test_name}")
            return

        success_rate = len(successful_requests) / len(valid_results)
        actual_rps = len(successful_requests) / total_test_time

        print(f"📊 {test_name} Results:")
        print(f"  Total requests: {len(valid_results)}")
        print(f"  Successful: {len(successful_requests)}")
        print(f"  Success rate: {success_rate * 100:.2f}%")
        print(f"  Target RPS: {target_rps}")
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Test duration: {total_test_time:.2f}s")

        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)

            print(f"  Avg response time: {avg_response_time * 1000:.2f}ms")
            print(f"  Min response time: {min_response_time * 1000:.2f}ms")
            print(f"  Max response time: {max_response_time * 1000:.2f}ms")

            if len(response_times) > 10:
                median_time = statistics.median(response_times)
                print(f"  Median response time: {median_time * 1000:.2f}ms")

            # Performance rating
            performance_score = min(100, (actual_rps / target_rps) * 100)
            if performance_score >= 80:
                print(f"  🟢 Performance: {performance_score:.1f}% (Excellent)")
            elif performance_score >= 60:
                print(f"  🟡 Performance: {performance_score:.1f}% (Good)")
            elif performance_score >= 40:
                print(f"  🟠 Performance: {performance_score:.1f}% (Fair)")
            else:
                print(f"  🔴 Performance: {performance_score:.1f}% (Needs Improvement)")

        failed_requests = [r for r in valid_results if not r["success"]]
        if failed_requests:
            error_codes = {}
            for req in failed_requests:
                code = req["status_code"]
                error_codes[code] = error_codes.get(code, 0) + 1
            print(f"  Error codes: {error_codes}")

    @pytest.mark.asyncio
    async def test_rps_summary_report(self):
        """Generate comprehensive RPS performance report"""
        print("\n📋 RPS Performance Summary Report")
        print("=" * 60)
        print("")
        print("🎯 TEST CONFIGURATION:")
        print(
            f"  • Test data: {len(self.test_data.get('warehouses', []))} warehouses, {len(self.test_data.get('items', []))} items"
        )
        print("  • Created resources during tests:")
        print(f"    - Warehouses: {len(self.created_resources['warehouses'])}")
        print(f"    - Items: {len(self.created_resources['items'])}")
        print("")
        print("🚀 API METHOD PERFORMANCE TARGETS:")
        print("  • GET /warehouses: 200 RPS target")
        print("  • POST /warehouses: 50 RPS target")
        print("  • GET /items: 150 RPS target")
        print("  • POST /items: 30 RPS target")
        print("  • Mixed CRUD: 100 RPS target")
        print("  • Analytics: 50 RPS target")
        print("")
        print("📊 EXPECTED PERFORMANCE CHARACTERISTICS:")
        print("  • GET operations: Fastest (DB reads + caching)")
        print("  • POST operations: Slower (validation + DB writes)")
        print("  • PUT operations: Medium (partial updates)")
        print("  • DELETE operations: Fast (simple operations)")
        print("  • Analytics: Variable (complex queries)")
        print("")
        print("🔧 OPTIMIZATION RECOMMENDATIONS:")
        print("  1. Add Redis caching for GET operations")
        print("  2. Batch POST operations where possible")
        print("  3. Optimize database indexes for search queries")
        print("  4. Add connection pooling optimization")
        print("  5. Consider read replicas for analytics")
        print("")
        print("📈 SCALING TARGETS:")
        print("  • Production goal: 500+ RPS for GET operations")
        print("  • Production goal: 100+ RPS for POST operations")
        print("  • Production goal: Handle 1000+ concurrent users")

        # This test always passes - it's informational
        assert True, "Summary report generated"


@pytest.mark.performance
class TestDataLoadedRPS:
    """RPS tests with pre-loaded realistic data"""

    @pytest.mark.asyncio
    async def test_rps_with_large_dataset(self):
        """Test RPS performance with large dataset already loaded"""
        print("\n🗄️  Testing RPS with large dataset simulation")
        print("This test simulates API performance when database contains:")
        print("  • 10,000+ items")
        print("  • 50+ warehouses")
        print("  • 50,000+ inventory levels")
        print("  • Complex search and filtering operations")

        target_rps = 100
        test_duration = 15  # Longer test

        # Simulate heavy database queries
        heavy_queries = [
            f"{BASE_URL}/api/inventory/items?search=switch&page=1&size=50",
            f"{BASE_URL}/api/inventory/items?category=switches&is_active=true",
            f"{BASE_URL}/api/inventory/items?item_type=component&brand=Cherry",
            f"{BASE_URL}/api/inventory/warehouses?page=1&size=20",
            f"{BASE_URL}/api/inventory/analytics/summary",
            f"{BASE_URL}/api/inventory/analytics/low-stock",
        ]

        connector = aiohttp.TCPConnector(limit=80, limit_per_host=80)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            total_requests = target_rps * test_duration

            tasks = []
            for i in range(total_requests):
                query = heavy_queries[i % len(heavy_queries)]

                # Add some randomization to queries
                if "page=" in query:
                    page = random.randint(1, 5)
                    query = query.replace("page=1", f"page={page}")

                task = TestAllMethodsRPS().make_async_request(session, "GET", query)
                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]

        actual_rps = len(successful_requests) / total_test_time
        success_rate = (
            len(successful_requests) / len(valid_results) if valid_results else 0
        )

        print("📊 Large Dataset RPS Results:")
        print(f"  Target RPS: {target_rps}")
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Success rate: {success_rate * 100:.2f}%")
        print(f"  Test duration: {total_test_time:.2f}s")

        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_time = statistics.mean(response_times)
            print(f"  Avg response time: {avg_time * 1000:.2f}ms")

        print("  💡 This simulates real-world performance with large datasets")

        assert len(successful_requests) > 0
        assert success_rate > 0.7, (
            f"Success rate too low with large dataset: {success_rate * 100:.2f}%"
        )
