from dataclasses import dataclass
from routers.user.router import router as user_router


@dataclass(frozen=True)
class Router:
    routers = [
        (user_router, "/api/user", ["user"]),   
    ]