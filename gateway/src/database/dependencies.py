from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from database.core import get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]