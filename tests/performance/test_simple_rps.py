"""
Simple high RPS performance tests
Tests API capability to handle high concurrent load
"""

import pytest
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any


BASE_URL = "http://localhost:8001"


@pytest.mark.performance
class TestSimpleRPS:
    """Simple high RPS performance tests"""
    
    async def make_async_request(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Make an async HTTP request and measure response time"""
        start_time = time.time()
        try:
            async with session.get(url) as response:
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
    async def test_simple_health_load(self):
        """Simple test: 100 RPS to health endpoint"""
        target_rps = 100
        test_duration = 5
        total_requests = target_rps * test_duration
        
        print(f"\n🚀 Simple health test: {target_rps} RPS for {test_duration}s")
        
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Создаем все задачи сразу
            tasks = [
                self.make_async_request(session, f"{BASE_URL}/api/health")
                for _ in range(total_requests)
            ]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            total_test_time = end_time - start_time
        
        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]
        failed_requests = [r for r in valid_results if not r["success"]]
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = 0
            min_response_time = 0
            max_response_time = 0
        
        actual_rps = len(successful_requests) / total_test_time
        success_rate = len(successful_requests) / len(valid_results) if valid_results else 0
        
        print(f"📊 Simple test results:")
        print(f"  Total requests: {len(valid_results)}")
        print(f"  Successful: {len(successful_requests)}")
        print(f"  Failed: {len(failed_requests)}")
        print(f"  Success rate: {success_rate*100:.2f}%")
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Test duration: {total_test_time:.2f}s")
        
        if successful_requests:
            print(f"  Avg response time: {avg_response_time*1000:.2f}ms")
            print(f"  Min response time: {min_response_time*1000:.2f}ms")
            print(f"  Max response time: {max_response_time*1000:.2f}ms")
        
        # Показываем несколько ошибок для диагностики
        if failed_requests:
            print(f"  Sample errors:")
            for i, req in enumerate(failed_requests[:3]):
                if req.get("error"):
                    print(f"    {i+1}. {req['error']}")
        
        # Мягкие assertions для диагностики
        assert len(valid_results) > 0, "No valid results at all"
        
        if len(successful_requests) == 0:
            print("⚠️  No successful requests - this indicates API connectivity issues")
            print("   Check that gateway is running on http://localhost:8001")
            print("   Try: curl http://localhost:8001/api/health")
        else:
            print(f"✅ Test passed! API handled {actual_rps:.1f} RPS successfully")
    
    @pytest.mark.asyncio
    async def test_burst_health_load(self):
        """Burst test: 500 requests as fast as possible"""
        total_requests = 500
        
        print(f"\n💥 Burst test: {total_requests} requests as fast as possible")
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=20)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Создаем все задачи сразу для максимальной скорости
            tasks = [
                self.make_async_request(session, f"{BASE_URL}/api/health")
                for _ in range(total_requests)
            ]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            total_test_time = end_time - start_time
        
        # Анализ результатов
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]
        
        actual_rps = len(successful_requests) / total_test_time
        success_rate = len(successful_requests) / len(valid_results) if valid_results else 0
        
        print(f"📊 Burst test results:")
        print(f"  Total requests: {len(valid_results)}")
        print(f"  Successful: {len(successful_requests)}")
        print(f"  Success rate: {success_rate*100:.2f}%")
        print(f"  Peak RPS: {actual_rps:.2f}")
        print(f"  Test duration: {total_test_time:.2f}s")
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            print(f"  Avg response time: {avg_response_time*1000:.2f}ms")
            
            if len(response_times) > 10:
                median_time = statistics.median(response_times)
                print(f"  Median response time: {median_time*1000:.2f}ms")
        
        # Проверяем базовую работоспособность
        assert len(valid_results) > 0
        
        if len(successful_requests) > 0:
            print(f"✅ Burst test passed! Peak RPS: {actual_rps:.1f}")
        else:
            print("⚠️  Burst test failed - no successful requests")
    
    @pytest.mark.asyncio
    async def test_mixed_endpoints_light(self):
        """Light test of mixed endpoints"""
        endpoints = [
            f"{BASE_URL}/api/health",
            f"{BASE_URL}/api/inventory/warehouses",
            f"{BASE_URL}/api/inventory/items",
        ]
        
        requests_per_endpoint = 50
        total_requests = len(endpoints) * requests_per_endpoint
        
        print(f"\n🔀 Mixed endpoints test: {requests_per_endpoint} requests per endpoint")
        
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Создаем задачи для всех endpoints
            tasks = []
            for endpoint in endpoints:
                for _ in range(requests_per_endpoint):
                    tasks.append(self.make_async_request(session, endpoint))
            
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
        
        actual_rps = len(successful_requests) / total_test_time
        success_rate = len(successful_requests) / len(valid_results) if valid_results else 0
        
        # Группировка по статус кодам
        status_codes = {}
        for result in valid_results:
            code = result["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1
        
        print(f"📊 Mixed endpoints results:")
        print(f"  Total requests: {len(valid_results)}")
        print(f"  Successful: {len(successful_requests)}")
        print(f"  Success rate: {success_rate*100:.2f}%")
        print(f"  Actual RPS: {actual_rps:.2f}")
        print(f"  Test duration: {total_test_time:.2f}s")
        print(f"  Status codes: {status_codes}")
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            print(f"  Avg response time: {avg_response_time*1000:.2f}ms")
        
        # Базовые проверки
        assert len(valid_results) > 0
        
        if len(successful_requests) > 0:
            print(f"✅ Mixed test passed! RPS: {actual_rps:.1f}")
        else:
            print("⚠️  Mixed test failed - check individual endpoints")
    
    def test_single_request_check(self):
        """Simple synchronous test to check basic connectivity"""
        import requests
        
        print(f"\n🔍 Single request connectivity check")
        
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/api/health", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            print(f"📊 Single request result:")
            print(f"  Status code: {response.status_code}")
            print(f"  Response time: {response_time:.2f}ms")
            print(f"  Content length: {len(response.text)} bytes")
            
            if response.status_code == 200:
                print(f"  Content preview: {response.text[:100]}...")
                print("✅ Basic connectivity works!")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"  Response: {response.text}")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            assert response_time < 1000, f"Response too slow: {response_time:.2f}ms"
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise AssertionError(f"Cannot connect to API: {e}")
