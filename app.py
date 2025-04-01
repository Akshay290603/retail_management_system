import pyodbc
from flask import Flask, render_template
from flask_login import LoginManager, UserMixin, current_user, login_required

app = Flask(__name__)
app.secret_key = "1234"


# SQL Server connection
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=MARCO\MSSQSERVER;'
        'DATABASE=retail_management_system;'   
        'Trusted_Connection=yes'  
    )
    return conn



# # Initialize Flask-Login
# login_manager = LoginManager()
# login_manager.init_app(app)

# # Dummy user class for demonstration
# class User(UserMixin):
#     def __init__(self, id):
#         self.id = id

# # Load user function
# @login_manager.user_loader
# def load_user(user_id):
#     return User(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/layout')
# @login_required
def layout():
    return render_template('layout.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    return render_template('index.html')

@app.route('/customer/home')
@app.route('/customer/category')
def category():
    return render_template('customer/category.html')

@app.route('/customer/cart')
def cart():
    return render_template('customer/cart.html')

@app.route('/retailer/home')
@app.route('/retailer/current_orders')
def current_orders():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    select od.order_id, p.product_name, od.quantity, od.unit_price, od.status, od.order_date
    from OrderDetails as od
    join Products as p on od.product_id = p.product_id
    order by od.order_date desc
    """
    cursor.execute(query)
    orders = [
        {
            'order_id': row[0],
            'product_name': row[1],
            'quantity': row[2],
            'unit_price': row[3],
            'status': row[4],
            'order_date': row[5]
        }
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()
    return render_template('retailer/current_orders.html', orders=orders)

if __name__ == "__main__":
    app.run(debug=True)

