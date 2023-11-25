from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from dantic import ComponentsDantic, EmloyeeDantic, ProductDantic, BankDantic, DistributorDantic, ServiceDantic, \
    CustomerDantic
from functions import ComponentCrud, EmployeesCrud, ProductsCrud, BanksCrud, DistributorsCrud, ServicesCrud, \
    CustomerCrud

app = FastAPI()
SUCCESSFUL_ADD = "Successful addition"


@app.post('/components', tags=["Components"])
def component_add(component: ComponentsDantic):
    comp = ComponentCrud.add_component(component.name, component.type)
    if comp is not False:
        return comp
    else:
        return False


@app.get("/components/{id}", tags=["Components"])
def component_get(id: int):
    comp = ComponentCrud.get_component(id)
    if comp is False:
        raise HTTPException(status_code=404)
    else:
        return comp


@app.put("/components/{id}", tags=["Components"])
def component_update(id: int, component: ComponentsDantic):
    comp = ComponentCrud.update_component(id, component.name, component.type)
    if comp is not False:
        return comp
    else:
        raise HTTPException(status_code=404)


@app.delete("/components/{id}", tags=["Components"])
def component_delete(id: int):
    comp = ComponentCrud.delete_component(id)
    if comp is False:
        raise HTTPException(status_code=404)
    else:
        return True


@app.post("/employees", tags=["Employee"])
def employee_add(employee: EmloyeeDantic):
    emp = EmployeesCrud.add_emp(group=employee.group, first_name=employee.first_name, second_name=employee.second_name,
                                salary=employee.salary, contract_end=employee.contract_end)
    if emp is True:
        return emp
    else:
        return False


@app.get("/employees/{id}", tags=["Employee"])
def employee_get(id: int):
    emp = EmployeesCrud.get_emp(id)
    if emp is not False:
        return emp
    else:
        raise HTTPException(status_code=404)


@app.put("/employees/{id}", tags=["Employee"])
def employee_update(id: int, employee: EmloyeeDantic):
    emp = EmployeesCrud.update_emp(first_name=employee.name, second_name=employee.surname, group=employee.group,
                                   salary=employee.salary,
                                   contract_end=employee.contract_end)
    if emp is False:
        return False
    elif emp is None:
        return HTTPException(status_code=404)
    else:
        return emp


@app.delete("/employees/{id}", tags=["Employee"])
def employee_delete(id: int):
    emp = EmployeesCrud.delete_emp(id)
    if emp is False:
        raise HTTPException(status_code=404)
    else:
        return True


@app.post("/products", tags=["Products"])
def product_add(product: ProductDantic):
    prod = ProductsCrud.add(product.name, product.category, product.price)
    if prod is not False:
        return SUCCESSFUL_ADD
    else:
        return False


@app.get("/products/{id}", tags=["Products"])
def product_get(id: int):
    prod = ProductsCrud.get_product(id)
    if prod is not False:
        return prod
    else:
        raise HTTPException(status_code=404)


@app.put("/products/{id}", tags=["Products"])
def product_update(id: int, product: ProductDantic):
    prod = ProductsCrud.update_product(id, product.name, product.category, product.price)
    if prod is not False:
        return prod
    else:
        return HTTPException(status_code=404)


@app.delete("/products/delete/{name}", tags=["Products"])
def product_delete(name: str):
    prod = ProductsCrud.delete_product(name)
    if prod is not False:
        return "Successful deletion"
    else:
        raise HTTPException(status_code=404)


@app.post("/banks/add")
def bank_add(bank: BankDantic):
    bank = BanksCrud.add(bank.name)
    if bank is not False:
        return "Successful add"
    else:
        raise HTTPException(status_code=404)


@app.get("/banks/get/{name}")
def bank_get(name: str):
    bank = BanksCrud.get_bank(name)
    if bank is not False:
        return bank
    else:
        raise HTTPException(status_code=404)


@app.delete("/banks/delete/{name}")
def bank_delete(name: str):
    bank = BanksCrud.delete_bank(name)
    if bank is not False:
        return "Successful delete"
    else:
        raise HTTPException(status_code=404)


@app.post("/distributors/add")
def distributor_add(distributor: DistributorDantic):
    distributor = DistributorsCrud.add(distributor.name, distributor.deliver_service)
    if distributor is not False:
        return SUCCESSFUL_ADD
    else:
        raise HTTPException(status_code=404)


@app.get("/distributors/get/{name}")
def distributor_get(name: str):
    distributor = DistributorsCrud.get(name)
    if distributor is not False:
        return distributor
    else:
        raise HTTPException(status_code=404)


@app.put("/distributors/update")
def distributor_update(distributor: DistributorDantic):
    distributor = DistributorsCrud.update_service(distributor.name, distributor.deliver_service)
    if distributor is not False:
        return distributor
    else:
        raise HTTPException(status_code=404)


@app.delete("/distributors/delete/{name}")
def distributor_delete(name: str):
    distributor = DistributorsCrud.delete(name)
    if distributor is not False:
        return True
    else:
        raise HTTPException(status_code=404)


@app.post("/services/add")
def service_add(service: ServiceDantic):
    service = ServicesCrud.add(service.name, service.price)
    if service is not False:
        return SUCCESSFUL_ADD
    else:
        return False


@app.get("/services/get/{name}")
def service_get(name):
    service = ServicesCrud.get_service(name)
    if service is not False:
        return service
    else:
        raise HTTPException(status_code=404)


@app.put("/services/update")
def service_update(service: ServiceDantic):
    service = ServicesCrud.update_service_price(service.name, service.price)
    if service is not False:
        return service
    else:
        raise HTTPException(status_code=404)


@app.delete("/services/delete/{name}")
def service_delete(name: str):
    service = ServicesCrud.delete_service(name)
    if service is not False:
        return True
    else:
        raise HTTPException(status_code=404)


@app.post("/customers/add")
def customer_add(customer: CustomerDantic):
    customer = CustomerCrud.add_customer(vendor_id=customer.vendor_id, vendor_type=customer.vendor_type,
                                         first_name=customer.name, second_name=customer.surname,
                                         username=customer.username, email=customer.email)
    if customer is not False:
        return SUCCESSFUL_ADD
    else:
        return False


@app.get("/customers/get/{id}")
def customer_get(id: int):
    customer = CustomerCrud.get_customer(id)
    if customer is not False:
        return customer
    else:
        raise HTTPException(status_code=404)
