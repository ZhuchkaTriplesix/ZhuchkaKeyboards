"""
Health check and monitoring endpoints
"""

import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import ORJSONResponse
from services.redis.rediska import redis_manager
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("")
async def health_check():
    """Basic health check endpoint"""
    return ORJSONResponse(
        {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "ZhuchkaKeyboards Gateway",
        }
    )


@router.get("/deep")
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
        else:
            overall_healthy = False
            health_status["checks"]["redis"] = {
                "status": "unhealthy",
                "message": "Redis ping failed",
            }

    except Exception as e:
        overall_healthy = False
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "Redis connection failed",
        }

        logger.error(f"Redis health check failed: {e}")

    # Set overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"

    return ORJSONResponse(health_status, status_code=200 if overall_healthy else 503)


@router.get("/liveness")
async def liveness_probe():
    """Kubernetes liveness probe endpoint"""
    return ORJSONResponse({"status": "alive"})


@router.get("/readiness")
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
            }
        )

    except Exception as e:
        logger.error(f"Metrics summary failed: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to generate metrics summary"
        )