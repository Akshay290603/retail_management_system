import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session
from config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_required

app = Flask(__name__)
app.secret_key = "1234"


# SQL Server connection
def get_db_connection():
    # Replace with your actual details
    server = 'NICESS-LP264'  # Your SQL Server name or IP address
    database = 'retail management DB'  # Your database name
    username = 'sa'  # Your SQL Server username
    password = 'training@123'  # Your SQL Server password


    # Establish connection using ODBC Driver 13 for SQL Server
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 13 for SQL Server};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
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
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        conn = get_db_connection()
        cursor = conn.cursor()

        table = "Retailers" if user_type == "retailer" else "Customers"
        cursor.execute(f"SELECT * FROM {table} WHERE email = ?", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user'] = user[1]
            session['user_type'] = user_type

            if user_type == "retailer":
                session['store_name'] = user[4] 

            return redirect(url_for('home'))
        else:
            return " Invalid Credentials"

    return render_template("login.html")
    

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

@app.route('/customer/home')
def home():
    return render_template('customer/home.html')

@app.route('/customer/order_history')
def order_history():
    return render_template('customer/order_history.html')

@app.route('/customer/subcategory')
def subcategory():
    return render_template('customer/subcategory.html')

@app.route('/customer/product')
def product():
    return render_template('customer/product.html')

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

@app.route('/retailer/customer_management')
def customer_management():
    conn=get_db_connection()
    cursor=conn.cursor()

    query= '''
        select customer_id, full_name, email, mobile_number 
        from customer;
    '''

    cursor.execute(query)

    customers=[
        {
            'customer_id':row[0],
            'full_name':row[1],
            'email':row[2],
            'mobile_number':row[3]
        }
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return render_template('retailer/customer_management.html',customers=customers)

@app.route('/retailer/dashboard')
def dashboard():
    return render_template('retailer/dashboard.html')

@app.route('/retailer/expired_products')
def expired_products():
    return render_template('retailer/expired_products.html')

@app.route('/retailer/product_analysis')
def product_analysis():
    return render_template('retailer/product_analysis.html')

@app.route('/retailer/restock')
def restock():
    return render_template('retailer/restock.html')

if __name__ == "__main__":
    app.run(debug=True)

