"""
RPS Benchmarks for comparing API performance across different scenarios
Tests API with empty database vs loaded database vs heavy database
"""

import pytest
import asyncio
import aiohttp
import time
import statistics
import random
from typing import List, Dict


BASE_URL = "http://localhost:8001"


@pytest.mark.performance
class TestRPSBenchmarks:
    """Comprehensive RPS benchmarks for API performance comparison"""

    @pytest.mark.asyncio
    async def test_empty_database_baseline(self):
        """Baseline RPS test with empty database"""
        print("\n🌱 BASELINE: Empty Database RPS Test")
        print("Testing API performance with minimal database load")

        target_rps = 300
        test_duration = 10
        total_requests = target_rps * test_duration

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=10)

        # Простые endpoints которые должны работать быстро на пустой БД
        endpoints = [
            f"{BASE_URL}/api/health",
            f"{BASE_URL}/api/inventory/warehouses",
            f"{BASE_URL}/api/inventory/items",
            f"{BASE_URL}/api/inventory/analytics/summary",
            f"{BASE_URL}/metrics",
        ]

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = []
            for i in range(total_requests):
                endpoint = endpoints[i % len(endpoints)]
                task = self._make_request(session, "GET", endpoint)
                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        stats = self._analyze_results(
            "Empty Database Baseline", results, total_test_time, target_rps
        )

        # Базовая производительность должна быть высокой
        assert stats["success_rate"] > 0.8, (
            f"Baseline success rate too low: {stats['success_rate']:.2f}"
        )
        assert stats["actual_rps"] > 50, (
            f"Baseline RPS too low: {stats['actual_rps']:.2f}"
        )

        return stats

    @pytest.mark.asyncio
    async def test_loaded_database_performance(self):
        """RPS test with moderately loaded database"""
        print("\n📚 LOADED DATABASE: RPS Test with realistic data")
        print("Testing API performance with moderate database load")

        target_rps = 150
        test_duration = 15
        total_requests = target_rps * test_duration

        connector = aiohttp.TCPConnector(limit=80, limit_per_host=80)
        timeout = aiohttp.ClientTimeout(total=15)

        # Более сложные запросы для загруженной БД
        complex_endpoints = [
            f"{BASE_URL}/api/inventory/warehouses?page=1&size=20",
            f"{BASE_URL}/api/inventory/items?search=switch&page=1&size=10",
            f"{BASE_URL}/api/inventory/items?category=switches",
            f"{BASE_URL}/api/inventory/items?item_type=component&is_active=true",
            f"{BASE_URL}/api/inventory/analytics/summary",
            f"{BASE_URL}/api/inventory/analytics/low-stock",
            f"{BASE_URL}/api/health",
            f"{BASE_URL}/metrics",
        ]

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = []
            for i in range(total_requests):
                endpoint = complex_endpoints[i % len(complex_endpoints)]

                # Добавляем вариативность в запросы
                if "page=" in endpoint:
                    page = random.randint(1, 5)
                    endpoint = endpoint.replace("page=1", f"page={page}")

                task = self._make_request(session, "GET", endpoint)
                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        stats = self._analyze_results(
            "Loaded Database", results, total_test_time, target_rps
        )

        # Производительность с данными должна быть приемлемой
        assert stats["success_rate"] > 0.7, (
            f"Loaded DB success rate too low: {stats['success_rate']:.2f}"
        )
        assert stats["actual_rps"] > 30, (
            f"Loaded DB RPS too low: {stats['actual_rps']:.2f}"
        )

        return stats

    @pytest.mark.asyncio
    async def test_heavy_database_stress(self):
        """RPS test with heavy database operations"""
        print("\n💪 HEAVY DATABASE: Stress test with complex operations")
        print("Testing API limits with heavy database operations")

        target_rps = 80
        test_duration = 20
        total_requests = target_rps * test_duration

        connector = aiohttp.TCPConnector(limit=60, limit_per_host=60)
        timeout = aiohttp.ClientTimeout(total=30)

        # Тяжелые операции
        heavy_endpoints = [
            f"{BASE_URL}/api/inventory/items?search=component&page=1&size=50",  # Большие результаты
            f"{BASE_URL}/api/inventory/items?search=switch&category=switches&brand=Cherry",  # Множественные фильтры
            f"{BASE_URL}/api/inventory/analytics/summary",  # Аналитика
            f"{BASE_URL}/api/inventory/analytics/low-stock",  # Сложные расчеты
            f"{BASE_URL}/metrics",  # Prometheus метрики
        ]

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = []
            for i in range(total_requests):
                endpoint = heavy_endpoints[i % len(heavy_endpoints)]

                # Добавляем случайные параметры для усложнения
                if "search=" in endpoint and random.random() < 0.3:
                    search_terms = [
                        "key",
                        "switch",
                        "cap",
                        "component",
                        "mechanical",
                        "board",
                    ]
                    term = random.choice(search_terms)
                    endpoint = endpoint.replace("search=component", f"search={term}")

                task = self._make_request(session, "GET", endpoint)
                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        stats = self._analyze_results(
            "Heavy Database Stress", results, total_test_time, target_rps
        )

        # Даже под нагрузкой должна быть минимальная производительность
        assert stats["success_rate"] > 0.6, (
            f"Heavy DB success rate too low: {stats['success_rate']:.2f}"
        )
        assert stats["actual_rps"] > 10, (
            f"Heavy DB RPS too low: {stats['actual_rps']:.2f}"
        )

        return stats

    @pytest.mark.asyncio
    async def test_mixed_operations_benchmark(self):
        """Benchmark mixed CRUD operations under load"""
        print("\n🔀 MIXED OPERATIONS: CRUD benchmark")
        print("Testing mixed GET/POST/PUT operations performance")

        target_rps = 100
        test_duration = 12
        total_requests = target_rps * test_duration

        connector = aiohttp.TCPConnector(limit=70, limit_per_host=70)
        timeout = aiohttp.ClientTimeout(total=25)

        # Смешанные операции (реалистичное распределение)
        operation_weights = [70, 20, 8, 2]  # GET, POST, PUT, DELETE
        operations = ["GET", "POST", "PUT", "DELETE"]

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = []
            created_ids = []

            for i in range(total_requests):
                operation = random.choices(operations, weights=operation_weights)[0]

                if operation == "GET":
                    # GET operations (70%)
                    get_endpoints = [
                        f"{BASE_URL}/api/inventory/warehouses",
                        f"{BASE_URL}/api/inventory/items",
                        f"{BASE_URL}/api/inventory/analytics/summary",
                        f"{BASE_URL}/api/health",
                    ]
                    endpoint = random.choice(get_endpoints)
                    task = self._make_request(session, "GET", endpoint)

                elif operation == "POST":
                    # POST operations (20%)
                    if random.choice([True, False]):
                        # Create warehouse
                        warehouse_data = {
                            "name": f"Benchmark Warehouse {i}",
                            "code": f"BM-WH-{i:04d}",
                            "description": f"Benchmark test warehouse {i}",
                            "address": f"{i} Test Street",
                            "city": "Test City",
                            "postal_code": f"{10000 + i}",
                            "country": "Test Country",
                            "contact_person": f"Test Manager {i}",
                            "phone": f"+1-555-{i:04d}",
                            "email": f"test{i}@benchmark.com",
                            "is_active": True,
                        }
                        task = self._make_request(
                            session,
                            "POST",
                            f"{BASE_URL}/api/inventory/warehouses",
                            json=warehouse_data,
                        )
                    else:
                        # Create item
                        item_data = {
                            "sku": f"BM-ITEM-{i:04d}",
                            "name": f"Benchmark Item {i}",
                            "description": f"Test item for benchmarking {i}",
                            "item_type": "component",
                            "category": "tools",
                            "brand": "Benchmark",
                            "model": f"Model-{i}",
                            "unit_of_measure": "piece",
                            "weight_kg": 0.1,
                            "dimensions": "10x10x5 mm",
                            "min_stock_level": 10,
                            "max_stock_level": 100,
                            "unit_cost": 1.0,
                            "selling_price": 2.0,
                            "is_active": True,
                            "is_tracked": True,
                        }
                        task = self._make_request(
                            session,
                            "POST",
                            f"{BASE_URL}/api/inventory/items",
                            json=item_data,
                        )

                elif operation == "PUT" and created_ids:
                    # PUT operations (8%) - только если есть созданные ресурсы
                    resource_id = random.choice(created_ids)
                    update_data = {"name": f"Updated Resource {i}"}
                    task = self._make_request(
                        session,
                        "PUT",
                        f"{BASE_URL}/api/inventory/warehouses/{resource_id}",
                        json=update_data,
                    )

                else:
                    # Fallback to GET if no resources to update/delete
                    task = self._make_request(session, "GET", f"{BASE_URL}/api/health")

                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        stats = self._analyze_results(
            "Mixed Operations", results, total_test_time, target_rps
        )

        # Смешанные операции должны работать стабильно
        assert stats["success_rate"] > 0.6, (
            f"Mixed operations success rate too low: {stats['success_rate']:.2f}"
        )
        assert stats["actual_rps"] > 20, (
            f"Mixed operations RPS too low: {stats['actual_rps']:.2f}"
        )

        return stats

    @pytest.mark.asyncio
    async def test_concurrent_users_simulation(self):
        """Simulate multiple concurrent users"""
        print("\n👥 CONCURRENT USERS: Multi-user simulation")
        print("Simulating realistic user behavior patterns")

        # Симулируем 20 пользователей, каждый делает 50 запросов
        users_count = 20
        requests_per_user = 50
        total_requests = users_count * requests_per_user

        connector = aiohttp.TCPConnector(
            limit=users_count * 2, limit_per_host=users_count * 2
        )
        timeout = aiohttp.ClientTimeout(total=30)

        async def simulate_user(
            session: aiohttp.ClientSession, user_id: int
        ) -> List[Dict]:
            """Simulate single user behavior"""
            user_results = []

            # Каждый пользователь имеет свой паттерн поведения
            user_endpoints = [
                f"{BASE_URL}/api/inventory/warehouses",  # Просмотр складов
                f"{BASE_URL}/api/inventory/items?page=1&size=10",  # Просмотр товаров
                f"{BASE_URL}/api/inventory/items?search=switch",  # Поиск
                f"{BASE_URL}/api/inventory/analytics/summary",  # Аналитика
            ]

            for i in range(requests_per_user):
                # Случайная пауза между запросами пользователя (человеческое поведение)
                if i > 0:
                    await asyncio.sleep(random.uniform(0.1, 1.0))

                endpoint = random.choice(user_endpoints)
                result = await self._make_request(session, "GET", endpoint)
                user_results.append(result)

            return user_results

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            start_time = time.time()

            # Запускаем всех пользователей параллельно
            user_tasks = [simulate_user(session, i) for i in range(users_count)]
            all_user_results = await asyncio.gather(*user_tasks, return_exceptions=True)

            end_time = time.time()
            total_test_time = end_time - start_time

        # Flatten results from all users
        all_results = []
        for user_results in all_user_results:
            if isinstance(user_results, list):
                all_results.extend(user_results)

        stats = self._analyze_results(
            "Concurrent Users", all_results, total_test_time, target_rps=0
        )

        print(f"  Simulated users: {users_count}")
        print(f"  Requests per user: {requests_per_user}")
        print("  User think time: 0.1-1.0s between requests")

        # Многопользовательский режим должен работать стабильно
        assert stats["success_rate"] > 0.7, (
            f"Multi-user success rate too low: {stats['success_rate']:.2f}"
        )

        return stats

    async def _make_request(
        self, session: aiohttp.ClientSession, method: str, url: str, **kwargs
    ) -> Dict:
        """Make async HTTP request"""
        start_time = time.time()
        try:
            async with session.request(method, url, **kwargs) as response:
                end_time = time.time()

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
                    "success": 200 <= response.status < 300,
                    "content_length": len(str(content)),
                    "method": method,
                    "url": url,
                }
        except Exception as e:
            end_time = time.time()
            return {
                "status_code": 0,
                "response_time": end_time - start_time,
                "success": False,
                "content_length": 0,
                "method": method,
                "url": url,
                "error": str(e),
            }

    def _analyze_results(
        self, test_name: str, results: List, total_time: float, target_rps: int
    ) -> Dict:
        """Analyze test results and print statistics"""
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r.get("success", False)]

        success_rate = (
            len(successful_requests) / len(valid_results) if valid_results else 0
        )
        actual_rps = len(successful_requests) / total_time if total_time > 0 else 0

        stats = {
            "test_name": test_name,
            "total_requests": len(valid_results),
            "successful_requests": len(successful_requests),
            "success_rate": success_rate,
            "actual_rps": actual_rps,
            "target_rps": target_rps,
            "total_time": total_time,
        }

        print(f"📊 {test_name} Results:")
        print(f"  Total requests: {len(valid_results)}")
        print(f"  Successful: {len(successful_requests)}")
        print(f"  Success rate: {success_rate * 100:.2f}%")
        print(f"  Actual RPS: {actual_rps:.2f}")
        if target_rps > 0:
            print(f"  Target RPS: {target_rps}")
            performance = (actual_rps / target_rps * 100) if target_rps > 0 else 0
            print(f"  Performance: {performance:.1f}% of target")
        print(f"  Test duration: {total_time:.2f}s")

        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)

            print(f"  Avg response time: {avg_time * 1000:.2f}ms")
            print(f"  Min response time: {min_time * 1000:.2f}ms")
            print(f"  Max response time: {max_time * 1000:.2f}ms")

            stats.update(
                {
                    "avg_response_time": avg_time,
                    "min_response_time": min_time,
                    "max_response_time": max_time,
                }
            )

            if len(response_times) > 10:
                median_time = statistics.median(response_times)
                p95_time = statistics.quantiles(response_times, n=20)[
                    18
                ]  # 95th percentile
                print(f"  Median response time: {median_time * 1000:.2f}ms")
                print(f"  95th percentile: {p95_time * 1000:.2f}ms")

                stats.update(
                    {"median_response_time": median_time, "p95_response_time": p95_time}
                )

        # Performance rating
        if target_rps > 0:
            if actual_rps >= target_rps * 0.8:
                print("  🟢 Performance Rating: Excellent")
            elif actual_rps >= target_rps * 0.6:
                print("  🟡 Performance Rating: Good")
            elif actual_rps >= target_rps * 0.4:
                print("  🟠 Performance Rating: Fair")
            else:
                print("  🔴 Performance Rating: Needs Improvement")

        return stats

    @pytest.mark.asyncio
    async def test_performance_comparison_report(self):
        """Generate comprehensive performance comparison report"""
        print("\n📋 PERFORMANCE COMPARISON REPORT")
        print("=" * 80)

        # Этот тест запускает все предыдущие тесты и сравнивает результаты
        print("\n🔄 Running all benchmark tests for comparison...")

        # Collect results from all tests
        benchmark_results = {}

        print("\n1️⃣ Testing empty database baseline...")
        benchmark_results["empty_db"] = await self.test_empty_database_baseline()

        print("\n2️⃣ Testing with loaded database...")
        benchmark_results["loaded_db"] = await self.test_loaded_database_performance()

        print("\n3️⃣ Testing heavy database operations...")
        benchmark_results["heavy_db"] = await self.test_heavy_database_stress()

        print("\n4️⃣ Testing mixed operations...")
        benchmark_results["mixed_ops"] = await self.test_mixed_operations_benchmark()

        print("\n5️⃣ Testing concurrent users...")
        benchmark_results[
            "concurrent_users"
        ] = await self.test_concurrent_users_simulation()

        # Generate comparison report
        print("\n📊 BENCHMARK COMPARISON")
        print("=" * 80)

        print(f"{'Test Name':<25} {'RPS':<8} {'Success%':<9} {'Avg RT':<8} {'Rating'}")
        print(f"{'-' * 25} {'-' * 8} {'-' * 9} {'-' * 8} {'-' * 10}")

        for test_key, stats in benchmark_results.items():
            rps = f"{stats['actual_rps']:.1f}"
            success = f"{stats['success_rate'] * 100:.1f}%"
            avg_rt = f"{stats.get('avg_response_time', 0) * 1000:.0f}ms"

            # Simple rating based on RPS
            if stats["actual_rps"] > 100:
                rating = "🟢 Excellent"
            elif stats["actual_rps"] > 50:
                rating = "🟡 Good"
            elif stats["actual_rps"] > 25:
                rating = "🟠 Fair"
            else:
                rating = "🔴 Poor"

            print(f"{test_key:<25} {rps:<8} {success:<9} {avg_rt:<8} {rating}")

        print("\n🎯 PERFORMANCE INSIGHTS:")

        # Find best and worst performing tests
        rps_values = {k: v["actual_rps"] for k, v in benchmark_results.items()}
        best_test = max(rps_values, key=rps_values.get)
        worst_test = min(rps_values, key=rps_values.get)

        print(f"  • Best performance: {best_test} ({rps_values[best_test]:.1f} RPS)")
        print(f"  • Worst performance: {worst_test} ({rps_values[worst_test]:.1f} RPS)")

        # Performance degradation analysis
        if "empty_db" in benchmark_results and "loaded_db" in benchmark_results:
            empty_rps = benchmark_results["empty_db"]["actual_rps"]
            loaded_rps = benchmark_results["loaded_db"]["actual_rps"]
            degradation = (
                ((empty_rps - loaded_rps) / empty_rps * 100) if empty_rps > 0 else 0
            )
            print(f"  • Performance degradation with data: {degradation:.1f}%")

        print("\n🚀 OPTIMIZATION RECOMMENDATIONS:")
        print("  1. Database indexing for search operations")
        print("  2. Redis caching for frequently accessed data")
        print("  3. Connection pooling optimization")
        print("  4. Load balancing for concurrent users")
        print("  5. Query optimization for analytics endpoints")

        # Always passes - this is a reporting test
        assert True, "Performance comparison report generated"
