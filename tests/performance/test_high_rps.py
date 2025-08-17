"""
High RPS (Requests Per Second) performance tests
Tests API capability to handle thousands of concurrent requests
"""

import pytest
import asyncio
import aiohttp
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any


BASE_URL = "http://localhost:8001"


@pytest.mark.performance
class TestHighRPSPerformance:
    """High RPS performance tests for inventory API"""

    async def make_async_request(
        self, session: aiohttp.ClientSession, method: str, url: str, **kwargs
    ) -> Dict[str, Any]:
        """Make an async HTTP request and measure response time"""
        start_time = time.time()
        try:
            async with session.request(method, url, **kwargs) as response:
                end_time = time.time()
                content = await response.text()

                return {
                    "status_code": response.status,
                    "response_time": end_time - start_time,
                    "content_length": len(content),
                    "success": 200 <= response.status < 300,
                    "error": None,
                }
        except Exception as e:
            end_time = time.time()
            return {
                "status_code": 0,
                "response_time": end_time - start_time,
                "content_length": 0,
                "success": False,
                "error": str(e),
            }

    @pytest.mark.asyncio
    async def test_health_endpoint_high_rps(self):
        """Test health endpoint under high RPS load"""
        target_rps = 1000
        test_duration = 10  # seconds
        total_requests = target_rps * test_duration

        print(
            f"\n🚀 Testing health endpoint: {target_rps} RPS for {test_duration}s ({total_requests} total requests)"
        )

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            # Создаем задачи с задержкой для равномерного распределения
            tasks = []
            delay_between_requests = 1.0 / target_rps

            start_time = time.time()

            for i in range(total_requests):
                # Добавляем небольшую задержку для равномерного распределения
                await asyncio.sleep(delay_between_requests)
                task = asyncio.create_task(
                    self.make_async_request(session, "GET", f"{BASE_URL}/api/health")
                )
                tasks.append(task)

                # Если набралось достаточно задач, ждем их завершения
                if len(tasks) >= 100:
                    results = await asyncio.gather(*tasks)
                    tasks = []

            # Завершаем оставшиеся задачи
            if tasks:
                results = await asyncio.gather(*tasks)

            end_time = time.time()
            total_test_time = end_time - start_time

            # Собираем результаты из всех батчей
            all_results = []
            for batch_start in range(0, total_requests, 100):
                batch_end = min(batch_start + 100, total_requests)
                batch_tasks = [
                    self.make_async_request(session, "GET", f"{BASE_URL}/api/health")
                    for _ in range(batch_end - batch_start)
                ]
                batch_results = await asyncio.gather(*batch_tasks)
                all_results.extend(batch_results)

        # Анализ результатов
        successful_requests = [r for r in all_results if r["success"]]
        failed_requests = [r for r in all_results if not r["success"]]

        response_times = [r["response_time"] for r in successful_requests]

        actual_rps = len(successful_requests) / total_test_time
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = (
            statistics.quantiles(response_times, n=20)[18]
            if len(response_times) > 20
            else 0
        )
        p99_response_time = (
            statistics.quantiles(response_times, n=100)[98]
            if len(response_times) > 100
            else 0
        )

        print("📊 Results:")
        print(f"  Total requests: {len(all_results)}")
        print(f"  Successful: {len(successful_requests)}")
        print(f"  Failed: {len(failed_requests)}")
        print(
            f"  Success rate: {len(successful_requests) / len(all_results) * 100:.2f}%"
        )
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Avg response time: {avg_response_time * 1000:.2f}ms")
        print(f"  P95 response time: {p95_response_time * 1000:.2f}ms")
        print(f"  P99 response time: {p99_response_time * 1000:.2f}ms")
        print(f"  Total test time: {total_test_time:.2f}s")

        # Assertions для производительности
        assert len(successful_requests) > 0, "No successful requests"
        assert len(successful_requests) / len(all_results) > 0.95, (
            f"Success rate too low: {len(successful_requests) / len(all_results) * 100:.2f}%"
        )
        assert avg_response_time < 0.1, (
            f"Average response time too high: {avg_response_time * 1000:.2f}ms"
        )
        assert actual_rps > target_rps * 0.8, (
            f"RPS too low: {actual_rps:.2f} (target: {target_rps})"
        )

    @pytest.mark.asyncio
    async def test_warehouse_list_high_rps(self):
        """Test warehouse listing endpoint under high RPS"""
        target_rps = 500
        test_duration = 5
        total_requests = target_rps * test_duration

        print(f"\n📦 Testing warehouse listing: {target_rps} RPS for {test_duration}s")

        connector = aiohttp.TCPConnector(limit=50, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            # Создаем все задачи сразу
            tasks = [
                self.make_async_request(
                    session, "GET", f"{BASE_URL}/api/inventory/warehouses"
                )
                for _ in range(total_requests)
            ]

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        # Фильтруем исключения
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]

        response_times = [r["response_time"] for r in successful_requests]
        actual_rps = len(successful_requests) / total_test_time
        avg_response_time = statistics.mean(response_times) if response_times else 0

        print("📊 Warehouse listing results:")
        print(f"  Successful requests: {len(successful_requests)}/{total_requests}")
        print(f"  Success rate: {len(successful_requests) / total_requests * 100:.2f}%")
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Avg response time: {avg_response_time * 1000:.2f}ms")
        print(f"  Test duration: {total_test_time:.2f}s")

        assert len(successful_requests) > 0
        assert len(successful_requests) / total_requests > 0.9
        assert avg_response_time < 0.2
        assert actual_rps > target_rps * 0.7

    @pytest.mark.asyncio
    async def test_mixed_endpoints_load(self):
        """Test mixed endpoint load (real-world scenario)"""
        target_total_rps = 800
        test_duration = 8

        # Распределение запросов по эндпоинтам (как в реальном мире)
        endpoints = [
            {"method": "GET", "url": f"{BASE_URL}/api/health", "weight": 0.3},
            {
                "method": "GET",
                "url": f"{BASE_URL}/api/inventory/warehouses",
                "weight": 0.25,
            },
            {"method": "GET", "url": f"{BASE_URL}/api/inventory/items", "weight": 0.25},
            {
                "method": "GET",
                "url": f"{BASE_URL}/api/inventory/analytics/summary",
                "weight": 0.15,
            },
            {
                "method": "GET",
                "url": f"{BASE_URL}/api/inventory/analytics/low-stock",
                "weight": 0.05,
            },
        ]

        print(
            f"\n🔀 Testing mixed endpoints: {target_total_rps} total RPS for {test_duration}s"
        )

        # Рассчитываем количество запросов для каждого эндпоинта
        total_requests = target_total_rps * test_duration
        endpoint_requests = []

        for endpoint in endpoints:
            count = int(total_requests * endpoint["weight"])
            endpoint_requests.extend([endpoint] * count)

        print("  Distribution:")
        for endpoint in endpoints:
            count = int(total_requests * endpoint["weight"])
            rps = count / test_duration
            print(f"    {endpoint['url']}: {count} requests ({rps:.1f} RPS)")

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            # Перемешиваем запросы для реалистичности
            import random

            random.shuffle(endpoint_requests)

            # Создаем задачи
            tasks = [
                self.make_async_request(session, req["method"], req["url"])
                for req in endpoint_requests
            ]

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            total_test_time = end_time - start_time

        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]

        response_times = [r["response_time"] for r in successful_requests]
        actual_rps = len(successful_requests) / total_test_time
        avg_response_time = statistics.mean(response_times) if response_times else 0

        # Группировка по кодам ответа
        status_codes = {}
        for result in valid_results:
            code = result["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1

        print("📊 Mixed load results:")
        print(f"  Total requests: {len(valid_results)}")
        print(f"  Successful: {len(successful_requests)}")
        print(
            f"  Success rate: {len(successful_requests) / len(valid_results) * 100:.2f}%"
        )
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Avg response time: {avg_response_time * 1000:.2f}ms")
        print(f"  Test duration: {total_test_time:.2f}s")
        print(f"  Status codes: {status_codes}")

        if response_times:
            print(f"  Min response time: {min(response_times) * 1000:.2f}ms")
            print(f"  Max response time: {max(response_times) * 1000:.2f}ms")
            if len(response_times) > 10:
                p95 = statistics.quantiles(response_times, n=20)[18]
                print(f"  P95 response time: {p95 * 1000:.2f}ms")

        assert len(successful_requests) > 0
        assert len(successful_requests) / len(valid_results) > 0.85
        assert actual_rps > target_total_rps * 0.6

    def test_burst_load_with_threads(self):
        """Test burst load using threading (different approach)"""
        target_rps = 1500
        burst_duration = 3
        total_requests = target_rps * burst_duration
        max_workers = 50

        print(
            f"\n💥 Testing burst load with threads: {target_rps} RPS for {burst_duration}s"
        )
        print(f"  Using {max_workers} thread workers")

        import requests

        def make_request(request_id: int) -> Dict[str, Any]:
            """Make a single request"""
            start_time = time.time()
            try:
                response = requests.get(f"{BASE_URL}/api/health", timeout=10)
                end_time = time.time()

                return {
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": 200 <= response.status_code < 300,
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "request_id": request_id,
                    "status_code": 0,
                    "response_time": end_time - start_time,
                    "success": False,
                    "error": str(e),
                }

        # Выполняем запросы с помощью ThreadPoolExecutor
        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Отправляем все задачи
            future_to_id = {
                executor.submit(make_request, i): i for i in range(total_requests)
            }

            # Собираем результаты
            for future in as_completed(future_to_id):
                result = future.result()
                results.append(result)

        end_time = time.time()
        total_test_time = end_time - start_time

        # Анализ
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]

        actual_rps = len(successful_requests) / total_test_time
        avg_response_time = statistics.mean(response_times) if response_times else 0

        print("📊 Burst load results:")
        print(f"  Total requests: {len(results)}")
        print(f"  Successful: {len(successful_requests)}")
        print(f"  Success rate: {len(successful_requests) / len(results) * 100:.2f}%")
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Avg response time: {avg_response_time * 1000:.2f}ms")
        print(f"  Test duration: {total_test_time:.2f}s")

        if response_times:
            print(f"  Min response time: {min(response_times) * 1000:.2f}ms")
            print(f"  Max response time: {max(response_times) * 1000:.2f}ms")
            if len(response_times) > 100:
                p99 = statistics.quantiles(response_times, n=100)[98]
                print(f"  P99 response time: {p99 * 1000:.2f}ms")

        assert len(successful_requests) > 0
        assert len(successful_requests) / len(results) > 0.8
        assert actual_rps > target_rps * 0.5  # Более мягкое требование для burst load

    @pytest.mark.asyncio
    async def test_sustained_high_load(self):
        """Test sustained high load over longer period"""
        target_rps = 300
        test_duration = 30  # 30 секунд
        batch_size = 50

        print(f"\n⏱️  Testing sustained load: {target_rps} RPS for {test_duration}s")
        print(f"  Using batches of {batch_size} requests")

        total_requests = target_rps * test_duration
        batches = total_requests // batch_size

        connector = aiohttp.TCPConnector(limit=batch_size, limit_per_host=batch_size)
        timeout = aiohttp.ClientTimeout(total=60)

        all_results = []
        batch_times = []

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            start_time = time.time()

            for batch_num in range(batches):
                batch_start = time.time()

                # Создаем батч запросов
                tasks = [
                    self.make_async_request(session, "GET", f"{BASE_URL}/api/health")
                    for _ in range(batch_size)
                ]

                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                valid_batch_results = [r for r in batch_results if isinstance(r, dict)]
                all_results.extend(valid_batch_results)

                batch_end = time.time()
                batch_time = batch_end - batch_start
                batch_times.append(batch_time)

                # Прогресс
                if (batch_num + 1) % 10 == 0:
                    elapsed = batch_end - start_time
                    current_rps = len(all_results) / elapsed
                    print(f"    Batch {batch_num + 1}/{batches}: {current_rps:.1f} RPS")

                # Небольшая пауза для равномерного распределения
                target_batch_time = batch_size / target_rps
                if batch_time < target_batch_time:
                    await asyncio.sleep(target_batch_time - batch_time)

            end_time = time.time()
            total_test_time = end_time - start_time

        # Анализ результатов
        successful_requests = [r for r in all_results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]

        actual_rps = len(successful_requests) / total_test_time
        avg_response_time = statistics.mean(response_times) if response_times else 0
        avg_batch_time = statistics.mean(batch_times) if batch_times else 0

        print("📊 Sustained load results:")
        print(f"  Total requests: {len(all_results)}")
        print(f"  Successful: {len(successful_requests)}")
        print(
            f"  Success rate: {len(successful_requests) / len(all_results) * 100:.2f}%"
        )
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Avg response time: {avg_response_time * 1000:.2f}ms")
        print(f"  Avg batch time: {avg_batch_time:.3f}s")
        print(f"  Total test time: {total_test_time:.2f}s")
        print(f"  Batches completed: {len(batch_times)}")

        if response_times and len(response_times) > 100:
            p50 = statistics.median(response_times)
            p95 = statistics.quantiles(response_times, n=20)[18]
            p99 = statistics.quantiles(response_times, n=100)[98]
            print(f"  P50 response time: {p50 * 1000:.2f}ms")
            print(f"  P95 response time: {p95 * 1000:.2f}ms")
            print(f"  P99 response time: {p99 * 1000:.2f}ms")

        assert len(successful_requests) > 0
        assert len(successful_requests) / len(all_results) > 0.95
        assert actual_rps > target_rps * 0.8
        assert avg_response_time < 0.1  # 100ms среднее время ответа

    @pytest.mark.asyncio
    async def test_gradual_ramp_up(self):
        """Test gradual RPS ramp up to find breaking point"""
        print("\n📈 Testing gradual RPS ramp up")

        rps_levels = [100, 200, 400, 600, 800, 1000, 1200, 1500]
        test_duration_per_level = 5

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)

        results_by_rps = {}

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            for target_rps in rps_levels:
                print(f"  Testing {target_rps} RPS...")

                total_requests = target_rps * test_duration_per_level

                tasks = [
                    self.make_async_request(session, "GET", f"{BASE_URL}/api/health")
                    for _ in range(total_requests)
                ]

                start_time = time.time()
                level_results = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()

                test_time = end_time - start_time
                valid_results = [r for r in level_results if isinstance(r, dict)]
                successful = [r for r in valid_results if r["success"]]

                actual_rps = len(successful) / test_time
                success_rate = (
                    len(successful) / len(valid_results) if valid_results else 0
                )
                avg_response_time = (
                    statistics.mean([r["response_time"] for r in successful])
                    if successful
                    else 0
                )

                results_by_rps[target_rps] = {
                    "actual_rps": actual_rps,
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "total_requests": len(valid_results),
                    "successful_requests": len(successful),
                }

                print(
                    f"    Result: {actual_rps:.1f} RPS, {success_rate * 100:.1f}% success, {avg_response_time * 1000:.1f}ms avg"
                )

                # Если производительность сильно упала, прерываем тест
                if success_rate < 0.8 or avg_response_time > 0.5:
                    print(
                        f"    ⚠️  Performance degraded significantly at {target_rps} RPS"
                    )
                    break

                # Небольшая пауза между уровнями
                await asyncio.sleep(2)

        # Итоговый анализ
        print("\n📊 RPS Ramp-up Summary:")
        print(
            f"{'RPS':>6} {'Actual':>8} {'Success%':>8} {'AvgTime':>8} {'Requests':>9}"
        )
        print("-" * 50)

        max_stable_rps = 0
        for target_rps, data in results_by_rps.items():
            print(
                f"{target_rps:>6} {data['actual_rps']:>8.1f} {data['success_rate'] * 100:>7.1f}% {data['avg_response_time'] * 1000:>7.1f}ms {data['successful_requests']:>9}"
            )

            # Определяем максимальный стабильный RPS (>90% success, <200ms avg time)
            if data["success_rate"] > 0.9 and data["avg_response_time"] < 0.2:
                max_stable_rps = max(max_stable_rps, data["actual_rps"])

        print(f"\n🎯 Maximum stable RPS: {max_stable_rps:.1f}")

        # API должен выдержать хотя бы 500 RPS
        assert max_stable_rps >= 500, (
            f"API should handle at least 500 RPS, but max stable was {max_stable_rps:.1f}"
        )
