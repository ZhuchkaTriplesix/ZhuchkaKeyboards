import re

from sqlalchemy import inspect, make_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import declared_attr, declarative_base
from starlette.requests import Request

from config import postgres_cfg
from database.logging import SessionTracker


def create_db_engine(connection_string: str) -> AsyncEngine:
    """Create a database engine with proper timeout settings.

    Args:
        connection_string: Database connection string
    """
    url = make_url(connection_string)

    # Use existing configuration values with fallbacks
    timeout_kwargs = {
        # Connection timeout - how long to wait for a connection from the pool
        "pool_timeout": postgres_cfg.database_engine_pool_timeout,
        # Recycle connections after this many seconds
        "pool_recycle": postgres_cfg.database_engine_pool_recycle,
        # Maximum number of connections to keep in the pool
        "pool_size": postgres_cfg.database_engine_pool_size,
        # Maximum overflow connections allowed beyond pool_size
        "max_overflow": postgres_cfg.database_engine_max_overflow,
        # Connection pre-ping to verify connection is still alive
        "pool_pre_ping": postgres_cfg.database_engine_pool_ping,
        # Enables/Disables engine logging.
        "echo": postgres_cfg.database_echo,
    }
    return create_async_engine(url=url, **timeout_kwargs)


# Create the default engine with standard timeout
engine = create_db_engine(postgres_cfg.url)


def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)
    return "_".join([x.lower() for x in names if x])


class CustomBase:
    __repr_attrs__ = []
    __repr_max_length__ = 15

    @declared_attr
    def __tablename__(cls):
        return resolve_table_name(cls.__name__)

    def dict(self):
        """Returns a dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @property
    def _id_str(self):
        ids = inspect(self).identity
        return (
            "-".join([str(x) for x in ids])
            if ids and len(ids) > 1
            else str(ids[0])
            if ids
            else "None"
        )

    @property
    def _repr_attrs_str(self):
        max_length = self.__repr_max_length__

        values = []
        single = len(self.__repr_attrs__) == 1
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError(
                    f"{self.__class__} has incorrect attribute '{key}' in __repr__attrs__"
                )
            value = getattr(self, key)
            wrap_in_quote = isinstance(value, str)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + "..."

            if wrap_in_quote:
                value = f"'{value}'"
            values.append(value if single else f"{key}:{value}")

        return " ".join(values)

    def __repr__(self):
        id_str = f"#{self._id_str}" if self._id_str else ""
        return f"<{self.__class__.__name__} {id_str} {self._repr_attrs_str if self._repr_attrs_str else ''}>"


Base = declarative_base(cls=CustomBase)


def get_db(request: Request) -> AsyncSession:
    """Get database session from request state."""
    session = request.state.db
    if not hasattr(session, "_dispatch_session_id"):
        session._dispatch_session_id = SessionTracker.track_session(
            session, context="fastapi_request"
        )
    return session
