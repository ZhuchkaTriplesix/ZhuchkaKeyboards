import os

class PostgresCfg:
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", 5432))
    user: str = os.getenv("POSTGRES_USER", "postgres")
    password: str = os.getenv("POSTGRES_PASSWORD", "password")
    db: str = os.getenv("POSTGRES_DB", "postgres")
    
    @classmethod
    def dsn(cls) -> str:
        return f"postgresql://{cls.user}:{cls.password}@{cls.host}:{cls.port}/{cls.db}" 