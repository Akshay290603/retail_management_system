# import pyodbc
import re
from flask import Flask, render_template, request, redirect, url_for, session,flash
from config import get_db_connection, get_products
# from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "1234"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/layout')
def layout():
    return render_template('layout.html',address=session.get('user_address','No address found'))


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
            session['user_id']=user[0]
            session['user'] = user[2]
            session['user_type'] = user_type
            session['address']= user[5]
            if user_type == "retailer":
                session['store_name'] = user[7]
                return redirect(url_for('current_orders'))
            else:
                return redirect(url_for('category'))
        else:
            return "Invalid Credentials"
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    errors = {}
    if request.method == 'POST':
        name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        mobile = request.form.get('mobile')
        user_type = request.form.get('user_type')
        store_name = request.form.get('store_name') if user_type == "retailer" else None

        # Validate username
        if not username:
            errors['username'] = "Username is required!"

        # Validate password
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            errors['password'] = "Password must be at least 8 characters long, with uppercase, lowercase, a number, and a special character."

        # Validate mobile number
        if not re.match(r'^\d{10}$', mobile):
            errors['mobile'] = "Mobile number must be exactly 10 digits."

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for duplicate username
        cursor.execute('SELECT username FROM Retailer WHERE username = ? UNION SELECT username FROM Customer WHERE username = ?', (username, username))
        if cursor.fetchone():
            errors['username'] = "Username already exists. Please choose a different username."

        # Check for duplicate email
        cursor.execute('SELECT email FROM Retailer WHERE email = ? UNION SELECT email FROM Customer WHERE email = ?', (email, email))
        if cursor.fetchone():
            errors['email'] = "Email already exists. Please use a different email."

        if errors:
            cursor.close()
            conn.close()
            return render_template('register.html', errors=errors)

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
            cursor.execute(query2, (name, username, email, password, address, mobile))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('login'))

    return render_template("register.html", errors=errors)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     errors={}
#     if request.method == 'POST':
#         name = request.form.get('full_name')
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         address = request.form.get('address')
#         mobile =request.form.get('mobile')
#         user_type = request.form.get('user_type')
#         store_name = request.form.get('store_name') if user_type == "retailer" else None
 

#         # Validate username
#         if not username:
#             errors['username'] = "Username is required!"
 
#         # Validate password
#         if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
#             errors['password'] = "Password must be at least 8 characters long, with uppercase, lowercase, a number, and a special character."
 
#         # Validate mobile number
#         if not re.match(r'^\d{10}$', mobile):
#             errors['mobile'] = "Mobile number must be exactly 10 digits."
 
#         if errors:
#             return render_template('register.html', errors=errors)

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         if user_type == "retailer":
#             query1 = '''
#                 INSERT INTO Retailer (full_name, username, email, password, address, mobile_number, store_name)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             '''
#             cursor.execute(query1, (name, username, email, password, address, mobile, store_name))
 
#         else:
#             query2 = '''
#                 INSERT INTO Customer (full_name, username, email, password, address, mobile_number)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             '''
#             cursor.execute(query2, (name, username, email, password, address , mobile))
 
#         conn.commit()
#         cursor.close()
#         conn.close()
 
#         return redirect(url_for('login'))
 
#     return render_template("register.html",errors=errors)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     errors = {}
#     if request.method == 'POST':
#         name = request.form.get('full_name')
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         address = request.form.get('address')
#         mobile =request.form.get('mobile')
#         user_type = request.form.get('user_type')
#         store_name = request.form.get('store_name') if user_type == "retailer" else None
    
#         # Validate username
#         if not username:
#             errors['username'] = "Username is required!"
 
#         # Validate password
#         if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
#             errors['password'] = "Password must be at least 8 characters long, with uppercase, lowercase, a number, and a special character."
 
#         # Validate mobile number
#         if not re.match(r'^\d{10}$', mobile):
#             errors['mobile'] = "Mobile number must be exactly 10 digits."
 
#         if errors:
#             return render_template('register.html', errors=errors)
 

#         conn = get_db_connection()
#         cursor = conn.cursor()
 
#         if user_type == "retailer":
#             query1 = '''
#                 INSERT INTO Retailer (full_name, username, email, password, address, mobile_number, store_name)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             '''
#             cursor.execute(query1, (name, username, email, password, address, mobile, store_name))
 
#         else:
#             query2 = '''
#                 INSERT INTO Customer (full_name, username, email, password, address, mobile_number)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             '''
#             cursor.execute(query2, (name, username, email, password, address , mobile))
 
#         conn.commit()
#         cursor.close()
#         conn.close()
 
#         return redirect(url_for('login'))
 
#     return render_template("register.html", errors={})


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     errors = {}
 
#     if request.method == 'POST':
#         name = request.form.get('full_name')
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         address = request.form.get('address')
#         mobile =request.form.get('mobile')
#         user_type = request.form.get('user_type')
#         store_name = request.form.get('store_name') if user_type == "retailer" else None
 
#         # Validate username
#         if not username:
#             errors['username'] = "Username is required!"
 
