import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session
from config import get_db_connection, get_products
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import LoginManager, UserMixin, current_user, login_required

app = Flask(__name__)
app.secret_key = "1234"


# SQL Server connection

# def get_db_connection():
    
#     server = 'NICESS-LP264'  
#     database = 'retail management DB' 
#     username = 'sa' 
#     password = 'training@123'  

#     conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 13 for SQL Server};'
#         f'SERVER={server};'
#         f'DATABASE={database};'
#         f'UID={username};'
#         f'PWD={password};'
#     )

#     return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/layout')
def layout():
    return render_template('layout.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type').lower()

        conn = get_db_connection()
        cursor = conn.cursor()
        table = "Retailer" if user_type == "retailer" else "Customer"
        query = f"SELECT * FROM [{table}] WHERE username = ?"
        print(query)
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user[4] == password:
            session['user'] = user[1]
            session['user_type'] = user_type
            if user_type == "retailer":
                session['store_name'] = user[5]
                return redirect(url_for('current_orders'))
            else:
                return redirect(url_for('category'))
        else:
            return "Invalid Credentials"
    return render_template("login.html")

  
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        mobile =request.form.get('mobile_number')
        user_type = request.form.get('user_type')
        store_name = request.form.get('store_name') if user_type == "retailer" else None

        conn = get_db_connection()
        cursor = conn.cursor()

        if user_type == "retailer":
            query1 = '''
                INSERT INTO Retailer (full_name, username, email, password, address, store_name) 
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(query1, (name, username, email, password, address, store_name))

        else:
            query2 = '''
                INSERT INTO Customer (full_name, username, email, password, address) 
                VALUES (?, ?, ?, ?, ?)
            '''
            cursor.execute(query2, (name, username, email, password, address))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/logout') 
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chome')
@app.route('/customer/category')
def category():
    return render_template('customer/category.html')

# @app.route('/customer/cart')
# def cart():
#     # if 'user' not in session or session.get('user_type') != 'Customer':
#     #     print(session.get('user_type'))
#     #     return redirect(url_for('login'))
    
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     query = '''
#         SELECT p.product_name, c.quantity, p.unit_price, p.product_id 
#         FROM Cart as c
#         JOIN Products as p ON c.product_id = p.product_id
#         WHERE c.customer_id = (SELECT customer_id FROM Customer WHERE username = ?)
#     '''
#     cursor.execute(query, (session['user'],))
#     cart_items = [
#         {'product_name': row[0], 'quantity': row[1], 'unit_price': row[2], 'product_id': row[3]}
#         for row in cursor.fetchall()
#     ]
#     total = sum(item['price'] * item['quantity'] for item in cart_items)
#     cursor.close()
#     conn.close()
#     return render_template('customer/cart.html', cart_items=cart_items, total=total)

@app.route('/customer/cart')
def cart():
    # if 'user' not in session or session.get('user_type') != 'Customer':
    #     return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT p.product_name, c.quantity, p.unit_price, p.product_id 
        FROM Cart as c
        JOIN Products as p ON c.product_id = p.product_id
        WHERE c.customer_id = (SELECT customer_id FROM Customer WHERE username = ?)
    '''
    cursor.execute(query, (session['user'],))
    cart_items = [
        {'name': row[0], 'quantity': row[1], 'price': row[2], 'id': row[3]}
        for row in cursor.fetchall()
    ]
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    cursor.close()
    conn.close()
    return render_template('customer/cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'user' not in session or session.get('user_type') != 'Customer':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        DELETE FROM Cart
        WHERE customer_id = (SELECT customer_id FROM Customer WHERE username = ?)
        AND product_id = ?
    '''
    cursor.execute(query, (session['user'], product_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/customer/home')
def home():
    return render_template('customer/home.html')
    

@app.route('/customer/order_history')
def order_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT p.product_name, order_date, status, SUM(o.quantity * o.unit_price) AS total
        FROM OrderDetails as o
        join Products as p 
        on o.product_id=p.product_id
        GROUP BY p.product_name, order_date, status
        ORDER BY order_date DESC;
    '''
    
    cursor.execute(query)
    orders = [
        {
            'product_name': row[0],
            'date': row[1],
            'status': row[2],
            'total': row[3]
        }
        for row in cursor.fetchall()
    ]
    
    cursor.close()
    conn.close()
    return render_template('customer/order_history.html',orders=orders)

@app.route('/customer/subcategory')
def subcategory():
    return render_template('customer/subcategory.html')

# @app.route('/customer/product')
# def product():
#     search_query = request.args.get('query')
#     products = get_products(search_query) 
#     return render_template('product.html', products=products, search_query=search_query)

@app.route('/product.html')
def product():
    search_query = request.args.get('query', '')  
    products = get_products(search_query)
    return render_template('product.html', products=products, search_query=search_query)

@app.route('/rhome')
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

@app.route('/retailer/restock', methods=['GET', 'POST'])
def restock():
    conn = get_db_connection()
    cursor = conn.cursor()
 
    if request.method == 'POST':  # Handling form submission
        product_id = request.form['product_id']  # Get product_id from hidden input
        add_stock = int(request.form['add_stock'])  # Get entered quantity
 
        # Update inventory with the new stock
        update_query = '''
            UPDATE Inventory
            SET stock_qty = stock_qty + ?
            WHERE product_id = ?;
        '''
        cursor.execute(update_query, (add_stock, product_id))
        conn.commit()
 
    # Fetch products that need restocking
    fetch_query = '''
        SELECT p.product_id, p.product_name, i.stock_qty
        FROM Inventory AS i
        JOIN Products AS p ON i.product_id = p.product_id
        WHERE stock_qty < 110;
    '''
    cursor.execute(fetch_query)
 
    low_stock_products = [
        {
            'product_id': row[0],  
            'product_name': row[1],
            'stock_qty': row[2]
        }
        for row in cursor.fetchall()
    ]
 
    cursor.close()
    conn.close()
 
    return render_template('retailer/restock.html', low_stock_products=low_stock_products)

if __name__ == "__main__":
    app.run(debug=True)

