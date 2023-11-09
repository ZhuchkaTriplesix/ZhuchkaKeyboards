from flask import Flask
from flask import request
from flask import jsonify
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
        return jsonify(component)
    else:
        answer = {"Status": "400, ", "Error": "Component is already in database"}
        return jsonify(answer)


@app.route("/comp/get", methods={'GET'})
def get_comp():
    name = request.args.get('name')
    type = request.args.get('type')
    component = ComponentCrud.get_component(name, type)
    if component is not False:
        return jsonify(component)
    else:
        answer = {"Status": "400", "Error": "User Data exception"}
        return jsonify(answer)


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
            return jsonify(answer)
        else:
            answer = {"status": "200", "answer": "Employee is already in database"}
            return jsonify(answer)
    except Exception as e:
        print(e)
        answer = {"Status": "400", "Error": "User Data exception"}
        return jsonify(answer)


@app.route("/emp/delete", methods=["GET", "DELETE"])
def delete_emp():
    name = request.args.get("name")
    surname = request.args.get("surname")
    emp = EmployeesCrud.get_emp(name, surname)
    if emp is not False:
        id = emp["id"]
        EmployeesCrud.delete_emp(id)
        answer = {"status": "200", "answer": "OK"}
        return jsonify(answer)
    else:
        answer = {"Status": "400", "Error": "User Data exception"}
        return jsonify(answer)


@app.route('/prod/add', methods=["POST"])
def add_prod():
    name = request.args.get("name")
    price = request.args.get("price")
    try:
        ProductsCrud.add(name, price)
        answer = {"status": "200", "answer": "OK"}
        return jsonify(answer)
    except Exception as e:
        print(e)
        answer = {"Status": "400", "Error": "User Data exception"}
        return jsonify(answer)


@app.route("/prod/get", methods=['GET', 'POST'])
def get_prod():
    product_name = request.args.get('name')
    prod = ProductsCrud.get_product(product_name)
    if prod is not False:
        return jsonify(prod)
    else:
        answer = {"Status": "400", "Error": "User Data exception"}
        return jsonify(answer)


@app.route('/prod/delete', methods=['DELETE'])
def delete_product():
    name = request.args.get("name")
    prod = ProductsCrud.delete_product(name)
    if prod is True:
        answer = {"answer": "ok", "status": 200}
        return jsonify(answer)
    else:
        answer = {"Status": "400", "Error": "User Data exception"}
        return jsonify(answer)


@app.route("/bank/add", methods=["POST"])
def add_bank():
    name = request.args.get("name")
    bank = BanksCrud.add(name)
    answer = {"answer": "ok", "status": 200}
    return jsonify(answer)


@app.route("/bank/get", methods=["GET"])
def get_bank():
    name = request.args.get("name")
    bank = BanksCrud.get_bank(name)
    return jsonify(bank)


@app.route("/dist/add", methods=["POST"])
def add_dist():
    name = request.args.get("name")
    deliver_service = request.args.get("service")
    dist = DistributorsCrud.add(name, deliver_service)
    if dist is True:
        answer = {"answer": "Added", "status": 200}
        return jsonify(answer)
    else:
        answer = {"answer": "Already in database", "status": 200}
        return jsonify(answer)


@app.route("/dist/get", methods=["GET"])
def get_dist():
    name = request.args.get("name")
    dist = DistributorsCrud.get(name)
    if dist is not False:
        return jsonify(dist)
    else:
        answer = {"Status": "400", "Error": "User Data exception"}
        return jsonify(answer)


app.run(debug=True)