#         # Validate password
#         if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
#             errors['password'] = "Password must be at least 8 characters long, with uppercase, lowercase, a number, and a special character."
 
#         # Validate mobile number
#         if not re.match(r'^\d{10}$', mobile):
#             errors['mobile'] = "Mobile number must be exactly 10 digits."
 
#         if errors:
#             return render_template('register.html', errors=errors)
 
#         # Proceed with database insertion if no errors
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         if user_type == "retailer":
#             query1 = '''
#                 INSERT INTO Retailer (full_name, username, email, password, address, mobile_number, store_name)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             '''
#             cursor.execute(query1, (name, username, email, password, address, mobile, store_name))
 
#         else:
#             query2 = '''
#                 INSERT INTO Customer (full_name, username, email, password, address, mobile_number)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             '''
#             cursor.execute(query2, (name, username, email, password, address , mobile))
 
        
#         conn.commit()
#         cursor.close()
#         conn.close()
 
#         flash("Registration successful!", "success")
#         return redirect(url_for('login'))
 
#     return render_template("register.html", errors={})

@app.route('/retailer/update_order_status', methods=['POST'])
def update_order_status():
    # Ensure only a retailer can update order statuses
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))
    
    order_id = request.form.get('order_id')
    new_status = request.form.get('status')
    
    # Validate that both values are provided
    if not order_id or not new_status:
        flash("Order ID or status missing.", "danger")
        return redirect(url_for('current_orders'))
    
    # Update the order status in the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "UPDATE OrderDetails SET status = ? WHERE order_id = ?"
    try:
        cursor.execute(query, (new_status, order_id))
        conn.commit()
        flash("Order status updated successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash("Error updating order status: " + str(e), "danger")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('current_orders'))


def fetch_user_address():
    if 'user' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
 
            query = "SELECT address FROM Customer WHERE username = ?;"
            cursor.execute(query, (session['user'],))
            customer_address = cursor.fetchone()
 
            session['user_address'] = customer_address[0] if customer_address else "No address found"
 
        except Exception as e:
            print("Error fetching user address:", e)
            session['user_address'] = "Error fetching address"
 
        finally:
            cursor.close()
            conn.close()
 

@app.route('/logout') 
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chome')
@app.route('/customer/category')
def category():
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))
    return render_template('customer/category.html')

@app.route('/subcategory/<subcategory>')
def subcategory(subcategory):
    conn = get_db_connection()
    cursor = conn.cursor()
 
    query = '''
        SELECT p.product_name, p.description, p.unit_price, s.subcategory_id, p.image_name, p.product_id
        FROM Products p
        JOIN ProductSubcategory s ON p.subcategory_id = s.subcategory_id
        WHERE s.subcategory_name = ?;
        '''
 
    cursor.execute(query, (subcategory,))
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
 
    return render_template('customer/product.html', subcategory=subcategory, products=products)

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

# @app.route('/checkout', methods=['POST'])
# def checkout():
#     if 'user' not in session or session.get('user_type').lower() != 'customer':
#         return redirect(url_for('login'))

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Fetch cart items for the current customer
#     customer_id = session.get('user_id')
#     cursor.execute('''
#         SELECT cart_id, product_id, quantity
#         FROM Cart
#         WHERE customer_id = ?;
#     ''', (customer_id,))
#     cart_items = cursor.fetchall()

#     # Generate a new order ID
#     cursor.execute('''
#         INSERT INTO Orders (customer_id, order_date, status)
#         VALUES (?, CURRENT_TIMESTAMP, 'Pending');
#     ''', (customer_id,))
#     conn.commit()

#     # Get the generated order_id
#     cursor.execute('SELECT SCOPE_IDENTITY();')
#     order_id = cursor.fetchone()[0]

#     print(f"Customer ID: {customer_id}")
#     print(f"Order ID: {order_id}")
#     for item in cart_items:
#         print(f"Product ID: {item[1]}, Quantity: {item[2]}")

#     # Insert cart items into OrderDetails and update Inventory
#     for item in cart_items:
#         # Fetch retailer_id and unit_price for each product from Inventory
#         cursor.execute('''
#             SELECT retailer_id, unit_price
#             FROM Inventory
#             JOIN Products ON Inventory.product_id = Products.product_id
#             WHERE Inventory.product_id = ?;
#         ''', (item[1],))  # Access the product_id correctly
#         inventory_item = cursor.fetchone()

#         if inventory_item:
#             retailer_id = inventory_item[0]
#             unit_price = inventory_item[1]

#             # Insert into OrderDetails without specifying the identity column
#             cursor.execute('''
#                 INSERT INTO OrderDetails (retailer_id, customer_id, order_date, status, product_id, quantity, unit_price)
#                 VALUES (?, ?, CURRENT_TIMESTAMP, 'Pending', ?, ?, ?);
#             ''', (retailer_id, customer_id, item[1], item[2], unit_price))

