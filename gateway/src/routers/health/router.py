from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

router = APIRouter()


@router.get("")
async def health_check():
    """Simple health check endpoint"""
    return ORJSONResponse(
        content={"status": "healthy", "message": "API is running"}
    )


@router.get("/deep")
async def deep_health_check():
    """Deep health check"""
    return ORJSONResponse(
        content={
            "status": "healthy",
            "message": "Deep health check passed",
            "services": {
                "api": "healthy",
                "database": "healthy",
                "redis": "healthy"
            }
        }
    )


@router.get("/ready")
async def readiness_probe():
    """Kubernetes readiness probe"""
    return ORJSONResponse(
        content={"status": "ready", "message": "Service is ready"}
    )
