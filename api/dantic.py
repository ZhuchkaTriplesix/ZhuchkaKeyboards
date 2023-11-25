from pydantic import BaseModel
from datetime import datetime


class ComponentsDantic(BaseModel):
    name: str
    type: str


class EmloyeeDantic(BaseModel):
    first_name: str
    second_name: str
    group: str | None = None
    salary: float | None = None
    contract_end: datetime | None = None


class ProductDantic(BaseModel):
    name: str | None = None
    category: str | None = None
    price: float | None = None


class BankDantic(BaseModel):
    name: str


class DistributorDantic(BaseModel):
    name: str
    deliver_service: str


class ServiceDantic(BaseModel):
    name: str
    price: float


class CustomerDantic(BaseModel):
    vendor_id: int
    vendor_type: int
    name: str
    surname: str
    username: str
    email: str | None = None
