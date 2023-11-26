import datetime
from sqlalchemy import create_engine, and_, func
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import scoped_session, sessionmaker
from config import database
from dantic import ComponentsDantic, EmloyeeDantic, ProductDantic, BankDantic, DistributorDantic, ServiceDantic, \
    CustomerDantic
from models import Banks, ComponentUsage, Components, Customers, Distributors, Employees, TelegramUsers, Logs, Orders, \
    Products, Services, ServiceOrders, Supplies, Tasks, Transactions

engine = create_engine(database, echo=False)

Session = sessionmaker(bind=engine)
session = scoped_session(Session)
conn = engine.connect()


# noinspection PyTypeChecker
class TelegramUsersCrud:
    @staticmethod
    def add_user(telegram_id: int, username: str) -> object:
        sess = Session()
        user = sess.query(TelegramUsers).where(TelegramUsers.id == telegram_id).first()
        if user is not None:
            sess.close()
            return False
        else:
            user = TelegramUsers(id=telegram_id, username=username)
            sess.add(user)
            sess.commit()
            sess.close()
            return True

    @staticmethod
    def get_user(telegram_id: int) -> object:
        sess = Session()
        user = sess.query(TelegramUsers).where(TelegramUsers.id == telegram_id).first()
        if user is not None:
            answer = {"id": user.id, "username": user.username, "group": user.group}
            return answer
        else:
            return False

    @staticmethod
    def update_group(telegram_id: int, group: int) -> object:
        sess = Session()
        user = sess.query(TelegramUsers).where(TelegramUsers.id == telegram_id).first()
        if user is not None:
            user.group = group
            sess.commit()
            answer = {"id": user.id, "username": user.username, "group": user.group}
            sess.close()
            return answer
        else:
            sess.close()
            return False

    @staticmethod
    def delete_user(telegram_id: int) -> object:
        sess = Session()
        user = sess.query(TelegramUsers).where(TelegramUsers.id == telegram_id).first()
        if user is not None:
            sess.delete(user)
            sess.commit()
            sess.close()
            return True
        else:
            sess.close()
            return False


# noinspection PyTypeChecker
class CustomerCrud:
    @staticmethod
    def get_customer(vendor_id: int) -> object:
        sess = Session()
        customer = sess.query(Customers).where(Customers.vendor_id == vendor_id).first()
        if customer is not None:
            cust = CustomerDantic(id=customer.id, vendor_id=customer.vendor_id, vendor_type=customer.vendor_id,
                                  first_name=customer.first_name, second_name=customer.second_name,
                                  username=customer.username, email=customer.email, created_date=customer.created_date,
                                  updated_date=customer.updated_date)
            sess.close()
            return customer
        else:
            sess.close()
            return None

    @staticmethod
    def add_customer(vendor_id: int, vendor_type: int, first_name: str, second_name: str, username: str,
                     email: str) -> object:
        sess = Session()
        customer = sess.query(Customers).where(Customers.vendor_id == vendor_id).first()
        if customer is None:
            customer = Customers(vendor_id=vendor_id, vendor_type=vendor_type, first_name=first_name,
                                 second_name=second_name, username=username, email=email)
            sess.add(customer)
            sess.commit()
            sess.close()
            return True
        else:
            return False

    @staticmethod
    def update_customer_email(id: int, vendor_id: int, vendor_type: int, first_name: str, second_name: str,
                              username: str, email: str) -> CustomerDantic:
        sess = Session()
        try:
            customer = sess.query(Customers).where(Customers.id == id).first()
            if vendor_id is not None:
                customer.vendor_id = vendor_id
            if vendor_type is not None:
                customer.vendor_type = vendor_type
            if first_name is not None:
                customer.first_name = first_name
            if second_name is not None:
                customer.second_name = second_name
            if username is not None:
                customer.username = username
            if email is not None:
                customer.email = email
            customer.updated_date = datetime.datetime.utcnow()
            sess.commit()
            cust = CustomerDantic(id=customer.id, vendor_id=customer.vendor_id, vendor_type=customer.vendor_id,
                                  first_name=customer.first_name, second_name=customer.second_name,
                                  username=customer.username, email=customer.email, created_date=customer.created_date,
                                  updated_date=customer.updated_date)
            sess.close()
            return cust
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


