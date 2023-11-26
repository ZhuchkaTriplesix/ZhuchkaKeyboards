from fastapi import FastAPI, HTTPException
from dantic import ComponentsDantic, EmloyeeDantic, ProductDantic, BankDantic, DistributorDantic, ServiceDantic, \
    CustomerDantic
from functions import ComponentCrud, EmployeesCrud, ProductsCrud, BanksCrud, DistributorsCrud, ServicesCrud, \
    CustomerCrud

app = FastAPI()
SUCCESSFUL_ADD = "Successful addition"


@app.post('/components', tags=["Components"])
def component_add(component: ComponentsDantic) -> ComponentsDantic:
    comp = ComponentCrud.add_component(component.name, component.type)
    if comp is not False:
        return comp
    else:
        raise HTTPException


@app.get("/components/{id}", tags=["Components"])
def component_get(id: int) -> ComponentsDantic:
    comp = ComponentCrud.get_component(id)
    if comp is False:
        raise HTTPException(status_code=404)
    else:
        return comp


@app.put("/components/{id}", tags=["Components"])
def component_update(id: int, component: ComponentsDantic) -> ComponentsDantic:
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
def employee_add(employee: EmloyeeDantic) -> EmloyeeDantic:
    emp = EmployeesCrud.add_emp(employee.first_name, employee.second_name, employee.group, employee.salary,
                                employee.contract_end)
    if emp is True:
        return emp
    else:
        raise HTTPException


@app.get("/employees/{id}", tags=["Employee"])
def employee_get(id: int) -> EmloyeeDantic:
    emp = EmployeesCrud.get_emp(id)
    if emp is not False:
        return emp
    else:
        raise HTTPException(status_code=404)


@app.put("/employees/{id}", tags=["Employee"])
def employee_update(id: int, employee: EmloyeeDantic):
    emp = EmployeesCrud.update_emp(id, employee.first_name, employee.second_name, employee.group, employee.salary,
                                   employee.contract_end)
    if emp is not False:
        return emp
    else:
        return HTTPException(status_code=404)


@app.delete("/employees/{id}", tags=["Employee"])
def employee_delete(id: int):
    emp = EmployeesCrud.delete_emp(id)
    if emp is False:
        raise HTTPException(status_code=404)
    else:
        return True


@app.post("/products", tags=["Products"])
def product_add(product: ProductDantic) -> ProductDantic:
    prod = ProductsCrud.add(product.name, product.category, product.price)
    if prod is not False:
        return prod
    else:
        raise HTTPException


@app.get("/products/{id}", tags=["Products"])
def product_get(id: int) -> ProductDantic:
    prod = ProductsCrud.get_product(id)
    if prod is not False:
        return prod
    else:
        raise HTTPException(status_code=404)


@app.put("/products/{id}", tags=["Products"])
def product_update(id: int, product: ProductDantic) -> ProductDantic:
    prod = ProductsCrud.update_product(id, product.name, product.category, product.price)
    if prod is not False:
        return prod
    else:
        raise HTTPException(status_code=404)


@app.delete("/products/{id}", tags=["Products"])
def product_delete(id: int):
    prod = ProductsCrud.delete_product(id)
    if prod is not False:
        return True
    else:
        raise HTTPException(status_code=404)


@app.post("/banks", tags=["Banks"])
def bank_add(bank: BankDantic) -> BankDantic:
    bank = BanksCrud.add_bank(bank.name)
    if bank is not False:
        return bank
    else:
        raise HTTPException(status_code=404)


@app.get("/banks/{id}", tags=["Banks"])
def bank_get(id: int) -> BankDantic:
    bank = BanksCrud.get_bank(id)
    if bank is not False:
        return bank
    else:
        raise HTTPException(status_code=404)


@app.delete("/banks/{id}", tags=["Banks"])
def bank_delete(id: int):
    bank = BanksCrud.delete_bank(id)
    if bank is not False:
        return "Successful delete"
    else:
        raise HTTPException(status_code=404)


@app.post("/distributors", tags=["Distributors"])
def distributor_add(distributor: DistributorDantic) -> DistributorDantic:
    distributor = DistributorsCrud.add(distributor.name, distributor.deliver_service)
    if distributor is not False:
        return distributor
    else:
        raise HTTPException


@app.get("/distributors/{id}", tags=["Distributors"])
def distributor_get(id: int) -> DistributorDantic:
    distributor = DistributorsCrud.get(id)
    if distributor is not False:
        return distributor
    else:
        raise HTTPException(status_code=404)


@app.put("/distributors/{id}", tags=["Distributors"])
def distributor_update(id: int, distributor: DistributorDantic) -> DistributorDantic:
    distributor = DistributorsCrud.update(id, distributor.name, distributor.deliver_service)
    if distributor is not False:
        return distributor
    else:
        raise HTTPException(status_code=404)


@app.delete("/distributors/{id}", tags=["Distributors"])
def distributor_delete(id: int):
    distributor = DistributorsCrud.delete(id)
    if distributor is not False:
        return True
    else:
        raise HTTPException(status_code=404)


@app.post("/services", tags=["Services"])
def service_add(service: ServiceDantic) -> ServiceDantic:
    ser = ServicesCrud.add(service.name, service.price)
    if ser is not False:
        return ser
    else:
        raise HTTPException


@app.get("/services/{id}", tags=["Services"])
def service_get(id: int):
    service = ServicesCrud.get_service(id)
    if service is not False:
        return service
    else:
        raise HTTPException(status_code=404)


@app.put("/services/{id}", tags=["Services"])
def service_update(id: int, service: ServiceDantic):
    service = ServicesCrud.update_service_price(id, service.name, service.price)
    if service is not False:
        return service
    else:
        raise HTTPException(status_code=404)


@app.delete("/services/{id}", tags=["Services"])
def service_delete(id: int):
    service = ServicesCrud.delete_service(id)
    if service is not False:
        return True
    else:
        raise HTTPException(status_code=404)


@app.post("/customers", tags=["Customers"])
def customer_add(customer: CustomerDantic):
    customer = CustomerCrud.add_customer(vendor_id=customer.vendor_id, vendor_type=customer.vendor_type,
                                         first_name=customer.name, second_name=customer.surname,
                                         username=customer.username, email=customer.email)
    if customer is not False:
        return SUCCESSFUL_ADD
    else:
        return False


@app.get("/customers/{id}", tags=["Customers"])
def customer_get(id: int) -> CustomerDantic:
    customer = CustomerCrud.get_customer(id)
    if customer is not False:
        return customer
    else:
        raise HTTPException(status_code=404)


@app.put("/customers/{id}", tags=["Customers"])
def customer_update(id: int, customer: CustomerDantic) -> CustomerDantic:
    cust = CustomerCrud.update_customer_email()