from flask import Flask
from models import CustomerCrud, EmployeesCrud, ProductsCrud

app = Flask(__name__)


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