# noinspection PyTypeChecker
class EmployeesCrud:
    @staticmethod
    def add_emp(first_name: str, second_name: str, group: str, salary: float,
                contract_end: datetime.datetime) -> EmloyeeDantic:
        sess = Session()
        try:
            emp = Employees(first_name=first_name, second_name=second_name, group=group,
                            salary=salary, contract_end=contract_end)
            sess.add(emp)
            sess.commit()
            employee = Employees(id=emp.id, first_name=emp.first_name, second_name=emp.second_name, group=emp.group,
                                 salary=emp.salary, contract_end=emp.contract_end)
            return employee
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()

    @staticmethod
    def update_emp(id: int, first_name: str, second_name: str, group: str, salary: float,
                   contract_end) -> EmloyeeDantic:
        sess = Session()
        try:
            emp = sess.query(Employees).where(Employees.id == id).first()
            if first_name is not None:
                emp.first_name = first_name
            if second_name is not None:
                emp.second_name = second_name
            if group is not None:
                emp.group = group
            if salary is not None:
                emp.salary = salary
            if contract_end is not None:
                emp.contract_end = contract_end
            sess.commit()
            employee = Employees(id=emp.id, first_name=emp.first_name, second_name=emp.second_name, group=emp.group,
                                 salary=emp.salary, contract_end=emp.contract_end)
            return employee
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()

    @staticmethod
    def get_emp(id: int) -> EmloyeeDantic:
        sess = Session()
        try:
            emp = sess.query(Employees).where(Employees.id == id).first()
            employee = {"id": id, "first_name": emp.first_name, "second_name": emp.second_name, "group": emp.group,
                        "salary": emp.salary,
                        "contract_end": emp.contract_end}
            return employee
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()

    @staticmethod
    def delete_emp(id: int) -> object:
        sess = Session()
        try:
            emp = sess.query(Employees).where(Employees.id == id).first()
            sess.delete(emp)
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()


class LogsCrud:
    @staticmethod
    def add_log(employee_id: int, operation: str):
        sess = Session()
        log = Logs(employee_id=employee_id, operation=operation)
        sess.add(log)
        sess.commit()
        sess.close()


# noinspection PyTypeChecker
class ComponentCrud:
    @staticmethod
    def add_component(component_name: str, component_type: str) -> ComponentsDantic:
        sess = Session()
        comp = sess.query(Components).where(Components.component_name == component_name).first()
        if comp is not None:
            return False
        else:
            component = Components(component_name=component_name, component_type=component_type)
            sess.add(component)
            sess.commit()
            component = ComponentsDantic(id=component.id, name=component.component_name, type=component.component_type)

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
    def get_component(id: int) -> ComponentsDantic:
        sess = Session()
        try:
            comp = sess.query(Components).where(Components.id == id).first()
            component = ComponentsDantic(id=comp.id, name=comp.component_name, type=comp.component_type)
            return component
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()

    @staticmethod
    def update_component(id: int, component_name: str, component_type: str) -> ComponentsDantic:
        sess = Session()
        comp = sess.query(Components).where(Components.id == id).first()
        if comp is not None:
            if component_name is not None:
                comp.component_name = component_name
            if component_type is not None:
                comp.component_type = component_type
            sess.commit()
            component = ComponentsDantic(id=comp.id, name=comp.component_name, type=comp.component_type)
            sess.close()
            return component
        else:
            return False


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


# noinspection PyTypeChecker
class OrdersCrud:
    @staticmethod
    def add(customer_id: int, transaction_id: int, product_id: int) -> object:
        sess = Session()
        try:
            order = Orders(customer_id=customer_id, transaction_id=transaction_id, product_id=product_id)
            sess.add(order)
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            sess.close()

    @staticmethod
    def add_manager(id: int, manager_id: int):
        sess = Session()
        order = sess.query(Orders).where(Orders.id == id).first()
        order.manager_id = manager_id
        sess.commit()
        product = ProductsCrud.get_product(order.id)
        answer = {"id": order.id, "customer_id": order.customer_id, "manager_id": order.manager_id,
                  "transaction_id": order.transaction_id, "product": product}
        sess.close()
        return answer

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


# noinspection PyTypeChecker
class ProductsCrud:
    @staticmethod
    def add(name: str, category: str, product_price: float) -> ProductDantic:
        sess = Session()
        prod = sess.query(Products).where(Products.name == name).first()
        if prod is not None:
            return False
        else:
            prod = Products(name=name, category=category, product_price=product_price)
            sess.add(prod)
            sess.commit()
            product = ProductDantic(id=prod.id, name=prod.name, category=prod.category, price=prod.product_price)
            sess.close()
            return product

    @staticmethod
    def get_product(id: int) -> ProductDantic:
        sess = Session()
        prod = sess.query(Products).where(Products.id == id).first()
        if prod is not None:
            product = ProductDantic(id=prod.id, name=prod.name, category=prod.category, price=prod.product_price)
            sess.close()
            return product
        else:
            sess.close()
            return False

    @staticmethod
    def delete_product(id: int) -> object:
        sess = Session()
        prod = sess.query(Products).where(Products.id == id).first()
        if prod is not None:
            sess.delete(prod)
            sess.commit()
            sess.close()
            return True
        else:
            sess.close()
            return False

    @staticmethod
    def update_product(id: int, product_name: str, category: str, product_price: float) -> ProductDantic:
        sess = Session()
        prod = sess.query(Products).where(Products.id == id).first()
        if prod is not None:
            if product_price is not None:
                prod.product_price = product_price
            if product_name is not None:
                prod.name = product_name
            if category is not None:
                prod.category = category
            sess.commit()
            product = ProductDantic(id=prod.id, name=prod.name, category=prod.category, price=prod.product_price)
            sess.close()
            return product
        else:
            return False