#             # Update Inventory
#             cursor.execute('''
#                 UPDATE Inventory
#                 SET stock_qty = stock_qty - ?
#                 WHERE product_id = ? AND retailer_id = ?;
#             ''', (item[2], item[1], retailer_id))
#         else:
#             # Handle the case where there is no mapping
#             print(f"No retailer found for product_id: {item[1]}")

#     # Delete cart items after successful checkout
#     cursor.execute('''
#         DELETE FROM Cart
#         WHERE customer_id = ?;
#     ''', (customer_id,))
#     conn.commit()

#     cursor.close()
#     conn.close()

#     return redirect(url_for('order_history'))


@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch cart items for the current customer
    customer_id = session.get('user_id')
    customer_id = session.get('user_id')
    cursor.execute('''
        SELECT c.cart_id, c.product_id, c.quantity, p.product_name, p.unit_price
        FROM Cart AS c
        JOIN Products AS p ON c.product_id = p.product_id
        WHERE c.customer_id = ?;
    ''', (customer_id,))
    cart_items = cursor.fetchall()

    # Generate a new order ID
    cursor.execute('''
        INSERT INTO Orders (customer_id, order_date, status)
        VALUES (?, CURRENT_TIMESTAMP, 'Pending');
    ''', (customer_id,))
    conn.commit()

    # Get the generated order_id
    cursor.execute('SELECT SCOPE_IDENTITY();')
    order_id = cursor.fetchone()[0]

    print(f"Customer ID: {customer_id}")
    print(f"Order ID: {order_id}")
    for item in cart_items:
        print(f"Product ID: {item[1]}, Quantity: {item[2]}")

    out_of_stock_products = []

    # Insert cart items into OrderDetails and update Inventory
    for item in cart_items:
        # Fetch retailer_id and unit_price for each product from Inventory
        cursor.execute('''
            SELECT retailer_id, unit_price
            FROM Inventory
            JOIN Products ON Inventory.product_id = Products.product_id
            WHERE Inventory.product_id = ?;
        ''', (item[1],))  # Access the product_id correctly
        inventory_item = cursor.fetchone()

        if inventory_item:
            retailer_id = inventory_item[0]
            unit_price = inventory_item[1]

            # Insert into OrderDetails without specifying the identity column
            cursor.execute('''
                INSERT INTO OrderDetails (retailer_id, customer_id, order_date, status, product_id, quantity, unit_price)
                 VALUES (?, ?, CURRENT_TIMESTAMP, 'Pending', ?, ?, ?);
             ''', (retailer_id, customer_id, item[1], item[2], unit_price))

            # Update Inventory
            cursor.execute('''
                UPDATE Inventory
                SET stock_qty = stock_qty - ?
                WHERE product_id = ? AND retailer_id = ?;
            ''', (item[2], item[1], retailer_id))
        else:
            # Add the product to the out_of_stock_products list
            out_of_stock_products.append(item[1])
            print(f"No retailer found for product_id: {item[1]}")

    if out_of_stock_products:
        # Handle the case where some products are out of stock
        out_of_stock_message = "The following products are out of stock: " 
        return render_template('customer/cart.html', error_message=out_of_stock_message, cart_items=cart_items)

    # Delete cart items after successful checkout
    cursor.execute('''
        DELETE FROM Cart
        WHERE customer_id = ?;
    ''', (customer_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('order_history'))

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

@app.route('/retailer/inventory', methods=['GET', 'POST'])
def manage_inventory():
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        product_id = request.form['product_id']
        stock_qty = int(request.form['stock_qty'])
        retailer_id = session.get('user_id')

        # Insert or update the inventory
        cursor.execute('''
            IF EXISTS (SELECT 1 FROM Inventory WHERE product_id = ? AND retailer_id = ?)
            BEGIN
                UPDATE Inventory
                SET stock_qty = stock_qty + ?
                WHERE product_id = ? AND retailer_id = ?;
            END
            ELSE
            BEGIN
                INSERT INTO Inventory (product_id, retailer_id, stock_qty, reorder_level)
                VALUES (?, ?, ?, 10);
            END
        ''', (product_id, retailer_id, stock_qty, product_id, retailer_id, product_id, retailer_id, stock_qty))
        conn.commit()

    # Fetch all products for the dropdown
    cursor.execute('SELECT product_id, product_name FROM Products')
    products = cursor.fetchall()

    # Fetch the retailer's inventory
    cursor.execute('''
        SELECT p.product_name, i.stock_qty, i.reorder_level
        FROM Inventory AS i
        JOIN Products AS p ON i.product_id = p.product_id
        WHERE i.retailer_id = ?;
    ''', (session.get('user_id'),))
    inventory_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('retailer/inventory.html', products=products, inventory_items=inventory_items)

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

# @app.route('/retailer/expired_products')
# def expired_products():
#     if 'user' not in session or session.get('user_type').lower() != 'retailer':
#         return redirect(url_for('login'))
#     return render_template('retailer/expired_products.html')

# @app.route('/retailer/product_analysis')
# def product_analysis():
#     if 'user' not in session or session.get('user_type').lower() != 'retailer':
#         return redirect(url_for('login'))
#     return render_template('retailer/product_analysis.html')

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

