from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from dantic import ComponentsDantic, EmloyeeDantic, ProductDantic, BankDantic, DistributorDantic, ServiceDantic
from functions import ComponentCrud, EmployeesCrud, ProductsCrud, BanksCrud, DistributorsCrud, ServicesCrud

app = FastAPI()
SUCCESSFUL_ADD = "Successful addition"


@app.post('/components/add')
def component_add(component: ComponentsDantic):
    comp = ComponentCrud.add_component(component.name, component.type)
    if comp is not False:
        return SUCCESSFUL_ADD
    else:
        return False


@app.get("/components/get/{name}")
def component_get(name: str):
    comp = ComponentCrud.get_component(name)
    if comp is False:
        raise HTTPException(status_code=404)
    else:
        return comp


@app.delete("/components/{name}")
def component_delete(name: str):
    comp = ComponentCrud.get_component(name)
    if comp is False:
        raise HTTPException(status_code=404)
    else:
        cmp = ComponentCrud.delete_component(comp['id'])
        if cmp is not False:
            return "Successful deletion"
        else:
            raise HTTPException(status_code=500, detail="Server error")


@app.post("/employee/add")
def employee_add(employee: EmloyeeDantic):
    emp = EmployeesCrud.add_emp(group=employee.group, first_name=employee.name, second_name=employee.surname,
                                salary=employee.salary, contract_end=employee.contract_end)
    if emp is True:
        return SUCCESSFUL_ADD
    else:
        return False


@app.get("/employee/get/{name}-{surname}")
def employee_get(name: str, surname: str):
    emp = EmployeesCrud.get_emp(first_name=name, second_name=surname)
    if emp is not False:
        return emp
    else:
        raise HTTPException(status_code=404)


@app.put("/employee/update/")
def employee_update(employee: EmloyeeDantic):
    emp = EmployeesCrud.update_emp(first_name=employee.name, second_name=employee.surname, group=employee.group,
                                   salary=employee.salary,
                                   contract_end=employee.contract_end)
    if emp is False:
        return False
    elif emp is None:
        return HTTPException(status_code=404)
    else:
        return emp


@app.delete("/employee/delete/{name}-{surname}")
def employee_delete(name: str, surname: str):
    emp = EmployeesCrud.get_emp(first_name=name, second_name=surname)
    if emp is False:
        raise HTTPException(status_code=404)
    else:
        EmployeesCrud.delete_emp(emp['id'])
        return True


@app.post("/products/add")
def product_add(product: ProductDantic):
    prod = ProductsCrud.add(product.name, product.category, product.price)
    if prod is not False:
        return SUCCESSFUL_ADD
    else:
        return False


@app.get("/products/get/{name}")
def product_get(name: str):
    prod = ProductsCrud.get_product(name)
    if prod is not False:
        return prod
    else:
        raise HTTPException(status_code=404)


@app.put("/products/update")
def product_update(product: ProductDantic):
    prod = ProductsCrud.update_product_price(product.name, product.price)
    if prod is not False:
        return prod
    else:
        return HTTPException(status_code=404)


@app.delete("/products/delete/{name}")
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


@app.post("/distributor/add")
def distributor_add(distributor: DistributorDantic):
    distributor = DistributorsCrud.add(distributor.name, distributor.deliver_service)
    if distributor is not False:
        return SUCCESSFUL_ADD
    else:
        raise HTTPException(status_code=404)


@app.get("/distributor/get/{name}")
def distributor_get(name: str):
    distributor = DistributorsCrud.get(name)
    if distributor is not False:
        return distributor
    else:
        raise HTTPException(status_code=404)


@app.put("/distributor/update")
def distributor_update(distributor: DistributorDantic):
    distributor = DistributorsCrud.update_service(distributor.name, distributor.deliver_service)
    if distributor is not False:
        return distributor
    else:
        raise HTTPException(status_code=404)


@app.delete("/distributor/delete/{name}")
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


