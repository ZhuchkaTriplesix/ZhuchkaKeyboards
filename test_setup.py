#!/usr/bin/env python3
"""
Test script to verify the monitoring and database setup
"""

import requests


def test_health_endpoints():
    """Test health check endpoints"""
    print("🩺 Testing health endpoints...")

    endpoints = [
        ("http://localhost:8001/api/health", "Basic Health"),
        ("http://localhost:8001/api/health/deep", "Deep Health"),
        ("http://localhost:8001/api/health/liveness", "Liveness"),
        ("http://localhost:8001/api/health/readiness", "Readiness"),
    ]

    for url, name in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: Connection failed - {e}")


def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    print("\n📊 Testing metrics endpoint...")

    try:
        response = requests.get("http://localhost:8001/metrics", timeout=5)
        if response.status_code == 200:
            metrics_count = len(
                [
                    line
                    for line in response.text.split("\n")
                    if line and not line.startswith("#")
                ]
            )
            print(f"✅ Metrics endpoint: OK ({metrics_count} metrics)")
        else:
            print(f"❌ Metrics endpoint: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Metrics endpoint: Connection failed - {e}")


def test_monitoring_services():
    """Test monitoring services"""
    print("\n📈 Testing monitoring services...")

    services = [
        ("http://localhost:9090/-/healthy", "Prometheus"),
        ("http://localhost:3000/api/health", "Grafana"),
        ("http://localhost:3100/ready", "Loki"),
    ]

    for url, name in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: Connection failed - {e}")


def main():
    """Main test function"""
    print("🔍 ZhuchkaKeyboards Setup Test")
    print("=" * 50)

    test_health_endpoints()
    test_metrics_endpoint()
    test_monitoring_services()

    print("\n" + "=" * 50)
    print("🎯 Test complete!")
    print("\nIf services are not running, use:")
    print("  make dev          # Start development environment")
    print("  make monitoring   # Start monitoring stack")


if __name__ == "__main__":
    main()
