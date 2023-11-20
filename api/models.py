from sqlalchemy import Column, String, Integer, DateTime, BigInteger, Float, ForeignKey, Boolean
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, relationship
from sqlalchemy.sql import func
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


class Group(Enum):
    ENGINEER = 1
    MANAGER = 2
    HIGH_MANAGER = 3


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


# noinspection PyShadowingBuiltins,PyMethodParameters,PyTypeChecker
class CustomerCrud:
    @staticmethod
    def get_customer(vendor_id: int) -> object:
        sess = Session()
        customer = sess.query(Customers).where(Customers.vendor_id == vendor_id).first()
        if customer is not None:
            sess.close()
            return customer
        else:
            sess.close()
            return None

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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


# noinspection PyTypeChecker
class EmployeesCrud:
    @staticmethod
    def add_emp(group: str, first_name: str, second_name: str, salary: float):
        sess = Session()
        employee = sess.query(Employees).where(
            and_(Employees.first_name == first_name, Employees.second_name == second_name)).first()
        if employee is not None:
            sess.close()
            return False
        else:
            emp = Employees(first_name=first_name, second_name=second_name, group=group,
                            salary=salary)
            sess.add(emp)
            sess.commit()
            sess.close()
            return True

    @staticmethod
    def get_emp(first_name: str, second_name: str):
        sess = Session()
        try:
            emp = sess.query(Employees).where(
                and_(Employees.first_name == first_name, Employees.second_name == second_name)).first()
            id = emp.id
            name = emp.first_name
            surname = emp.second_name
            salary = emp.salary
            employee = {"id": id, "name": name, "surname": surname, "salary": salary}
            return employee
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()

    @staticmethod
    def update_emp_group(id: int, group: str):
        sess = Session()
        emp = sess.query(Employees).where(Employees.id == id).first()
        emp.group = group
        sess.commit()
        sess.close()

    @staticmethod
    def update_contract_end(id, contract_end):
        sess = Session()
        emp = sess.query(Employees).where(Employees.id == id).first()
        emp.contract_end = contract_end
        sess.commit()
        sess.close()

    @staticmethod
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
    @staticmethod
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


# noinspection PyTypeChecker
class ComponentCrud:
    @staticmethod
    def add_component(component_name: str, component_type: str) -> object:
        sess = Session()
        comp = sess.query(Components).where(Components.component_name == component_name).first()
        if comp is not None:
            return False
        else:
            component = Components(component_name=component_name, component_type=component_type)
            sess.add(component)
            sess.commit()
            component = {"Name": component.component_name, "Type": component.component_type}
            sess.close()
            return component

    @staticmethod
    def delete_component(id: int) -> object:
        sess = Session()
        try:
            comp = sess.query(Components).where(Components.id == id).first()
            sess.delete(comp)
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()

    @staticmethod
    def get_component(component_name: str, component_type: str):
        sess = Session()
        try:
            comp = sess.query(Components).where(
                and_(Components.component_name == component_name, Components.component_type == component_type)).first()
            component = {"id": comp.id, "name": comp.component_name, "type": comp.component_type}
            return component
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()


class ComponentUsage(Base):
    __tablename__ = "component_usage"
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey('components.id'))
    usage_name = Column(String(length=16))
    usage_count = Column(Float)
    task_id = Column(Integer, ForeignKey('tasks.id'))


# noinspection PyTypeChecker
class ComponentUsageCrud:
    @staticmethod
    def add(component_id: int, usage_name: str, usage_count: float, task_id: int):
        sess = Session()
        comp = ComponentUsage(component_id=component_id, usage_name=usage_name, usage_count=usage_count,
                              task_id=task_id)
        sess.add(comp)
        sess.commit()
        sess.close()

    @staticmethod
    def get_count(component_id: int) -> object:
        sess = Session()
        try:
            count = sess.query(func.sum(ComponentUsage.usage_count)).filter(
                ComponentUsage.component_id == component_id).all()
            return count[0][0]
        except Exception as e:
            print(e)
            return None
        finally:
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


# noinspection PyTypeChecker
class OrdersCrud:
    @staticmethod
    def add(customer_id: int, transaction_id: int, product_id: int):
        sess = Session()
        order = Orders(customer_id=customer_id, transaction_id=transaction_id, product_id=product_id)
        sess.add(order)
        sess.commit()
        sess.close()

    @staticmethod
    def add_manager(id: int, manager_id: int):
        sess = Session()
        order = sess.query(Orders).where(Orders.id == id).first()
        order.manager_id = manager_id
        sess.commit()
        sess.close()

    @staticmethod
    def get_order(customer_id: int, product_id: int) -> object:
        sess = Session()
        order = sess.query(Orders).where(and_(Orders.customer_id == customer_id, product_id == product_id)).first()
        if order is not None:
            answer = {"id": order.id, "customer_id": order.customer_id, "manager_id": order.manager_id,
                      "transaction_id": order.transaction_id, "product_id": order.product_id}
            return answer
        else:
            return False


