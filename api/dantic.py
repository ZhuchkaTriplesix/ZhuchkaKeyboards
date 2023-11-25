from pydantic import BaseModel
from datetime import datetime


class ComponentsDantic(BaseModel):
    name: str | None = None
    type: str | None = None


class EmloyeeDantic(BaseModel):
    first_name: str | None = None
    second_name: str | None = None
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
    name: str | None = None
    deliver_service: str | None = None


class ServiceDantic(BaseModel):
    name: str | None = None
    price: float | None = None


class CustomerDantic(BaseModel):
    vendor_id: int
    vendor_type: int | None = None
    name: str | None = None
    surname: str | None = None
    username: str | None = None
    email: str | None = None
