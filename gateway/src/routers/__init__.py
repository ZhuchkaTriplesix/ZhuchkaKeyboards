from dataclasses import dataclass
from routers.user.router import router as user_router
from routers.health.router import router as health_router
<<<<<<< HEAD
from routers.inventory.router import router as inventory_router
=======
>>>>>>> performance-optimizations


@dataclass(frozen=True)
class Router:
    routers = [
<<<<<<< HEAD
        (user_router, "/api/user", ["user"]),
        (health_router, "/api", ["health"]),
        (inventory_router, "/api/inventory", ["inventory"]),
=======
        (health_router, "/api/health", ["health"]),
        (user_router, "/api/user", ["user"]),
>>>>>>> performance-optimizations
    ]
