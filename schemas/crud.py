from pydantic import BaseModel
from datetime import datetime


class Component(BaseModel):
    name: str
    type: str


class ComponentInDb(Component):
    id: int
    data: Component


class Employee(BaseModel):
    name: str
    second_name: str
    group: str
    salary: float
    contract_end_date: datetime


class EmployeeInDb(Employee):
    id: int
    data: Employee


class Product(BaseModel):
    name: str
    category: str
    price: float


class ProductInDb(Product):
    id: int
    data: Product


class Bank(BaseModel):
    name: str


class BankInDb(Bank):
    id: int
    data: Bank


class Distributor(BaseModel):
    name: str
    deliver_service: str


class DistributorInDb(Distributor):
    id: int
    data: Distributor


class Service(BaseModel):
    name: str
    price: float


class ServiceInDb(Service):
    id: int
    data: Service


class Customer(BaseModel):
    name: str
    second_name: str
    address: str
    city: str
    state: str
    country: str
    phone: str
    email: str


class CustomerInDb(Customer):
    id: int
    data: Customer


class Transaction(BaseModel):
    payment_date: datetime
    customer: CustomerInDb
    service: ServiceInDb | None = None
    product: ProductInDb | None = None
    bank: BankInDb


class TransactionInDb(Transaction):
    id: int
    data: Transaction


