from flask import Flask
from models import CustomerCrud, EmployeesCrud, ProductsCrud, ComponentCrud, BanksCrud, DistributorsCrud, \
    ComponentUsageCrud, OrdersCrud, LogsCrud, TasksCrud, TransactionsCrud, ServicesCrud, SuppliesCrud, ServiceOrdersCrud

app = Flask(__name__)

@app.route("/comp_add", methods=['GET'])
def comp_add():
    component = ComponentCrud.add_component("Varmilo Sakura", "KeyCups")
    if component is not False:
        return component
    else:
        return "Bad data"



@app.route('/test')
def main():
    CustomerCrud.add_customer(123, 1, "zhu", "zhu", "zhuzhu")
    return "q"


@app.route('/emp')
def emp_add():
    EmployeesCrud.add_emp("Owner", "Zhuchka", "TripleSix", 1500)
    return "ok"


@app.route('/add_product')
def add_prod():
    prod = ProductsCrud.add("kb", 250)
    return "ok"


@app.route('/delete_product')
def delete_product():
    prod = ProductsCrud.delete_product("kb")
    if prod is True:
        return 'Deleted'
    else:
        return 'None'


app.run(debug=True)
