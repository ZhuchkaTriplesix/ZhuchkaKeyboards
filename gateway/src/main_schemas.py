from uuid import UUID

from pydantic import BaseModel
from pydantic_config import default_config


class User(BaseModel):
    user_id: UUID
    email: str
    permission: str


class TestSchema(BaseModel):
    hello: str

    model_config = default_config
