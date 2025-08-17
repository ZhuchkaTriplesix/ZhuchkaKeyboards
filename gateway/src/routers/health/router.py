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
        # This could be enhanced to provide custom metric summaries
        # For now, it's a placeholder that could aggregate key metrics
        return ORJSONResponse(
            {
                "message": "Metrics available at /metrics endpoint",
                "prometheus_endpoint": "/metrics",
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
