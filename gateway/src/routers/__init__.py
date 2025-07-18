from dataclasses import dataclass
from routers.auth.router import router as auth_router


@dataclass(frozen=True)
class Router:
    routers = [
        (auth_router, "/api/auth", ["auth"]),   
    ]