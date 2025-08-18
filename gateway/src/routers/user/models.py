import uuid
from uuid import UUID
from typing import Optional
from sqlalchemy import types, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.core import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(types.UUID, primary_key=True, default=uuid.uuid4)

    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_verify: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
