from sqlalchemy import Column, String, Integer, DateTime, BigInteger, Float, ForeignKey, Boolean
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, relationship
import datetime
from config import database
from enum import Enum

Base = declarative_base()

engine = create_engine(database, echo=False)

Session = sessionmaker(bind=engine)
session = scoped_session(Session)
conn = engine.connect()


class Platform(Enum):
    TELEGRAM = 1
    VK = 2


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


# noinspection PyShadowingBuiltins,PyMethodParameters
class CustomerCrud:
    def get_customer(vendor_id: int) -> object:
        sess = Session()
        customer = sess.query(Customers).where(Customers.vendor_id == vendor_id).first()
        if customer is not None:
            sess.close()
            return customer
        else:
            sess.close()
            return None

    def add_customer(vendor_id: int, vendor_type: int, first_name: str, second_name: str, username) -> object:
        sess = Session()
        customer = sess.query(Customers).where(Customers.vendor_id == vendor_id).first()
        if customer is None:
            customer = Customers(vendor_id=vendor_id, vendor_type=vendor_type, first_name=first_name,
                                 second_name=second_name, username=username)
            sess.add(customer)
            sess.commit()
            sess.close()
            return True
        else:
            return False

    def update_customer_email(vendor_id: int, email: str) -> object:
        sess = Session()
        try:
            customer = sess.query(Customers).where(Customers.vendor_id == vendor_id).first()
            customer.email = email
            customer.updated_date = datetime.datetime.utcnow()
            sess.commit()
            sess.close()
            return True
        except ProgrammingError:
            return False

    def delete_customer(id: int) -> object:
        sess = Session()
        try:
            customer = sess.query(Customers).where(Customers.id == id).first()
            sess.delete(customer)
            sess.commit()
            sess.close()
            return True
        except ProgrammingError:
            return False


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


class EmployeesCrud:
    def add_emp(group: str, first_name: str, second_name: str, salary: float):
        sess = Session()
        employee = sess.query(Employees).where(
            and_(Employees.first_name == first_name, Employees.second_name == second_name)).first()
        if employee is not None:
            pass
        else:
            emp = Employees(first_name=first_name, second_name=second_name, group=group,
                            salary=salary)
            sess.add(emp)
            sess.commit()
        sess.close()

    def update_emp_group(id: int, group: str):
        sess = Session()
        emp = sess.query(Employees).where(Employees.id == id).first()
        emp.group = group
        sess.commit()
        sess.close()

    def update_contract_end(id, contract_end):
        sess = Session()
        emp = sess.query(Employees).where(Employees.id == id).first()
        emp.contract_end = contract_end
        sess.commit()
        sess.close()

    def delete_emp(id: int):
        sess = Session()
        emp = sess.query(Employees).where(Employees.id == id).first()
        sess.delete(emp)
        sess.commit()
        sess.close()


class Logs(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    operation_name = Column(String(length=16))
    date = Column(DateTime, default=datetime.datetime.utcnow)


class LogsCrud:
    def add_log(employee_id: int, operation: str):
        sess = Session()
        log = Logs(employee_id=employee_id, operation=operation)
        sess.add(log)
        sess.commit()
        sess.close()


class Components(Base):
    __tablename__ = "components"
    id = Column(Integer, primary_key=True)
    component_name = Column(String(length=16))
    component_type = Column(String(length=12))
    usage = relationship('ComponentUsage')
    usage1 = relationship('Supplies')


class ComponentCrud:
    def add_component(component_name: str, component_type: str) -> object:
        sess = Session()
        comp = sess.query(Components).where(Components.component_name == component_name).first()
        if comp is not None:
            return False
        else:
            component = Components(component_name=component_name, component_type=component_type)
            sess.add(component)
            sess.commit()
            sess.close()
            return True

    def delete_component(component_name: str) -> object:
        sess = Session()
        try:
            comp = sess.query(Components).where(Components.component_name == component_name).first()
            sess.delete(comp)
            sess.commit()
        except Exception as e:
            print(e)
        finally:
            sess.close()


class ComponentUsage(Base):
    __tablename__ = "component_usage"
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey('components.id'))
    usage_name = Column(String(length=16))
    usage_count = Column(Float)
    task_id = Column(Integer, ForeignKey('tasks.id'))


class ComponentUsageCrud:
    def add(component_id: int, usage_name: str, usage_count: float, task_id: int):
        sess = Session()
        comp = ComponentUsage(component_id=component_id, usage_name=usage_name, usage_count=usage_count,
                              task_id=task_id)
        sess.add(comp)
        sess.commit()
        sess.close()


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
    product_name = Column(String(length=16))
    product_price = Column(Float)
    usage = relationship('Orders')


class ProductsCrud:
    def add(product_name: str, product_price: float):
        sess = Session()
        prod = sess.query(Products).where(Products.product_name == product_name).first()
        if prod is not None:
            pass
        else:
            prod = Products(product_name=product_name, product_price=product_price)
            sess.add(prod)
            sess.commit()
            sess.close()

    def get_product(product_name: str) -> object:
        sess = Session()
        prod = sess.query(Products).where(Products.product_name == product_name).first()
        if prod is not None:
            prod = (prod.id, prod.product_name, prod.product_price)
            sess.close()
            return prod
        else:
            sess.close()
            return None

    def delete_product(product_name: str) -> object:
        sess = Session()
        prod = sess.query(Products).where(Products.product_name == product_name).first()
        if prod is not None:
            sess.delete(prod)
            sess.commit()
            sess.close()
            return True
        else:
            sess.close()
            return False

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
