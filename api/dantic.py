from pydantic import BaseModel


class ComponentsDantic(BaseModel):
    name: str
    type: str


class EmloyeeDantic(BaseModel):
    name: str
    surname: str
    group: str
    salary: float


class ProductDantic(BaseModel):
    name: str
    category: str | None = None
    price: float
