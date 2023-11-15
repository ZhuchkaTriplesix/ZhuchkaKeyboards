from flask import Flask
from flask import request
from flask import jsonify
from models import CustomerCrud, EmployeesCrud, ProductsCrud, ComponentCrud, BanksCrud, DistributorsCrud, \
    ComponentUsageCrud, OrdersCrud, LogsCrud, TasksCrud, TransactionsCrud, ServicesCrud, SuppliesCrud, ServiceOrdersCrud

app = Flask(__name__)


@app.route("/comp/add", methods=['POST'])
def comp_add():
    name = request.args.get('name')
    type = request.args.get('type')
    component = ComponentCrud.add_component(name, type)
    if component is not False:
        return jsonify(component)
    else:
        answer = {"status": "400, ", "answer": "Component is already in database"}
        return jsonify(answer)


@app.route("/comp/get", methods={'GET'})
def get_comp():
    name = request.args.get('name')
    type = request.args.get('type')
    component = ComponentCrud.get_component(name, type)
    if component is not False:
        return jsonify(component)
    else:
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route("/comp/delete", methods={'DELETE'})
def delete_comp():
    name = request.args.get("name")
    type = request.args.get("type")
    try:
        comp = ComponentCrud.get_component(name, type)
        comp_id = comp["id"]
        component = ComponentCrud.delete_component(comp_id)
        if component is not False:
            answer = {"status": "200", "answer": "Successful deletion"}
            return jsonify(answer)
        else:
            answer = {"status": "400", "answer": "User Data exception"}
            return jsonify(answer)
    except Exception as e:
        print(e)
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route('/supply/add', methods=["POST"])
def add_supply():
    name = request.args.get('name')
    type = request.args.get('type')
    dist = request.args.get('dist')
    count = request.args.get('count')
    comp = ComponentCrud.get_component(name, type)
    if comp is not False:
        comp_id = comp["id"]
        distributor = DistributorsCrud.get(dist)
        if distributor is not False:
            dist_id = distributor['id']
            SuppliesCrud.add(comp_id, float(count), dist_id)
            answer = {'status': '200', 'answer': 'Supply added'}
            return answer
        else:
            DistributorsCrud.add(dist, "DHL")
            distributor = DistributorsCrud.get(dist)
            dist_id = distributor['id']
            supply = SuppliesCrud.add(comp_id, float(count), dist_id)
            answer = {'status': '200', 'answer': 'Supply added'}
            return answer
    else:
        comp = ComponentCrud.add_component(name, type)
        component = ComponentCrud.get_component(name, type)
        comp_id = component['id']
        distributor = DistributorsCrud.get(dist)
        if distributor is not False:
            dist_id = distributor['id']
            supply = SuppliesCrud.add(comp_id, float(count), dist_id)
            answer = {'status': '200', 'answer': 'Supply added'}
            return answer
        else:
            x = DistributorsCrud.add(dist, "DHL")
            distributor = DistributorsCrud.get(dist)
            dist_id = distributor['id']
            supply = SuppliesCrud.add(comp_id, float(count), dist_id)
            answer = {'status': '200', 'answer': 'Supply added'}
            return answer


@app.route('/supply/count', methods=["GET"])
def get_count():
    name = request.args.get('name')
    type = request.args.get('type')
    try:
        comp = ComponentCrud.get_component(name, type)
        count = SuppliesCrud.get_count(comp['id'])
        answer = {"name": comp['name'], 'type': comp['type'], "count": count}
        return answer
    except Exception as e:
        print(e)
        answer = {'status': '400', 'answer': 'User Data exception'}
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
        answer = {"status": "400", "answer": "User Data exception"}
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
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route('/prod/add', methods=["POST"])
def add_prod():
    name = request.args.get("name")
    price = request.args.get("price")
    try:
        ProductsCrud.add(name, float(price))
        answer = {"status": "200", "answer": "OK"}
        return jsonify(answer)
    except Exception as e:
        print(e)
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route("/prod/get", methods=['GET', 'POST'])
def get_prod():
    product_name = request.args.get('name')
    prod = ProductsCrud.get_product(product_name)
    if prod is not False:
        return jsonify(prod)
    else:
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route('/prod/delete', methods=['DELETE'])
def delete_product():
    name = request.args.get("name")
    prod = ProductsCrud.delete_product(name)
    if prod is True:
        answer = {"status": "200", "answer": "Successful deletion"}
        return jsonify(answer)
    else:
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route('/prod/update', methods=["PUT"])
def update_price():
    name = request.args.get('name')
    price = request.args.get('price')
    prod = ProductsCrud.update_product_price(name, price)
    if prod is not False:
        return jsonify(prod)
    else:
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route("/bank/add", methods=["POST"])
def add_bank():
    name = request.args.get("name")
    bank = BanksCrud.add(name)
    answer = {"status": "200", "answer": "Successful bank add"}
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
        answer = {"status": "Added", "answer": "Added"}
        return jsonify(answer)
    else:
        answer = {"status": "200", "answer": "Already in database"}
        return jsonify(answer)


