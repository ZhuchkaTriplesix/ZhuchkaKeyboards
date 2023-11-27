from pydantic import BaseModel
from datetime import datetime


class ComponentsDantic(BaseModel):
    id: int | None = None
    name: str | None = None
    type: str | None = None


class EmployeeDantic(BaseModel):
    id: int
    first_name: str
    second_name: str
    group: str
    salary: float
    contract_end: datetime | None = None


class ProductDantic(BaseModel):
    id: int | None = None
    name: str | None = None
    category: str | None = None
    price: float | None = None


class BankDantic(BaseModel):
    id: int | None = None
    name: str | None = None


class DistributorDantic(BaseModel):
    id: int | None = None
    name: str | None = None
    deliver_service: str | None = None


class ServiceDantic(BaseModel):
    id: int | None = None
    name: str | None = None
    price: float | None = None


class CustomerDantic(BaseModel):
    id: int
    vendor_id: int
    vendor_type: int
    first_name: str
    second_name: str
    username: str
    email: str | None = None


class TransactionDantic(BaseModel):
    id: int | None = None
    payment: int
    status: bool | None = False
    bank_id: int
    card_type: int


class OutputTransaction(BaseModel):
    id: int
    payment: int
    status: bool | None = False
    card_type: str
    bank: BankDantic


class OrderDantic(BaseModel):
    id: int | None = None
    customer_id: int
    manager_id: int | None = None
    transaction_id: int
    product_id: int


class OutputOrder(BaseModel):
    id: int
    customer: CustomerDantic
    manager: EmployeeDantic | None = None
    transaction: OutputTransaction
    product: ProductDantic


class ServiceOrderDantic(BaseModel):
    id: int | None = None
    customer_id: int
    manager_id: int | None = None
    transaction_id: int
    service_id: int


class OutputServiceOrder(BaseModel):
    id: int
    customer: CustomerDantic
    manager: EmployeeDantic | None = None
    transaction: OutputTransaction
    service: ServiceDantic


class SupplyDantic(BaseModel):
    id: int | None = None
    component_id: int
    count: float
    distributor: int


class OutputSupplyDantic(BaseModel):
    id: int
    component: ComponentsDantic
    count: float
    distributor: DistributorDantic
