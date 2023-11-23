from flask import Flask
from flask import request
from flask import jsonify
from database.functions import EmployeesCrud, ProductsCrud, ComponentCrud, BanksCrud, DistributorsCrud, \
    ComponentUsageCrud, OrdersCrud, TasksCrud, TransactionsCrud, ServicesCrud, SuppliesCrud, ServiceOrdersCrud

app = Flask(__name__)

SUCCESSFUL_ADD = {"status": "200", "answer": "Successful addition"}
SUCCESSFUL_DELETE = {"status": "200", "answer": "Successful deletion"}

@app.route("/comp/add", methods=['POST'])
def comp_add():
    data = request.get_json()
    component = ComponentCrud.add_component(data["name"], data["type"])
    if component is not False:
        return jsonify(SUCCESSFUL_ADD)
    else:
        answer = {"status": "400, ", "answer": "Component is already in database"}
        return jsonify(answer)


@app.route("/comp/get", methods={'GET'})
def get_comp():
    data = request.get_json()
    component = ComponentCrud.get_component(data["name"], data["type"])
    if component is not False:
        return jsonify(component)
    else:
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route("/comp/delete", methods={'DELETE'})
def delete_comp():
    data = request.get_json()
    try:
        comp = ComponentCrud.get_component(data["name"], data["type"])
        comp_id = comp["id"]
        component = ComponentCrud.delete_component(comp_id)
        if component is not False:
            return jsonify(SUCCESSFUL_DELETE)
        else:
            answer = {"status": "400", "answer": "User Data exception"}
            return jsonify(answer)
    except Exception as e:
        print(e)
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route('/supply/add', methods=["POST"])
def add_supply():
    data = request.get_json()
    comp = ComponentCrud.get_component(data["name"], data["type"])
    if comp is not False:
        comp_id = comp["id"]
        distributor = DistributorsCrud.get(data["dist"])
        if distributor is not False:
            dist_id = distributor['id']
            SuppliesCrud.add(comp_id, data["count"], dist_id)
            return jsonify(SUCCESSFUL_ADD)
        else:
            DistributorsCrud.add(data["dist"], "DHL")
            distributor = DistributorsCrud.get(data["dist"])
            dist_id = distributor['id']
            supply = SuppliesCrud.add(comp_id, data["count"], dist_id)
            return jsonify(SUCCESSFUL_ADD)
    else:
        comp = ComponentCrud.add_component(data["name"], data["type"])
        component = ComponentCrud.get_component(data["name"], data["type"])
        comp_id = component['id']
        distributor = DistributorsCrud.get(data["dist"])
        if distributor is not False:
            dist_id = distributor['id']
            supply = SuppliesCrud.add(comp_id, data["count"], dist_id)
            return jsonify(SUCCESSFUL_ADD)
        else:
            x = DistributorsCrud.add(data["dist"], "DHL")
            distributor = DistributorsCrud.get(data["dist"])
            dist_id = distributor['id']
            supply = SuppliesCrud.add(comp_id, data["count"], dist_id)
            return jsonify(SUCCESSFUL_ADD)


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
    data = request.get_json()
    try:
        emp = EmployeesCrud.add_emp(data["group"], data["name"], data["surname"], data["salary"])
        if emp is True:
            return jsonify(SUCCESSFUL_ADD)
        else:
            answer = {"status": "200", "answer": "Employee is already in database"}
            return jsonify(answer)
    except Exception as e:
        print(e)
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route("/emp/delete", methods=["GET", "DELETE"])
def delete_emp():
    data = request.get_json()
    emp = EmployeesCrud.get_emp(data["name"], data["surname"])
    if emp is not False:
        id = emp["id"]
        EmployeesCrud.delete_emp(id)
        return jsonify(SUCCESSFUL_DELETE)
    else:
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route('/prod/add', methods=["POST"])
def add_prod():
    data = request.get_json()
    try:
        ProductsCrud.add(data["name"], data["category"], data["price"])
        return jsonify(SUCCESSFUL_ADD)
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
        return jsonify(SUCCESSFUL_DELETE)
    else:
        answer = {"status": "400", "answer": "User Data exception"}
        return jsonify(answer)


@app.route('/prod/update', methods=["PUT"])
def update_price():
    data = request.get_json()
    prod = ProductsCrud.update_product_price(data["name"], data["price"])
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
    data = request.get_json()
    dist = DistributorsCrud.add(data['name'], data['deliver_service'])
    if dist is True:
        return jsonify(SUCCESSFUL_ADD)
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
        print(e)
        answer = {"status": "400", "answer": "Bad Request"}
        return jsonify(answer)
    except ValueError as e:
        print(e)
        answer = {"status": "400", "answer": "Bad Request"}
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
        task = TasksCrud.add_task(int(order), int(worker_id))
        if task is not False:
            answer = {"status": "200", "answer": "Successful add"}
            return jsonify(answer)
        else:
            answer = {"status": "400", "answer": "Bad Request"}
            return jsonify(answer)
    except ValueError:
        answer = {"status": "400", "answer": "Error"}
        return jsonify(answer)


@app.route("/services/tasks/add", methods=["POST"])
def add_ser_task():
    order = request.args.get("order")
    worker = request.args.get("worker")
    try:
        task = TasksCrud.add_ser_task(int(order), int(worker))
        if task is not False:
            answer = {"status": "200", "answer": "Successful add"}
            return jsonify(answer)
        else:
            answer = {"status": "400", "answer": "123"}
            return jsonify(answer)
    except ValueError:
        answer = {"status": "400", "answer": "Error"}
        return jsonify(answer)


@app.route("/component/usage/add", methods=["POST"])
def add_comp_usage():
    comp = request.args.get("comp")
    name = request.args.get("name")
    count = request.args.get("count")
    task = request.args.get("task")
    try:
        ComponentUsageCrud.add(int(comp), name, int(count), int(task))
        answer = {"status": "200", "answer": "Successful add"}
        return jsonify(answer)
    except ValueError:
        answer = {"status": "400", "answer": "Error"}
        return jsonify(answer)


@app.route("/prod/test", methods=["POST"])
def bank_test():
    data = request.get_json()
    try:
        ProductsCrud.add(data["name"], data["category"], data["product_price"])
        answer = {"status": "200", "answer": "Successful add"}
        return jsonify(answer)
    except Exception as e:
        print(e)
        answer = {"status": "400", "answer": "Error"}
        return jsonify(answer)


app.run(debug=True)
