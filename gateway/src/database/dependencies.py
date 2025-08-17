from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.core import get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]


# Alternative alias
def get_session(request) -> AsyncSession:
    """Get database session from request state."""
    return get_db(request)
