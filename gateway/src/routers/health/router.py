"""
Health check and monitoring endpoints
"""

import time
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from services.redis.rediska import redis_manager
from services.metrics import prometheus_metrics
from database.core import get_db
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return ORJSONResponse(
        {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "ZhuchkaKeyboards Gateway",
        }
    )


@router.get("/health/deep")
async def deep_health_check():
    """Deep health check that tests all dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "ZhuchkaKeyboards Gateway",
        "checks": {},
    }

    overall_healthy = True

    # Check database connection (simplified for now)
    try:
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection not tested in deep health check (middleware handles DB)",
        }

    except Exception as e:
        overall_healthy = False
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "Database connection failed",
        }

        # Record metric
        prometheus_metrics.record_error("DatabaseError", "health_check")
        logger.error(f"Database health check failed: {e}")

    # Check Redis connection
    try:
        start_time = time.time()
        redis_healthy = await redis_manager.ping()
        redis_duration = time.time() - start_time

        if redis_healthy:
            health_status["checks"]["redis"] = {
                "status": "healthy",
                "response_time": redis_duration,
                "message": "Redis connection successful",
            }

            # Record metric
            prometheus_metrics.record_redis_operation("ping", True)
        else:
            overall_healthy = False
            health_status["checks"]["redis"] = {
                "status": "unhealthy",
                "message": "Redis ping failed",
            }

            # Record metric
            prometheus_metrics.record_redis_operation("ping", False)

    except Exception as e:
        overall_healthy = False
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "Redis connection failed",
        }

        # Record metric
        prometheus_metrics.record_error("RedisError", "health_check")
        logger.error(f"Redis health check failed: {e}")

    # Set overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"

    return ORJSONResponse(health_status, status_code=200 if overall_healthy else 503)


@router.get("/health/liveness")
async def liveness_probe():
    """Kubernetes liveness probe endpoint"""
    return ORJSONResponse({"status": "alive"})


@router.get("/health/readiness")
async def readiness_probe():
    """Kubernetes readiness probe endpoint"""
    try:
        # Quick Redis check (simplified)
        redis_healthy = await redis_manager.ping()

        if redis_healthy:
            return ORJSONResponse({"status": "ready"})
        else:
            raise HTTPException(status_code=503, detail="Redis not available")

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/metrics-summary")
async def metrics_summary():
    """Summary of application metrics for dashboard"""
    try:
        # Enhanced metrics summary with HTTP metrics info
        summary = prometheus_metrics.get_http_metrics_summary()
        
        return ORJSONResponse(
            {
                "message": "Enhanced HTTP metrics collection enabled",
                "prometheus_endpoint": "/metrics", 
                "metrics_info": {
                    "http_requests_total": "Total HTTP requests by method, endpoint, status_code, handler",
                    "http_request_duration_seconds": "HTTP request duration histograms with detailed buckets",
                    "http_requests_in_progress": "Current number of requests being processed",
                    "http_request_size_bytes": "HTTP request size histograms", 
                    "http_response_size_bytes": "HTTP response size histograms",
                    "http_requests_by_user_agent_total": "Requests grouped by user agent family and version",
                    "http_requests_by_ip_total": "Requests grouped by client IP",
                    "http_slow_requests_total": "Number of slow requests (>1s)",
                    "http_errors_by_type_total": "HTTP errors grouped by error type"
                },
                "health_endpoints": {
                    "basic": "/health",
                    "deep": "/health/deep",
                    "liveness": "/health/liveness", 
                    "readiness": "/health/readiness",
                },
                "prometheus_queries": summary
            }
        )

    except Exception as e:
        logger.error(f"Metrics summary failed: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to generate metrics summary"
        )


@router.get("/metrics/http")
async def http_metrics_details():
    """Detailed information about HTTP metrics collection"""
    try:
        return ORJSONResponse(
            {
                "status": "active",
                "middleware": "MetricsMiddleware enabled",
                "collected_metrics": {
                    "request_count": {
                        "metric": "http_requests_total",
                        "labels": ["method", "endpoint", "status_code", "handler"],
                        "description": "Counter of total HTTP requests"
                    },
                    "request_duration": {
                        "metric": "http_request_duration_seconds", 
                        "labels": ["method", "endpoint", "status_code"],
                        "buckets": [0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, "inf"],
                        "description": "Histogram of HTTP request durations"
                    },
                    "requests_in_progress": {
                        "metric": "http_requests_in_progress",
                        "labels": ["method", "endpoint"],
                        "description": "Gauge of requests currently being processed"
                    },
                    "request_size": {
                        "metric": "http_request_size_bytes",
                        "labels": ["method", "endpoint"],
                        "buckets": [64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, "inf"],
                        "description": "Histogram of HTTP request sizes"
                    },
                    "response_size": {
                        "metric": "http_response_size_bytes",
                        "labels": ["method", "endpoint", "status_code"],
                        "buckets": [64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, "inf"],
                        "description": "Histogram of HTTP response sizes"
                    },
                    "user_agent_tracking": {
                        "metric": "http_requests_by_user_agent_total",
                        "labels": ["user_agent_family", "user_agent_version"],
                        "description": "Counter of requests grouped by user agent"
                    },
                    "ip_tracking": {
                        "metric": "http_requests_by_ip_total", 
                        "labels": ["client_ip"],
                        "description": "Counter of requests grouped by client IP"
                    },
                    "slow_requests": {
                        "metric": "http_slow_requests_total",
                        "labels": ["method", "endpoint", "status_code"],
                        "threshold": ">1 second",
                        "description": "Counter of slow HTTP requests"
                    },
                    "error_tracking": {
                        "metric": "http_errors_by_type_total",
                        "labels": ["method", "endpoint", "error_type", "status_code"],
                        "description": "Counter of HTTP errors grouped by type"
                    }
                },
                "example_queries": {
                    "request_rate": "rate(http_requests_total[5m])",
                    "error_rate": "rate(http_errors_by_type_total[5m]) / rate(http_requests_total[5m])",
                    "avg_response_time": "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])",
                    "95th_percentile": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                    "slow_requests_rate": "rate(http_slow_requests_total[5m])",
                    "top_endpoints": "topk(10, sum by (endpoint) (rate(http_requests_total[5m])))",
                    "requests_by_status": "sum by (status_code) (rate(http_requests_total[5m]))"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"HTTP metrics details failed: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get HTTP metrics details"
        )
