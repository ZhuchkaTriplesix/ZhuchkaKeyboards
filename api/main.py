from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from dantic import ComponentsDantic, EmloyeeDantic, ProductDantic
from functions import ComponentCrud, EmployeesCrud, ProductsCrud

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
                                salary=employee.salary)
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