@app.route("/dist/get", methods=["GET"])
def get_dist():
    name = request.args.get("name")
    dist = DistributorsCrud.get(name)
    if dist is not False:
        return jsonify(dist)
    else:
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route("/dist/update", methods=["PUT"])
def update_dist():
    name = request.args.get("name")
    service = request.args.get("service")
    dist = DistributorsCrud.update_service(name, service)
    if dist is not False:
        return jsonify(dist)
    else:
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route("/transactions/add", methods=["POST"])
def add_transaction():
    payment = request.args.get('payment')
    status = request.args.get('status')
    bank_id = request.args.get('bank')
    type = request.args.get('type')
    try:
        TransactionsCrud.add(int(payment), bool(status), int(bank_id), int(type))
        answer = {"status": "200", "answer": "Successful addition"}
        return jsonify(answer)
    except TypeError as e:
        answer = {"status": "400", "answer": e}
        return jsonify(answer)
    except ValueError as e:
        answer = {"status": "400", "answer": e}
        return jsonify(answer)


@app.route("/services/add", methods=["POST"])
def add_service():
    name = request.args.get('name')
    price = request.args.get('price')
    service = ServicesCrud.add(name, price)
    if service is True:
        answer = {"status": "200", "answer": "Successful addition"}
        return jsonify(answer)
    else:
        answer = {"status": "200", "answer": "Already in database"}
        return jsonify(answer)


@app.route("/services/orders/add", methods=["POST"])
def add_service_order():
    service = request.args.get('service')
    trans = request.args.get('trans')
    customer = request.args.get('customer')
    ser = ServicesCrud.get_service(service)
    if ser is not False:
        try:
            ServiceOrdersCrud.add(ser["id"], int(trans), int(customer))
            answer = {"status": "200", "answer": "Successful add"}
            return jsonify(answer)
        except TypeError:
            answer = {"status": "400", "answer": "Error"}
            return jsonify(answer)
    else:
        answer = {"status": "400", "answer": "No service"}
        return jsonify(answer)


@app.route("/products/orders/add", methods=["POST"])
def add_order():
    customer = request.args.get('customer')
    transaction = request.args.get("trans")
    product = request.args.get("prod")
    prod = ProductsCrud.get_product(product)
    if prod is not False:
        try:
            OrdersCrud.add(int(customer), int(transaction), prod["id"])
            answer = {"status": "200", "answer": "Successful add"}
            return jsonify(answer)
        except TypeError:
            answer = {"status": "400", "answer": "Error"}
            return jsonify(answer)
    else:
        answer = {"status": "400", "answer": "No product"}
        return jsonify(answer)


@app.route("/products/tasks/add", methods=["POST"])
def add_task():
    order = request.args.get("order")
    worker_id = request.args.get("worker")
    try:
        task = TasksCrud.add_worker(int(order), None, int(worker_id))
        if task is True:
            answer = {"status": "200", "answer": "Successful add"}
            return jsonify(answer)
        else:
            answer = {"status": "400", "answer": "Error"}
            return jsonify(answer)
    except ValueError:
        answer = {"status": "400", "answer": "Error"}
        return jsonify(answer)


app.run(debug=True)
