from pydantic import BaseModel
from datetime import datetime


class ComponentsDantic(BaseModel):
    name: str
    type: str


class EmloyeeDantic(BaseModel):
    name: str
    surname: str
    group: str | None = None
    salary: float | None = None
    contract_end: datetime | None = None


class ProductDantic(BaseModel):
    name: str
    category: str | None = None
    price: float


class BankDantic(BaseModel):
    name: str


class DistributorDantic(BaseModel):
    name: str
    deliver_service: str


class ServiceDantic(BaseModel):
    name: str
    price: float
