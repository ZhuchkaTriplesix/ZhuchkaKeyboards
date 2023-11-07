from flask import Flask
from models import CustomerCrud, EmployeesCrud
app = Flask(__name__)


@app.route('/test')
def main():
    CustomerCrud.add_customer(123, 1, "zhu", "zhu", "zhuzhu")
    return "q"


@app.route('/emp')
def emp_add():
    EmployeesCrud.add_emp("Owner", "Zhuchka", "TripleSix", 1500)
    return "ok"

app.run(debug=True)