class Transactions(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    payment = Column(Integer)
    status = Column(Boolean)
    bank_id = Column(Integer, ForeignKey('banks.id'))
    card_type = Column(Integer)
    usage = relationship('Orders')
    usage1 = relationship('ServiceOrders')


class TransactionsCrud:
    @staticmethod
    def add(payment: int, status: bool, bank_id: int, card_type: int):
        sess = Session()
        try:
            transaction = Transactions(payment=payment, status=status, bank_id=bank_id, card_type=card_type)
            sess.add(transaction)
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()

    @staticmethod
    def get_last_transaction():
        sess = Session()
        try:
            trans = sess.query(Transactions).order_by(Transactions.id.desc()).first()
            answer = {"id": trans.id, "payment": trans.payment, "status": trans.status, "bank": trans.bank_id,
                      "card": trans.card_type}
            return answer
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()


class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    product_name = Column(String(length=16))
    product_price = Column(Float)
    usage = relationship('Orders')


# noinspection PyTypeChecker
class ProductsCrud:
    @staticmethod
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

    @staticmethod
    def get_product(product_name: str) -> object:
        sess = Session()
        prod = sess.query(Products).where(Products.product_name == product_name).first()
        if prod is not None:
            product = {"id": prod.id, "name:": prod.product_name, "price": prod.product_price}
            sess.close()
            return product
        else:
            sess.close()
            return False

    @staticmethod
    def delete_product(product_name: str) -> object:
        sess = Session()
        prod = ProductsCrud.get_product(product_name)
        if prod is not False:
            sess.delete(prod)
            sess.commit()
            sess.close()
            return True
        else:
            sess.close()
            return False

    @staticmethod
    def update_product_price(product_name: str, product_price) -> object:
        sess = Session()
        prod = sess.query(Products).where(Products.product_name == product_name).first()
        if prod is not None:
            prod.product_price = product_price
            sess.commit()
            product = {"name": product_name, "price": product_price}
            sess.close()
            return product
        else:
            return False


class Services(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=16))
    service_price = Column(Float)
    usage = relationship('ServiceOrders')


# noinspection PyTypeChecker
class ServicesCrud:
    @staticmethod
    def add(name: str, service_price: float) -> object:
        sess = Session()
        ser = sess.query(Services).where(Services.name == name).first()
        if ser is not None:
            sess.close()
            return False
        else:
            ser = Services(name=name, service_price=service_price)
            sess.add(ser)
            sess.commit()
            sess.close()
            return True

    @staticmethod
    def get_service(name: str) -> object:
        sess = Session()
        ser = sess.query(Services).where(Services.name == name).first()
        if ser is not None:
            answer = {"id": ser.id, "name": ser.name, "price": ser.service_price}
            sess.close()
            return answer
        else:
            sess.close()
            return False

    @staticmethod
    def get_service_price(name: str) -> object:
        sess = Session()
        ser = sess.query(Services).where(Services.name == name).first()
        if ser is not None:
            price = ser.service_price
            sess.close()
            return price
        else:
            sess.close()
            return None

    @staticmethod
    def delete_service(name: str) -> object:
        sess = Session()
        ser = sess.query(Services).where(Services.name == name).first()
        if ser is None:
            sess.close()
            return False
        else:
            sess.delete(ser)
            sess.commit()
            sess.close()
            return True

    @staticmethod
    def update_service_price(name: str, service_price: float):
        sess = Session()
        ser = sess.query(Services).where(Services.name == name).first()
        if ser is not None:
            ser.service_price = service_price
            sess.commit()
            sess.close()
        else:
            sess.close()


class ServiceOrders(Base):
    __tablename__ = "service_orders"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('services.id'))
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    manager_id = Column(Integer, ForeignKey('employees.id'))
    usage = relationship('Tasks')


# noinspection PyTypeChecker


class ServiceOrdersCrud:
    @staticmethod
    def add(service_id: int, transaction_id: int, customer_id: int):
        sess = Session()
        try:
            order = ServiceOrders(service_id=service_id, transaction_id=transaction_id, customer_id=customer_id,
                                  manager_id=None)
            sess.add(order)
            sess.commit()
            answer = {"status": "200", "answer": "Successful add"}
            return answer
        except Exception as e:
            print(e)
            answer = {"status": "400", "answer": "error"}
            return answer
        finally:
            sess.close()

    @staticmethod
    def update_manager(id: int, manager_id: int):
        sess = Session()
        order = sess.query(ServiceOrders).where(ServiceOrders.id == id).first()
        if order is not None:
            order.manager_id = manager_id
            sess.commit()
            sess.close()
        else:
            sess.close()


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    service_order_id = Column(Integer, ForeignKey('service_orders.id'))
    worker_id = Column(Integer, ForeignKey('employees.id'))
    status = Column(Integer)
    type = Column(Integer)
    usage = relationship('ComponentUsage')


