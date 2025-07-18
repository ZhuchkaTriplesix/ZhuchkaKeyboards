import os
from abc import ABC
from dataclasses import asdict, dataclass
from typing import Optional


class CfgBase(ABC):
    dict: callable = asdict


@dataclass
class RedisCfg(CfgBase):
    host: str = os.getenv("REDIS_HOST")
    port: int = os.getenv("REDIS_PORT")
    db: int = os.getenv("REDIS_DB")
    password: str = os.getenv("REDIS_PASSWORD")



@dataclass
class JWTCfg(CfgBase):
    jwt_secret: str = os.getenv("JWT_SECRET")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_exp: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

class PostgresCfg(CfgBase):
    host: str = os.getenv("POSTGRES_HOST")
    port: str = os.getenv("POSTGRES_PORT")
    user: str = os.getenv("POSTGRES_USER")
    password: str = os.getenv("POSTGRES_PASSWORD")
    db: str = os.getenv("POSTGRES_DB")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{int(self.port)}/{self.db}"

jwt_cfg = JWTCfg()
redis_cfg = RedisCfg()
postgres_cfg = PostgresCfg()
