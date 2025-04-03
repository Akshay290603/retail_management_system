import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session
from config import get_db_connection, get_products
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "1234"

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
            session['user'] = user[2]
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
        mobile =request.form.get('mobile')
        user_type = request.form.get('user_type')
        store_name = request.form.get('store_name') if user_type == "retailer" else None

        conn = get_db_connection()
        cursor = conn.cursor()

        if user_type == "retailer":
            query1 = '''
                INSERT INTO Retailer (full_name, username, email, password, address, mobile_number, store_name) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(query1, (name, username, email, password, address, mobile, store_name))

        else:
            query2 = '''
                INSERT INTO Customer (full_name, username, email, password, address, mobile_number) 
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(query2, (name, username, email, password, address , mobile))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/logout') 
def logout():
    se=session.get('user_type').lower()
    session.pop(se,None) 
    print(se)
    return redirect(url_for('login'))

@app.route('/chome')
@app.route('/customer/category')
def category():
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))
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
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT p.product_name, c.quantity, p.unit_price, p.product_id 
        FROM cart as c
        JOIN Products as p ON c.product_id = p.product_id
        WHERE c.customer_id = (SELECT customer_id FROM Customer WHERE username = ?)
    '''
    cursor.execute(query, (session['user'],))
    print(session['user'])
    print(query)
    cart_items = [
        {'product_name': row[0], 'quantity': row[1], 'unit_price': row[2], 'product_id': row[3]}
        for row in cursor.fetchall()
    ]
    total = sum(item['unit_price'] * item['quantity'] for item in cart_items)
    cursor.close()
    conn.close()
    return render_template('customer/cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product already in cart
    cursor.execute('''
        SELECT quantity FROM Cart 
        WHERE product_id = ? AND customer_id = (SELECT customer_id FROM Customer WHERE username = ?)
    ''', (product_id, session['user']))
    result = cursor.fetchone()
    
    if result:
        # Update quantity
        cursor.execute('''
            UPDATE Cart 
            SET quantity = quantity + 1 
            WHERE product_id = ? AND customer_id = (SELECT customer_id FROM Customer WHERE username = ?)
        ''', (product_id, session['user']))
    else:
        # Add new product to cart
        cursor.execute('''
            INSERT INTO Cart (customer_id, product_id, quantity) 
            VALUES ((SELECT customer_id FROM Customer WHERE username = ?), ?, 1)
        ''', (session['user'], product_id))
    
    


    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    # Remove product from cart
    cursor.execute('''DELETE FROM Cart WHERE product_id = ? AND customer_id = (SELECT customer_id FROM Customer WHERE username = ?)''', (product_id, session['user']))
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

@app.route('/customer/product')
def products_show():
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
 
    query = """
        select product_name, description, unit_price, subcategory_id, image_name, product_id
        from Products
        where product_name like ? ;
    """
    search_query = request.args.get('query', '')
    cursor.execute(query, ('%' + search_query + '%',))
    products = [
        {   
            'product_name': row[0],
            'description': row[1],
            'unit_price': row[2],
            'subcategory_id': row[3],
            'image_name': row[4],
            'product_id': row[5]
        }
        for row in cursor.fetchall()
    ]
 
    cursor.close()
    conn.close()
    return render_template('customer/product.html', products=products)

# @app.route('/product.html')
# def product():
#     search_query = request.args.get('query', '')  
#     products = get_products(search_query)

#     return render_template('product.html', products=products, search_query=search_query)

@app.route('/rhome')
@app.route('/retailer/current_orders')
def current_orders():
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))
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
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))
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
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))
    return render_template('retailer/dashboard.html')

@app.route('/retailer/expired_products')
def expired_products():
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))
    return render_template('retailer/expired_products.html')

@app.route('/retailer/product_analysis')
def product_analysis():
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))
    return render_template('retailer/product_analysis.html')

@app.route('/retailer/restock', methods=['GET', 'POST'])
def restock():
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':  # Handling form submission
        product_id = request.form['product_id']  # Get product_id from hidden input
        add_stock = int(request.form['add_stock'])  # Get entered quantity
        print(f"Product ID: {product_id}, Add Stock: {add_stock}")

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

