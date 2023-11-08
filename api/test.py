from flask import Flask
from flask import request
from models import CustomerCrud, EmployeesCrud, ProductsCrud, ComponentCrud, BanksCrud, DistributorsCrud, \
    ComponentUsageCrud, OrdersCrud, LogsCrud, TasksCrud, TransactionsCrud, ServicesCrud, SuppliesCrud, ServiceOrdersCrud
import json

app = Flask(__name__)


@app.route("/comp/add", methods=['POST'])
def comp_add():
    name = request.args.get('name')
    type = request.args.get('type')
    component = ComponentCrud.add_component(name, type)
    if component is not False:
        return component
    else:
        answer = {"Status": "400, ", "Error": "Component is already in database"}
        return answer["Status"] + answer['Error']


@app.route("/comp/get", methods={'GET'})
def get_comp():
    name = request.args.get('name')
    type = request.args.get('type')
    component = ComponentCrud.get_component(name, type)
    if component is not False:
        return component
    else:
        answer = {"Status": "400", "Error": "User Data exception"}
        return answer


@app.route("/comp/delete", methods={'DELETE'})
def delete_comp():
    name = request.args.get("name")
    type = request.args.get("type")
    comp = ComponentCrud.get_component(name, type)
    comp_id = comp["Id"]
    component = ComponentCrud.delete_component(comp_id)
    if component is not False:
        return "Successful deletion"
    else:
        answer = {"Status": "400", "Error": "User Data exception"}
        return answer


@app.route('/emp/add', methods=["POST"])
def emp_add():
    group = request.args.get("group")
    name = request.args.get("name")
    surname = request.args.get("surname")
    salary = request.args.get("salary")
    try:
        emp = EmployeesCrud.add_emp(group, name, surname, salary)
        if emp is True:
            answer = {"status": "200", "answer": "OK"}
            return answer
        else:
            answer = {"status": "200", "answer": "Employee is already in database"}
            return answer
    except Exception as e:
        print(e)
        answer = {"Status": "400", "Error": "User Data exception"}
        return answer


@app.route("/emp/delete", methods=["GET", "DELETE"])
def delete_emp():
    name = request.args.get("name")
    surname = request.args.get("surname")
    emp = EmployeesCrud.get_emp(name, surname)
    if emp is not False:
        id = emp["id"]
        EmployeesCrud.delete_emp(id)
        answer = {"status": "200", "answer": "OK"}
        return answer
    else:
        answer = {"Status": "400", "Error": "User Data exception"}
        return answer


@app.route('/add_product')
def add_prod():
    prod = ProductsCrud.add("privet", 200)
    return "ok"


@app.route("/prod/get/<product_name>", methods=['GET', 'POST'])
def get_prod(product_name):
    product_name = request.args.get('product_name')
    prod = ProductsCrud.get_product(product_name)
    if prod is not False:
        return prod
    else:
        answer = {"Status": "400", "Error": "User Data exception"}
        return answer


@app.route('/delete_product')
def delete_product():
    prod = ProductsCrud.delete_product("kb")
    if prod is True:
        return 'Deleted'
    else:
        return 'None'


app.run(debug=True)