# noinspection PyTypeChecker
class TasksCrud:
    @staticmethod
    def add_task(order_id: int, worker_id: int) -> object:
        sess = Session()
        try:
            task = Tasks(order_id=order_id, service_order_id=None, worker_id=worker_id, status=1, type=1)
            sess.add(task)
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()

    @staticmethod
    def add_ser_task(order: int, worker: int) -> object:
        sess = Session()
        try:
            task = Tasks(order_id=None, service_order_id=order, worker_id=worker, status=1, type=2)
            sess.add(task)
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()

    @staticmethod
    def change_status(order_id: int, service_order_id: int, status: int):
        sess = Session()
        if order_id is None:
            task = sess.query(Tasks).where(Tasks.service_order_id == service_order_id).first()
            if task is not None:
                task.status = status
                sess.commit()
                sess.close()
            else:
                sess.close()
        else:
            task = sess.query(Tasks).where(Tasks.order_id == order_id).first()
            if task is not None:
                task.status = status
                sess.commit()
                sess.close()
            else:
                sess.close()

    @staticmethod
    def add_worker(order_id: int, service_order_id: int, worker_id: int):
        sess = Session()
        if order_id is None:
            task = sess.query(Tasks).where(Tasks.service_order_id == service_order_id).first()
            if task is not None:
                task.worker_id = worker_id
                sess.commit()
                sess.close()
            else:
                sess.close()
        else:
            task = sess.query(Tasks).where(Tasks.order_id == order_id).first()
            if task is not None:
                task.worker_id = worker_id
                sess.commit()
                sess.close()
            else:
                sess.close()

    @staticmethod
    def get_task_order(order_id):
        sess = Session()
        task = sess.query(Tasks).where(Tasks.order_id == order_id).first()
        if task is not None:
            answer = {"id": task.id, "order": task.order_id, "status": task.status, "type": task.type}
            return answer
        else:
            return False


class Distributors(Base):
    __tablename__ = 'distributors'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=16))
    deliver_service = Column(String(length=16))
    relationship('Supplies')


# noinspection PyTypeChecker
class DistributorsCrud:
    @staticmethod
    def add(name: str, deliver_service: str) -> object:
        sess = Session()
        dist = sess.query(Distributors).where(Distributors.name == name).first()
        if dist is not None:
            sess.close()
            return False
        else:
            dist = Distributors(name=name, deliver_service=deliver_service)
            sess.add(dist)
            sess.commit()
            sess.close()
            return True

    @staticmethod
    def delete(name: str) -> object:
        sess = Session()
        dist = sess.query(Distributors).where(Distributors.name == name).first()
        if dist is not None:
            sess.delete(dist)
            sess.commit()
            sess.close()
            return "Deleted"
        else:
            sess.close()
            return "None"

    @staticmethod
    def get(name: str) -> object:
        sess = Session()
        dist = sess.query(Distributors).where(Distributors.name == name).first()
        if dist is not None:
            distributor = {"id": dist.id, "name": dist.name, "deliver_service": dist.deliver_service}
            return distributor
        else:
            return False

    @staticmethod
    def update_service(name: str, deliver_service: str) -> object:
        sess = Session()
        dist = sess.query(Distributors).where(Distributors.name == name).first()
        if dist is not None:
            dist.deliver_service = deliver_service
            sess.commit()
            distributor = {"name": dist.name, "deliver_service": deliver_service}
            sess.close()
            return distributor
        else:
            sess.close()
            return False


class Supplies(Base):
    __tablename__ = 'supplies'
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey('components.id'))
    count = Column(Float)
    distributor = Column(Integer, ForeignKey('distributors.id'))


# noinspection PyTypeChecker
class SuppliesCrud:
    @staticmethod
    def add(component_id: int, count: float, distributor: int):
        sess = Session()
        supply = Supplies(component_id=component_id, count=count, distributor=distributor)
        sess.add(supply)
        sess.commit()
        sess.close()

    @staticmethod
    def get_count(component_id: int) -> object:
        sess = Session()
        try:
            count = sess.query(func.sum(Supplies.count)).filter(Supplies.component_id == component_id).all()
            return count[0][0]
        except Exception as e:
            print(e)
            return None
        finally:
            sess.close()


class Banks(Base):
    __tablename__ = 'banks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    usage = relationship('Transactions')


# noinspection PyTypeChecker
class BanksCrud:
    @staticmethod
    def add(name: str):
        sess = Session()
        bank = sess.query(Banks).where(Banks.name == name).first()
        if bank is None:
            bank = Banks(name=name)
            sess.add(bank)
            sess.commit()
            sess.close()
        else:
            sess.close()

    @staticmethod
    def get_bank(name: str) -> object:
        sess = Session()
        bank = sess.query(Banks).where(Banks.name == name).first()
        if bank is not None:
            answer = {"id": bank.id, "name": bank.name}
            sess.close()
            return answer
        else:
            BanksCrud.add(name)
            return BanksCrud.get_bank(name)

    @staticmethod
    def delete_bank(name: str) -> object:
        sess = Session()
        bank = sess.query(Banks).where(Banks.name == name).first()
        if bank is not None:
            sess.delete(bank)
            sess.commit()
            sess.close()
            return True
        else:
            return False


Base.metadata.create_all(engine)