# noinspection PyTypeChecker
class ServicesCrud:
    @staticmethod
    def add(name: str, service_price: float) -> ServiceDantic:
        sess = Session()
        ser = sess.query(Services).where(Services.name == name).first()
        if ser is not None:
            sess.close()
            return False
        else:
            ser = Services(name=name, service_price=service_price)
            sess.add(ser)
            sess.commit()
            answer = ServiceDantic(id=ser.id, name=ser.name, price=ser.service_price)
            sess.close()
            return answer

    @staticmethod
    def get_service(id: int) -> object:
        sess = Session()
        ser = sess.query(Services).where(Services.id == id).first()
        if ser is not None:
            answer = {"id": ser.id, "name": ser.name, "price": ser.service_price}
            sess.close()
            return answer
        else:
            sess.close()
            return False

    @staticmethod
    def delete_service(id: int) -> object:
        sess = Session()
        ser = sess.query(Services).where(Services.id == id).first()
        if ser is None:
            sess.close()
            return False
        else:
            sess.delete(ser)
            sess.commit()
            sess.close()
            return True

    @staticmethod
    def update_service_price(id: int, name: str, service_price: float) -> object:
        sess = Session()
        ser = sess.query(Services).where(Services.id == id).first()
        if ser is not None:
            if name is not None:
                ser.name = name
            if service_price is not None:
                ser.service_price = service_price
            sess.commit()
            answer = {"id": ser.id, "name": ser.name, "price": ser.service_price}
            sess.close()
            return answer
        else:
            sess.close()
            return False


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


# noinspection PyTypeChecker
class DistributorsCrud:
    @staticmethod
    def add(name: str, deliver_service: str) -> DistributorDantic:
        sess = Session()
        dist = sess.query(Distributors).where(Distributors.name == name).first()
        if dist is not None:
            sess.close()
            return False
        else:
            dist = Distributors(name=name, deliver_service=deliver_service)
            sess.add(dist)
            sess.commit()
            distributor = DistributorDantic(id=dist.id, name=dist.name, deliver_service=dist.deliver_service)
            sess.close()
            return distributor

    @staticmethod
    def delete(id: int) -> object:
        sess = Session()
        dist = sess.query(Distributors).where(Distributors.id == id).first()
        if dist is not None:
            sess.delete(dist)
            sess.commit()
            sess.close()
            return True
        else:
            sess.close()
            return False

    @staticmethod
    def get(id: int) -> DistributorDantic:
        sess = Session()
        dist = sess.query(Distributors).where(Distributors.id == id).first()
        if dist is not None:
            distributor = DistributorDantic(id=dist.id, name=dist.name, deliver_service=dist.deliver_service)
            return distributor
        else:
            return False

    @staticmethod
    def update(id: int, name: str, deliver_service: str) -> DistributorDantic:
        sess = Session()
        dist = sess.query(Distributors).where(Distributors.id == id).first()
        if dist is not None:
            if name is not None:
                dist.name = name
            if deliver_service is not None:
                dist.deliver_service = deliver_service
            sess.commit()
            distributor = DistributorDantic(id=dist.id, name=dist.name, deliver_service=dist.deliver_service)
            sess.close()
            return distributor
        else:
            sess.close()
            return False


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


# noinspection PyTypeChecker
class BanksCrud:
    @staticmethod
    def add_bank(name: str) -> BankDantic:
        sess = Session()
        bank = sess.query(Banks).where(Banks.name == name).first()
        if bank is None:
            try:
                bank = Banks(name=name)
                sess.add(bank)
                sess.commit()
                answer = BankDantic(id=bank.id, name=bank.name)
                return answer
            except Exception as e:
                print(e)
                return False
            finally:
                sess.close()

    @staticmethod
    def get_bank(id: int) -> BankDantic:
        sess = Session()
        bank = sess.query(Banks).where(Banks.id == id).first()
        if bank is not None:
            answer = BankDantic(id=bank.id, name=bank.name)
            sess.close()
            return answer
        else:
            return False

    @staticmethod
    def delete_bank(id: int) -> object:
        sess = Session()
        bank = sess.query(Banks).where(Banks.id == id).first()
        if bank is not None:
            sess.delete(bank)
            sess.commit()
            sess.close()
            return True
        else:
            return False
