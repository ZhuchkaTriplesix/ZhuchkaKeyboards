"""
Performance tests specifically for metrics endpoints
Tests Prometheus metrics under high load
"""

import pytest
import asyncio
import aiohttp
import time
import statistics
from typing import Dict, Any


BASE_URL = "http://localhost:8001"


@pytest.mark.performance
class TestMetricsPerformance:
    """Performance tests for metrics and monitoring endpoints"""
    
    async def make_async_request(self, session: aiohttp.ClientSession, method: str, url: str, **kwargs) -> Dict[str, Any]:
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
                    "error": None
                }
        except Exception as e:
            end_time = time.time()
            return {
                "status_code": 0,
                "response_time": end_time - start_time,
                "content_length": 0,
                "success": False,
                "error": str(e)
            }
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint_performance(self):
        """Test /metrics endpoint under load"""
        target_rps = 200  # Metrics endpoint обычно менее нагружен
        test_duration = 10
        total_requests = target_rps * test_duration
        
        print(f"\n📈 Testing /metrics endpoint: {target_rps} RPS for {test_duration}s")
        
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [
                self.make_async_request(session, "GET", f"{BASE_URL}/metrics")
                for _ in range(total_requests)
            ]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            total_test_time = end_time - start_time
        
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]
        
        response_times = [r["response_time"] for r in successful_requests]
        content_sizes = [r["content_length"] for r in successful_requests]
        
        actual_rps = len(successful_requests) / total_test_time
        avg_response_time = statistics.mean(response_times) if response_times else 0
        avg_content_size = statistics.mean(content_sizes) if content_sizes else 0
        
        print(f"📊 Metrics endpoint results:")
        print(f"  Successful requests: {len(successful_requests)}/{total_requests}")
        print(f"  Success rate: {len(successful_requests)/total_requests*100:.2f}%")
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Avg response time: {avg_response_time*1000:.2f}ms")
        print(f"  Avg content size: {avg_content_size:.0f} bytes")
        print(f"  Total data transferred: {sum(content_sizes)/1024/1024:.2f} MB")
        
        if response_times and len(response_times) > 20:
            p95 = statistics.quantiles(response_times, n=20)[18]
            print(f"  P95 response time: {p95*1000:.2f}ms")
        
        # Assertions для metrics endpoint
        assert len(successful_requests) > 0
        assert len(successful_requests) / total_requests > 0.95
        assert avg_response_time < 0.5  # Metrics могут быть медленнее
        assert actual_rps > target_rps * 0.8
        assert avg_content_size > 1000  # Metrics должны содержать данные
    
    @pytest.mark.asyncio
    async def test_metrics_collection_under_load(self):
        """Test that metrics are correctly collected under high API load"""
        print(f"\n🔄 Testing metrics collection accuracy under load")
        
        # Сначала получаем базовые метрики
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Получаем начальные метрики
            initial_metrics = await self.get_request_count_from_metrics(session)
            print(f"  Initial request count: {initial_metrics}")
            
            # Делаем серию запросов к API
            api_requests_count = 100
            health_tasks = [
                self.make_async_request(session, "GET", f"{BASE_URL}/api/health")
                for _ in range(api_requests_count)
            ]
            
            print(f"  Making {api_requests_count} API requests...")
            start_time = time.time()
            api_results = await asyncio.gather(*health_tasks, return_exceptions=True)
            end_time = time.time()
            
            api_test_time = end_time - start_time
            successful_api_requests = len([r for r in api_results if isinstance(r, dict) and r.get("success")])
            
            # Ждем немного для обновления метрик
            await asyncio.sleep(2)
            
            # Получаем финальные метрики
            final_metrics = await self.get_request_count_from_metrics(session)
            print(f"  Final request count: {final_metrics}")
            
            metrics_increase = final_metrics - initial_metrics
            
            print(f"📊 Metrics collection results:")
            print(f"  API requests made: {successful_api_requests}")
            print(f"  API test time: {api_test_time:.2f}s") 
            print(f"  API RPS: {successful_api_requests/api_test_time:.2f}")
            print(f"  Metrics increase: {metrics_increase}")
            print(f"  Accuracy: {metrics_increase/successful_api_requests*100:.1f}%")
            
            # Metrics должны отражать реальное количество запросов (с небольшой погрешностью)
            assert successful_api_requests > 0
            assert metrics_increase > 0
            # Допускаем погрешность 10% (могут быть другие запросы)
            assert abs(metrics_increase - successful_api_requests) / successful_api_requests < 0.1
    
    async def get_request_count_from_metrics(self, session: aiohttp.ClientSession) -> int:
        """Extract total request count from Prometheus metrics"""
        try:
            async with session.get(f"{BASE_URL}/metrics") as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Ищем метрику общего количества запросов
                    for line in content.split('\n'):
                        if 'http_requests_total' in line and 'method="GET"' in line:
                            # Извлекаем значение из строки типа: http_requests_total{method="GET"} 123.0
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    return int(float(parts[-1]))
                                except ValueError:
                                    continue
                    
                    # Если не нашли http_requests_total, ищем другие метрики
                    for line in content.split('\n'):
                        if 'requests_total' in line or 'http_request_total' in line:
                            parts = line.split()
                            if len(parts) >= 2 and not line.startswith('#'):
                                try:
                                    return int(float(parts[-1]))
                                except ValueError:
                                    continue
                    
                    # Fallback: считаем количество строк с метриками
                    metric_lines = [line for line in content.split('\n') 
                                  if line and not line.startswith('#') and line.split() and '=' not in line.split()[0]]
                    return len(metric_lines)
        except Exception as e:
            print(f"Error getting metrics: {e}")
            return 0
        
        return 0
    
    @pytest.mark.asyncio
    async def test_health_and_metrics_mixed_load(self):
        """Test mixed load on health and metrics endpoints"""
        target_rps = 400
        test_duration = 8
        
        # 80% health requests, 20% metrics requests (realistic ratio)
        health_ratio = 0.8
        metrics_ratio = 0.2
        
        total_requests = target_rps * test_duration
        health_requests = int(total_requests * health_ratio)
        metrics_requests = int(total_requests * metrics_ratio)
        
        print(f"\n🔀 Testing mixed health/metrics load:")
        print(f"  Total RPS: {target_rps} for {test_duration}s")
        print(f"  Health requests: {health_requests} ({health_ratio*100:.0f}%)")
        print(f"  Metrics requests: {metrics_requests} ({metrics_ratio*100:.0f}%)")
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Создаем перемешанный список задач
            tasks = []
            
            # Health tasks
            tasks.extend([
                self.make_async_request(session, "GET", f"{BASE_URL}/api/health")
                for _ in range(health_requests)
            ])
            
            # Metrics tasks
            tasks.extend([
                self.make_async_request(session, "GET", f"{BASE_URL}/metrics")
                for _ in range(metrics_requests)
            ])
            
            # Перемешиваем для реалистичности
            import random
            random.shuffle(tasks)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            total_test_time = end_time - start_time
        
        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]
        
        response_times = [r["response_time"] for r in successful_requests]
        content_sizes = [r["content_length"] for r in successful_requests]
        
        actual_rps = len(successful_requests) / total_test_time
        avg_response_time = statistics.mean(response_times) if response_times else 0
        total_data_mb = sum(content_sizes) / 1024 / 1024
        
        # Разделяем результаты по размеру ответа (health ~100 bytes, metrics >1KB)
        health_results = [r for r in successful_requests if r["content_length"] < 500]
        metrics_results = [r for r in successful_requests if r["content_length"] >= 500]
        
        print(f"📊 Mixed load results:")
        print(f"  Total successful: {len(successful_requests)}/{len(valid_results)}")
        print(f"  Health responses: {len(health_results)}")
        print(f"  Metrics responses: {len(metrics_results)}")
        print(f"  Success rate: {len(successful_requests)/len(valid_results)*100:.2f}%")
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Avg response time: {avg_response_time*1000:.2f}ms")
        print(f"  Total data transferred: {total_data_mb:.2f} MB")
        print(f"  Test duration: {total_test_time:.2f}s")
        
        if len(health_results) > 0:
            health_avg_time = statistics.mean([r["response_time"] for r in health_results])
            print(f"  Health avg time: {health_avg_time*1000:.2f}ms")
        
        if len(metrics_results) > 0:
            metrics_avg_time = statistics.mean([r["response_time"] for r in metrics_results])
            print(f"  Metrics avg time: {metrics_avg_time*1000:.2f}ms")
        
        # Assertions
        assert len(successful_requests) > 0
        assert len(successful_requests) / len(valid_results) > 0.9
        assert actual_rps > target_rps * 0.7
        assert avg_response_time < 0.3
        assert len(health_results) > 0, "Should have health responses"
        assert len(metrics_results) > 0, "Should have metrics responses"
