from sqlalchemy import Column, String, Integer, DateTime, BigInteger, Float, ForeignKey, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, relationship
import datetime
from config import database


Base = declarative_base()

engine = create_engine(database, echo=False)

Session = sessionmaker(bind=engine)
session = scoped_session(Session)
conn = engine.connect()


class TelegramUsers(Base):
    __tablename__ = "telegram_users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String(length=32))
    group = Column(Integer)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


class Customers(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    vendor_id = Column(BigInteger)
    vendor_type = Column(Integer)
    first_name = Column(String(length=16))
    second_name = Column(String(length=16))
    username = Column(String(length=32))
    email = Column(String, default=None)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date = Column(DateTime, default=None)
    usage = relationship('Orders')
    usage1 = relationship('ServiceOrders')


class Employees(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(length=16))
    second_name = Column(String(length=16))
    group = Column(String(length=8))
    salary = Column(Float)
    contract_start = Column(DateTime, default=datetime.datetime.utcnow)
    contract_end = Column(DateTime)
    logs = relationship('Logs')
    usages = relationship('Orders')
    usage1 = relationship('Tasks')
    usage2 = relationship('ServiceOrders')


class Logs(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    operation_name = Column(String(length=16))
    date = Column(DateTime, default=datetime.datetime.utcnow)


class Components(Base):
    __tablename__ = "components"
    id = Column(Integer, primary_key=True)
    component_name = Column(String(length=16))
    component_type = Column(String(length=12))
    usage = relationship('ComponentUsage')
    usage1 = relationship('Supplies')


class ComponentUsage(Base):
    __tablename__ = "component_usage"
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey('components.id'))
    usage_name = Column(String(length=16))
    usage_count = Column(Float)
    task_id = Column(Integer, ForeignKey('tasks.id'))


class Orders(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    manager_id = Column(Integer, ForeignKey('employees.id'))
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    usage = relationship('Tasks')


class Transactions(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    payment = Column(Integer)
    status = Column(Boolean)
    bank_id = Column(Integer, ForeignKey('banks.id'))
    card_type = Column(Integer)
    usage = relationship('Orders')
    usage1 = relationship('ServiceOrders')


class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=16))
    category = Column(String)
    product_price = Column(Float)
    usage = relationship('Orders')


class Services(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=16))
    service_price = Column(Float)
    usage = relationship('ServiceOrders')


class ServiceOrders(Base):
    __tablename__ = "service_orders"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('services.id'))
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    manager_id = Column(Integer, ForeignKey('employees.id'))
    usage = relationship('Tasks')


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    service_order_id = Column(Integer, ForeignKey('service_orders.id'))
    worker_id = Column(Integer, ForeignKey('employees.id'))
    status = Column(Integer)
    type = Column(Integer)
    usage = relationship('ComponentUsage')


class Distributors(Base):
    __tablename__ = 'distributors'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=16))
    deliver_service = Column(String(length=16))
    relationship('Supplies')


class Supplies(Base):
    __tablename__ = 'supplies'
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey('components.id'))
    count = Column(Float)
    distributor = Column(Integer, ForeignKey('distributors.id'))


class Banks(Base):
    __tablename__ = 'banks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    usage = relationship('Transactions')


Base.metadata.create_all(engine)
