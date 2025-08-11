from pydantic import BaseModel


class ErrorBase(BaseModel):
    detail: str
    error_type: str | None = None


class BadRequestError(ErrorBase):
    """400 Bad Request"""

    class Config:
        schema_extra = {
            "example": {
                "detail": "Invalid request parameters",
                "error_type": "validation_error",
            }
        }


class UnauthorizedError(ErrorBase):
    """401 Unauthorized"""

    class Config:
        schema_extra = {
            "example": {"detail": "Not authenticated", "error_type": "auth_error"}
        }


class ForbiddenError(ErrorBase):
    """403 Forbidden"""

    class Config:
        schema_extra = {
            "example": {"detail": "Permission denied", "error_type": "permission_error"}
        }


class NotFoundError(ErrorBase):
    """404 Not Found"""

    class Config:
        schema_extra = {
            "example": {"detail": "Resource not found", "error_type": "not_found"}
        }


class TooManyRequestsError(ErrorBase):
    """429 Too Many Requests"""

    retry_after: int

    class Config:
        schema_extra = {
            "example": {
                "detail": "Rate limit exceeded",
                "error_type": "rate_limit",
                "retry_after": 30,
            }
        }


class InternalError(ErrorBase):
    """500 Internal Server Error"""

    class Config:
        schema_extra = {
            "example": {"detail": "Internal server error", "error_type": "server_error"}
        }
