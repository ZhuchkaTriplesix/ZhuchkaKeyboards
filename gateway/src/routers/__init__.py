from dataclasses import dataclass
from routers.user.router import router as user_router
from routers.health.router import router as health_router


@dataclass(frozen=True)
class Router:
    routers = [
        (health_router, "/api/health", ["health"]),
        (user_router, "/api/user", ["user"]),
    ]
