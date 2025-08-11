import os
from abc import ABC
from dataclasses import asdict, dataclass


class CfgBase(ABC):
    dict: callable = asdict


@dataclass
class RedisCfg(CfgBase):
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    db: int = int(os.getenv("REDIS_DB", "0"))
    password: str = os.getenv("REDIS_PASSWORD", "")


@dataclass
class JWTCfg(CfgBase):
    jwt_secret: str = os.getenv("JWT_SECRET")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_exp: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


@dataclass
class PostgresCfg(CfgBase):
    host: str = os.getenv("POSTGRES_HOST")
    port: str = os.getenv("POSTGRES_PORT")
    user: str = os.getenv("POSTGRES_USER")
    password: str = os.getenv("POSTGRES_PASSWORD")
    db: str = os.getenv("POSTGRES_DB")
    database_engine_pool_timeout: int = int(os.getenv("POSTGRES_POOL_TIMEOUT", 30))
    database_engine_pool_recycle: int = int(os.getenv("POSTGRES_POOL_RECYCLE", 1800))
    database_engine_pool_size: int = int(os.getenv("POSTGRES_POOL_SIZE", 10))
    database_engine_max_overflow: int = int(os.getenv("POSTGRES_MAX_OVERFLOW", 20))
    database_engine_pool_ping: bool = bool(int(os.getenv("POSTGRES_POOL_PING", 1)))
    database_echo: bool = bool(int(os.getenv("POSTGRES_ECHO", 0)))

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


jwt_cfg = JWTCfg()
redis_cfg = RedisCfg()
postgres_cfg = PostgresCfg()
