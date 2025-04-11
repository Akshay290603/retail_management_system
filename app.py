# import pyodbc
import re
from flask import Flask, render_template, request, redirect, url_for, session,flash
from config import get_db_connection, get_products
import pandas as pd 
import plotly.express as px
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
            session['city']= user[6]
            if user_type == "retailer":
                session['store_name'] = user[7]
                return redirect(url_for('current_orders'))
            else:
                return redirect(url_for('category'))
        else:
            return render_template("login.html", error="Invalid Credentials")
    else:
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
        city = request.form.get('city')
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
            return render_template('register.html', errors=errors, form_data=request.form)
 
        if user_type == "retailer":
            query1 = '''
                INSERT INTO Retailer (full_name, username, email, password, address, city, mobile_number, store_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(query1, (name, username, email, password, address, city, mobile, store_name))
 
        else:
            query2 = '''
                INSERT INTO Customer (full_name, username, email, password, address, city, mobile_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(query2, (name, username, email, password, address, city, mobile))
 
        conn.commit()
        cursor.close()
        conn.close()
 
        return redirect(url_for('login'))
 
    return render_template("register.html", errors=errors, form_data={})

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

    query2='''
        select quantity 
        from OrderDetails
        where order_id = ?
    '''
    cursor.execute(query2,(order_id))

    result=cursor.fetchone()

    qunatity=result[0]

    print(qunatity)
    query = "UPDATE OrderDetails SET status = ? WHERE order_id = ?"
    try:
        cursor.execute(query, (new_status, order_id))
        
        if new_status == 'Completed':
            query1= '''
                update inventory 
                set stock_qty = stock_qty - ?
                where retailer_id = ?
            '''
            cursor.execute(query1,(qunatity,session['user_id'] ))

        conn.commit()
        flash("Order status updated successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash("Error updating order status: " + str(e), "danger")
    finally:
        cursor.close()
        conn.close()

    
    return redirect(url_for('current_orders'))


# @app.route('/retailer/update_order_status', methods=['POST'])
# def update_order_status():
#     if 'user' not in session or session.get('user_type').lower() != 'retailer':
#         return redirect(url_for('login'))
    
#     order_id = request.form.get('order_id')
#     new_status = request.form.get('status')
    
#     if not order_id or not new_status:
#         flash("Order ID or status missing.", "danger")
#         return redirect(url_for('current_orders'))
    
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     try:
#         # Step 1: Get order quantity
#         order_qty_query = '''
#             SELECT quantity 
#             FROM orderdetails
#             WHERE order_id = ?
#         '''
#         cursor.execute(order_qty_query, order_id)
#         result = cursor.fetchone()
#         if result is None:
#             flash("Order not found.", "danger")
#             return redirect(url_for('current_orders'))
        
#         quantity = result[0]

#         # Step 2: Update order status
#         update_order_query = "UPDATE OrderDetails SET status = ? WHERE order_id = ?"
#         cursor.execute(update_order_query, (new_status, order_id))

#         # Step 3: Reduce stock in inventory
#         update_stock_query = '''
#             UPDATE inventory 
#             SET stock_qty = stock_qty - ?
#             WHERE order_id = ?
#         '''
#         cursor.execute(update_stock_query, (quantity, order_id))

#         conn.commit()
#         flash("Order status and inventory updated successfully!", "success")
#     except Exception as e:
#         conn.rollback()
#         flash("Error updating order status: " + str(e), "danger")
#     finally:
#         cursor.close()
#         conn.close()
    
#     return redirect(url_for('current_orders'))


def fetch_user_address():
    if 'user' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
 
            query = "SELECT address FROM Customer WHERE username = ?;"
            cursor.execute(query, (session['user'],))
            customer_address = cursor.fetchone()
 
            session['user_address'] = customer_address if customer_address else "No address found"
 
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
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))
 
    conn = get_db_connection()
    cursor = conn.cursor()
 
    customer_id = session.get('user_id')
 
    # Fetch all products in the specified subcategory with inventory and retailer details
    query = '''
        SELECT p.product_name, p.description, i.MRP, s.subcategory_id, p.image_name, p.product_id, r.store_name, r.retailer_id
        FROM Products p
        JOIN ProductSubcategory s ON p.subcategory_id = s.subcategory_id
        JOIN Inventory i on p.product_id = i.product_id
        JOIN Retailer r on i.retailer_id = r.retailer_id
        WHERE s.subcategory_name = ?;
    '''
    cursor.execute(query, (subcategory,))
    product_rows = cursor.fetchall()
 
    # Fetch discounts for this customer from each retailer
    cursor.execute("""
        SELECT d.retailer_id, d.discount
        FROM Discounts as d
        WHERE customer_id = ?
    """, (customer_id,))
    discount_dict = {row[0]: row[1] for row in cursor.fetchall()}
 
    products = []
    for row in product_rows:
        product_name = row[0]
        description = row[1]
        mrp = row[2]
        subcategory_id = row[3]
        image_name = row[4]
        product_id = row[5]
        store_name = row[6]
        retailer_id = row[7]
 
        # Ensure MRP is not None
        if mrp is None:
            mrp = 0.0
 
        discount_value = discount_dict.get(retailer_id, 0)
        final_price = round(mrp * (1 - discount_value / 100), 2) if discount_value > 0 else mrp
 
        products.append({
            'product_name': product_name,
            'description': description,
            'MRP': mrp,
            'subcategory_id': subcategory_id,
            'image_name': image_name,
            'product_id': product_id,
            'store_name': store_name,
            'retailer_id': retailer_id,
            'discount': discount_value,
            'final_price': final_price
        })
 
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
    SELECT 
    p.product_name, c.quantity, 
    CASE 
        WHEN d.discount > 0 THEN i.MRP * (1 - d.discount / 100)
        ELSE i.MRP
    END AS discounted_price, p.product_id, r.retailer_id, r.store_name
    FROM cart AS c JOIN 
    products AS p ON c.product_id = p.product_id
    JOIN 
    discounts AS d ON d.customer_id = c.customer_id 
    JOIN 
    inventory AS i ON p.product_id = i.product_id AND c.retailer_id = i.retailer_id
    JOIN 
    retailer AS r ON c.retailer_id = r.retailer_id
    WHERE 
    c.customer_id = ?

    '''
    cursor.execute(query, (session['user_id'],))
    cart_items = [
        {
            'product_name': row[0],
            'quantity': row[1],
            'unit_price': row[2],
            'product_id': row[3],
            'retailer_id': row[4],
            'retailer_name': row[5]
        }
        for row in cursor.fetchall()
    ]
 
    total = sum(item['unit_price'] * item['quantity'] for item in cart_items)
    cursor.close()
    conn.close()
    return render_template('customer/cart.html', cart_items=cart_items, total=total)

@app.route('/customer/payment_success')
def payment_success():
    # Handle post-payment logic here: order DB updates, email, etc.
    return render_template('customer/payment_success.html')


@app.route('/cart/increase/<int:product_id>/<int:retailer_id>', methods=['POST'])
def increase_quantity(product_id, retailer_id):
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Cart
        SET quantity = quantity + 1
        WHERE product_id = ? AND customer_id = ? AND retailer_id = ?
                   """, (product_id, session['user_id'], retailer_id))

    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('cart')) 

@app.route('/cart/decrease/<int:product_id>/<int:retailer_id>', methods=['POST'])
def decrease_quantity(product_id, retailer_id):
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

 
    cursor.execute("""
        UPDATE Cart
        SET quantity = quantity - 1
        WHERE product_id = ? AND customer_id = ? AND quantity > 1 AND retailer_id = ?
    """, (product_id, session['user_id'], retailer_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('cart'))

@app.route('/add_to_cart/<int:product_id>/<int:retailer_id>', methods=['POST'])
def add_to_cart(product_id, retailer_id):
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))
 
    conn = get_db_connection()
    cursor = conn.cursor()
 
    # Get customer_id using session username
    cursor.execute("SELECT customer_id FROM Customer WHERE username = ?", (session['user'],))
    customer_id = cursor.fetchone()[0]
 
    # Check if product from this retailer is already in cart
    cursor.execute('''
        SELECT quantity FROM Cart 
        WHERE product_id = ? AND retailer_id = ? AND customer_id = ?
    ''', (product_id, retailer_id, customer_id))
    result = cursor.fetchone()
 
    if result:
        # Update quantity
        cursor.execute('''
            UPDATE Cart 
            SET quantity = quantity + 1 
            WHERE product_id = ? AND retailer_id = ? AND customer_id = ?
        ''', (product_id, retailer_id, customer_id))
    else:
        # Add new product to cart
        cursor.execute('''
            INSERT INTO Cart (customer_id, product_id, retailer_id, quantity) 
            VALUES (?, ?, ?, 1)
        ''', (customer_id, product_id, retailer_id))
 
    conn.commit()
    cursor.close()
    conn.close()
 
    return redirect(request.referrer)


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
  
# working order history 

# @app.route('/customer/order_history')
# def order_history():
#     if 'user' not in session or session.get('user_type').lower() != 'customer':
#         return redirect(url_for('login'))
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     print(session['user'])
#     query = '''
#         SELECT p.product_name, order_date, status, SUM(o.quantity * o.unit_price) AS total
#         FROM OrderDetails as o
#         join Products as p 
#         on o.product_id=p.product_id
#         join customer c 
#         on o.customer_id=c.customer_id
#         where c.customer_id = ?
#         GROUP BY p.product_name, order_date, status
#         ORDER BY order_date DESC;
#     '''
    
#     cursor.execute(query,session['user_id'])
#     orders = [
#         {
#             'product_name': row[0],
#             'date': row[1],
#             'status': row[2],
#             'total': row[3]
#         }
#         for row in cursor.fetchall()
#     ]
    
#     cursor.close()
#     conn.close()
#     return render_template('customer/order_history.html',orders=orders)

# new order history 

# @app.route('/customer/order_history')
# def order_history():
#     if 'user' not in session or session.get('user_type').lower() != 'customer':
#         return redirect(url_for('login'))
    
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     query = '''
#         SELECT o.order_id, p.product_name, o.order_date, o.status,
#                SUM(o.quantity * o.unit_price) AS total
#         FROM OrderDetails AS o
#         JOIN Products AS p ON o.product_id = p.product_id
#         JOIN Customer AS c ON o.customer_id = c.customer_id
#         WHERE c.customer_id = ?
#         GROUP BY o.order_id, p.product_name, o.order_date, o.status
#         ORDER BY o.order_date DESC;
#     '''
    
#     cursor.execute(query, session['user_id'])
#     orders = [
#         {
#             'order_id': row[0],
#             'product_name': row[1],
#             'date': row[2],
#             'status': row[3],
#             'total': row[4]
#         }
#         for row in cursor.fetchall()
#     ]
#     # fetching the status from feedback table
#     query1='''
#         SELECT od.order_id, od.order_date, od.status, f.request,SUM(od.quantity * od.unit_price) AS total
#         FROM OrderDetails AS od
#         JOIN Feedback as f ON od.order_id = f.order_id
#         JOIN Customer AS c ON od.customer_id = c.customer_id 
#         WHERE c.customer_id = ?
#         GROUP BY od.order_id,od.order_date, od.status, f.request; 
#     '''

#     cursor.execute(query1,session['user_id'])

#     feedback_status = [
#         {
#             'request' : row[0],
#             'rating' : row[1]
#         }
#         for row in cursor.fetchall()
#     ]

#     cursor.close()
#     conn.close()
#     return render_template('customer/order_history.html', orders=orders, feedback_status=feedback_status)

@app.route('/customer/order_history')
def order_history():
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT o.order_id, p.product_name, o.order_date, o.status,
               SUM(o.quantity * o.unit_price) AS total,
               f.rating, f.feedback_description, f.request,o.quantity,f.r_quantity
        FROM OrderDetails AS o
        JOIN Products AS p ON o.product_id = p.product_id
        JOIN Customer AS c ON o.customer_id = c.customer_id
        LEFT JOIN Feedback AS f ON o.order_id = f.order_id
        WHERE c.customer_id = ?
        GROUP BY o.order_id, p.product_name, o.order_date, o.status,
                 f.rating, f.feedback_description, f.request, o.quantity,f.r_quantity
        ORDER BY o.order_date DESC;
    '''

    cursor.execute(query, session['user_id'])

    orders = []
    for row in cursor.fetchall():
        orders.append({
            'order_id': row[0],
            'product_name': row[1],
            'date': row[2],
            'status': row[3],
            'total': row[4],
            'rating': row[5],  
            'feedback_description': row[6], 
            'request': row[7],
            'order_qunatity' : row[8],
            'return_quantity' : row[9]
        })

    cursor.close()
    conn.close()

    return render_template('customer/order_history.html', orders=orders)


# feedback functionality
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))

    order_id = request.form['order_id']
    rating = request.form['rating']
    description = request.form.get('feedback_description', '')
    request_type = request.form.get('request', '')
    return_quantity = request.form.get('return_quantity')

    customer_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get product_id, retailer_id and order quantity
    cursor.execute('''
        SELECT product_id, retailer_id, quantity FROM OrderDetails WHERE order_id = ?
    ''', (order_id,))
    result = cursor.fetchone()

    if result:
        product_id, retailer_id, ordered_quantity = result

        # Validate return quantity only if Return or Replace is selected
        if request_type in ['Return', 'Replace']:
            try:
                return_quantity = int(return_quantity or 0)
                if return_quantity < 1 or return_quantity > ordered_quantity:
                    flash(f"⚠️ Return quantity must be between 1 and {ordered_quantity}.", 'danger')
                    return redirect(url_for('order_history'))
            except ValueError:
                flash("⚠️ Invalid return quantity entered.", 'danger')
                return redirect(url_for('order_history'))
        else:
            return_quantity = None  # Ignore if no return/replace is selected

        # Insert into Feedback table
        cursor.execute('''
            INSERT INTO Feedback (order_id, product_id, retailer_id, customer_id, rating, feedback_description, request, r_quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, product_id, retailer_id, customer_id, rating, description, request_type, return_quantity))

        conn.commit()

    cursor.close()
    conn.close()

    flash('✅ Thank you for your feedback!', 'success')
    return redirect(url_for('order_history'))


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
    customer_id = session.get('user_id')

    # Fetch cart items with retailer info (including store name)
    cursor.execute('''
        SELECT c.cart_id, c.product_id, c.quantity, p.product_name, i.mrp, c.retailer_id, r.store_name
        FROM Cart AS c
        JOIN Products AS p ON c.product_id = p.product_id
        JOIN Inventory AS i ON i.product_id = c.product_id AND i.retailer_id = c.retailer_id
        JOIN Retailer AS r ON c.retailer_id = r.retailer_id
        WHERE c.customer_id = ?;
    ''', (customer_id,))
    cart_items = cursor.fetchall()

    out_of_stock_products = []
    order_ids = {}  # Mapping of retailer_id to order_id

    for item in cart_items:
        cart_id = item.cart_id
        product_id = item.product_id
        quantity = item.quantity
        product_name = item.product_name
        mrp = item.mrp
        retailer_id = item.retailer_id

        # Create order per retailer
        if retailer_id not in order_ids:
            cursor.execute('''
                INSERT INTO Orders (customer_id, retailer_id, order_date, status)
                VALUES (?, ?, CURRENT_TIMESTAMP, 'Pending');
            ''', (customer_id, retailer_id))
            conn.commit()

            cursor.execute('SELECT SCOPE_IDENTITY();')
            order_ids[retailer_id] = cursor.fetchone()[0]

        order_id = order_ids[retailer_id]

        # Check stock
        cursor.execute('''
            SELECT stock_qty FROM Inventory
            WHERE product_id = ? AND retailer_id = ?;
        ''', (product_id, retailer_id))
        stock_result = cursor.fetchone()

        if stock_result and stock_result[0] >= quantity:
            # Insert into OrderDetails
            cursor.execute('''
                INSERT INTO OrderDetails (retailer_id, customer_id, order_date, status, product_id, quantity, unit_price)
                VALUES (?, ?, CURRENT_TIMESTAMP, 'Pending', ?, ?, ?);
            ''', (retailer_id, customer_id, product_id, quantity, mrp))

            # Update inventory
            cursor.execute('''
                UPDATE Inventory
                SET stock_qty = stock_qty - ?
                WHERE product_id = ? AND retailer_id = ?;
            ''', (quantity, product_id, retailer_id))
        else:
            out_of_stock_products.append(product_name)

    if out_of_stock_products:
        # Convert pyodbc.Row objects to dicts for Jinja2
        cart_items_dicts = [
            {
                'product_name': item.product_name,
                'quantity': item.quantity,
                'unit_price': item.mrp,
                'product_id': item.product_id,
                'retailer_id': item.retailer_id,
                'retailer_name': item.store_name
            }
            for item in cart_items
        ]

        error_message = "The following products are out of stock: " + ", ".join(out_of_stock_products)
        return render_template('customer/cart.html', error_message=error_message, cart_items=cart_items_dicts)

    # Clear cart after checkout
    cursor.execute('DELETE FROM Cart WHERE customer_id = ?;', (customer_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('order_history'))


# @app.route('/checkout', methods=['POST'])
# def checkout():
#     if 'user' not in session or session.get('user_type').lower() != 'customer':
#         return redirect(url_for('login'))
 
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     customer_id = session.get('user_id')
 
#     # Fetch cart items with retailer-specific info
#     cursor.execute('''
#         SELECT c.cart_id, c.product_id, c.quantity, p.product_name, i.mrp, c.retailer_id
#         FROM Cart AS c
#         JOIN Products AS p ON c.product_id = p.product_id
#         JOIN Inventory AS i ON i.product_id = c.product_id AND i.retailer_id = c.retailer_id
#         WHERE c.customer_id = ?;
#     ''', (customer_id,))
#     cart_items = cursor.fetchall()
 
#     out_of_stock_products = []
#     order_ids = {}  # Mapping of retailer_id to order_id
 
#     # Create a separate order for each retailer
#     for item in cart_items:
#         cart_id, product_id, quantity, product_name, mrp, retailer_id = item
 
#         # Create order only if it doesn't already exist for this retailer
#         if retailer_id not in order_ids:
#             cursor.execute('''
#                 INSERT INTO Orders (customer_id, retailer_id, order_date, status)
#                 VALUES (?, ?, CURRENT_TIMESTAMP, 'Pending');
#             ''', (customer_id, retailer_id))
#             conn.commit()
 
#             cursor.execute('SELECT SCOPE_IDENTITY();')
#             order_ids[retailer_id] = cursor.fetchone()[0]
 
#         order_id = order_ids[retailer_id]
 
#         # Check stock
#         cursor.execute('''
#             SELECT stock_qty FROM Inventory
#             WHERE product_id = ? AND retailer_id = ?;
#         ''', (product_id, retailer_id))
#         stock_result = cursor.fetchone()
 
#         if stock_result and stock_result[0] >= quantity:
#             # Insert into OrderDetails
#             cursor.execute('''
#                 INSERT INTO OrderDetails (retailer_id, customer_id, order_date, status, product_id, quantity, unit_price)
#                 VALUES (?, ?, CURRENT_TIMESTAMP, 'Pending', ?, ?, ?);
#             ''', (retailer_id, customer_id, product_id, quantity, mrp))


 
#             # Update inventory
#             cursor.execute('''
#                 UPDATE Inventory
#                 SET stock_qty = stock_qty - ?
#                 WHERE product_id = ? AND retailer_id = ?;
#             ''', (quantity, product_id, retailer_id))
#         else:
#             out_of_stock_products.append(product_name)
 
#     if out_of_stock_products:
#         error_message = "The following products are out of stock: " + ", ".join(out_of_stock_products)
#         return render_template('customer/cart.html', error_message=error_message, cart_items=cart_items)
 
#     # Clear cart after checkout
#     cursor.execute('DELETE FROM Cart WHERE customer_id = ?;', (customer_id,))
#     conn.commit()
 
#     cursor.close()
#     conn.close()
 
#     return redirect(url_for('order_history'))


# @app.route('/customer/product')
# def products_show():
#     if 'user' not in session or session.get('user_type').lower() != 'customer':
#         return redirect(url_for('login'))
#     conn = get_db_connection()
#     cursor = conn.cursor()
 
#     query = """
#         select p.product_name, p.description, p.unit_price, p.subcategory_id, p.image_name, p.product_id, i.stock_qty, r.retailer_id, r.store_name
#         from Products as p
#         join Inventory as i on p.product_id = i.product_id
#         join retailer as r on i.retailer_id = r.retailer_id
#         where p.product_name like ? ;
#     """
#     search_query = request.args.get('query', '')
#     print("Search Query:", search_query)
#     cursor.execute(query, ('%' + search_query + '%',))
#     rows = cursor.fetchall()
   
#     products = [
#         {  
#             'product_name': row[0],
#             'description': row[1],
#             'unit_price': row[2],
#             'subcategory_id': row[3],
#             'image_name': row[4],
#             'product_id': row[5],
#             'stock_qty': row[6],
#             'retailer_id': row[7],
#             'store_name': row[8]
#         }
#         for row in rows
#     ]
 
#     cursor.close()
#     conn.close()
#     return render_template('customer/product.html', products=products)

@app.route('/customer/product')
def products_show():
    if 'user' not in session or session.get('user_type').lower() != 'customer':
        return redirect(url_for('login'))
 
    conn = get_db_connection()
    cursor = conn.cursor()
 
    customer_id = session.get('user_id')
    search_query = request.args.get('query', '')
 
    # Fetch all products with inventory and retailer details
    query = """
        SELECT
            p.product_name, p.description, i.MRP, p.subcategory_id,
            p.image_name, p.product_id, i.stock_qty,
            r.retailer_id, r.store_name, i.MRP, i.inventory_id
        FROM Products AS p
        JOIN Inventory AS i ON p.product_id = i.product_id
        JOIN Retailer AS r ON i.retailer_id = r.retailer_id
        WHERE p.product_name LIKE ?;
    """
    cursor.execute(query, ('%' + search_query + '%',))
    product_rows = cursor.fetchall()
 
    # Fetch discounts for this customer from each retailer
    cursor.execute("""
        SELECT d.retailer_id, d.discount, i.MRP
        FROM Discounts as d
        JOIN Inventory as i ON d.retailer_id = i.retailer_id
        WHERE customer_id = ?
    """, (customer_id,))
    discount_dict = {
    row[0]: {
        'discount': row[1],
        'MRP': row[2]
    }
    for row in cursor.fetchall()
    }
 
    products = []
    for row in product_rows:
        product_name = row[0]
        description = row[1]
        mrp = row[2]
        subcategory_id = row[3]
        image_name = row[4]
        product_id = row[5]
        stock_qty = row[6]
        retailer_id = row[7]
        store_name = row[8]
        inventory_id = row[9]
 
        
        discount_value = discount_dict.get(retailer_id, {'discount': 0}).get('discount', 0)
        final_price = round(mrp * (1 - discount_value / 100), 2) if discount_value > 0 else mrp

 
        products.append({
            'product_name': product_name,
            'description': description,
            'MRP': mrp,
            'subcategory_id': subcategory_id,
            'image_name': image_name,
            'product_id': product_id,
            'stock_qty': stock_qty,
            'retailer_id': retailer_id,
            'store_name': store_name,
            'discount': discount_value,
            'final_price': final_price,
            'inventory_id': inventory_id
        })
 
    cursor.close()
    conn.close()
    return render_template('customer/product.html', products=products)

# @app.route('/product.html')
# def product():
#     search_query = request.args.get('query', '')  
#     products = get_products(search_query)

#     return render_template('product.html', products=products, search_query=search_query)


def has_inventory(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM Inventory WHERE retailer_id = ?"
    cursor.execute(query, (user_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0

# @app.route('/rhome')
# @app.route('/retailer/current_orders')
# def current_orders():
#     if 'user' not in session or session.get('user_type').lower() != 'retailer':
#         return redirect(url_for('login'))
    
#     # if not has_inventory(session['user_id']):
#     #     return redirect(url_for('inventory'))

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     query = """
#     select od.order_id, p.product_name, od.quantity, od.unit_price, od.status, od.order_date
#     from OrderDetails as od
#     join Products as p on od.product_id = p.product_id
#     where od.retaier_id = ?
#     order by od.order_date desc
#     """
#     cursor.execute(query)
#     orders = [
#         {
#             'order_id': row[0],
#             'product_name': row[1],
#             'quantity': row[2],
#             'unit_price': row[3],
#             'status': row[4],
#             'order_date': row[5]
#         }
#         for row in cursor.fetchall()
#     ]

#     cursor.close()
#     conn.close()
#     return render_template('retailer/current_orders.html', orders=orders)

@app.route('/retailer/current_orders')
def current_orders():
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))
   
    if not has_inventory(session['user_id']):
        return redirect(url_for('manage_inventory'))  
 
    conn = get_db_connection()
    cursor = conn.cursor()
   
    query = """
    SELECT od.order_id, p.product_name, od.quantity, (i.mrp * od.quantity) as total_price , od.status, od.order_date, c.city
    FROM OrderDetails AS od
    JOIN Products AS p ON od.product_id = p.product_id
    JOIN Inventory AS i ON i.product_id = od.product_id AND i.retailer_id = od.retailer_id
    JOIN Customer AS c ON od.customer_id = c.customer_id
 
    WHERE i.retailer_id = ?
        AND od.quantity <= i.stock_qty
    ORDER BY
        CASE WHEN LOWER(c.city) = LOWER(?) THEN 0 ELSE 1 END,
        od.order_date DESC;
    """
   
    cursor.execute(query, (session['user_id'], session['city']))
    orders = [
        {
            'order_id': row[0],
            'product_name': row[1],
            'quantity': row[2],
            'total_price': row[3],
            'status': row[4],
            'order_date': row[5],
            'city': row[6]
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
 
    # Initialize for GET requests
    added_total = None
    added_product_name = None
    added_quantity = None
 
    if request.method == 'POST':
        product_id = request.form['product_id']
        stock_qty = int(request.form['stock_qty'])
        retailer_id = session.get('user_id')
        MRP = float(request.form['MRP'])
 
        # Fetch the unit price before updating the inventory
        cursor.execute('SELECT product_name, unit_price FROM Products WHERE product_id = ?', (product_id,))
        product_data = cursor.fetchone()
 
        if product_data:
            added_product_name = product_data.product_name
            unit_price = product_data.unit_price
            added_total = stock_qty * unit_price
            added_quantity = stock_qty
 
        # Insert or update inventory
        cursor.execute('''
            IF EXISTS (
                SELECT 1 FROM Inventory WHERE product_id = ? AND retailer_id = ?
            )
            BEGIN
                UPDATE Inventory
                SET prev_stock_qty = stock_qty,
                    stock_qty = stock_qty + ?,
                    MRP = ?
                WHERE product_id = ? AND retailer_id = ?;
            END
            ELSE
            BEGIN
                INSERT INTO Inventory (product_id, retailer_id, stock_qty, reorder_level, prev_stock_qty, MRP)
                VALUES (?, ?, ?, 10, 0, ?);
            END
        ''', (
            product_id, retailer_id,
            stock_qty, MRP,
            product_id, retailer_id,
            product_id, retailer_id, stock_qty, MRP
        ))
 
        conn.commit()
 
    # Fetch all products for dropdown
    cursor.execute('SELECT product_id, product_name, unit_price FROM Products')
    products = cursor.fetchall()
 
    # Fetch inventory
    cursor.execute('''
        SELECT p.product_name, i.stock_qty, i.reorder_level, i.prev_stock_qty, i.MRP
        FROM Inventory AS i
        JOIN Products AS p ON i.product_id = p.product_id
        WHERE i.retailer_id = ?;
    ''', (session.get('user_id'),))
    inventory_items = cursor.fetchall()
 
    cursor.close()
    conn.close()
 
    return render_template(
        'retailer/inventory.html',
        products=products,
        inventory_items=inventory_items,
        added_total=added_total,
        added_product_name=added_product_name,
        added_quantity=added_quantity
    )

@app.route('/retailer/customer_management', methods=['GET', 'POST'])
def customer_management():
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))
 
    conn = get_db_connection()
    cursor = conn.cursor()
    retailer_id = session.get('user_id')
 
    # Handle form submission for setting discounts
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        discount = float(request.form.get('discount'))
 
        # Check if discount already exists for this customer and retailer
        cursor.execute('''
            SELECT 1 FROM Discounts WHERE retailer_id = ? AND customer_id = ?
        ''', (retailer_id, customer_id))
 
        if cursor.fetchone():
            # Update existing discount
            cursor.execute('''
                UPDATE Discounts SET discount = ?
                WHERE retailer_id = ? AND customer_id = ?
            ''', (discount, retailer_id, customer_id))
        else:
            # Insert new discount
            cursor.execute('''
                INSERT INTO Discounts (retailer_id, customer_id, discount)
                VALUES (?, ?, ?)
            ''', (retailer_id, customer_id, discount))
 
        conn.commit()
 
    # Fetch average total sales across customers
    cursor.execute('''
        SELECT AVG(total) FROM (
            SELECT SUM(od.quantity * i.MRP) AS total
            FROM OrderDetails od
            JOIN Inventory i ON od.product_id = i.product_id
            WHERE i.retailer_id = ?
            GROUP BY od.customer_id
        ) AS subquery
    ''', (retailer_id,))
    average_sales = cursor.fetchone()[0] or 0

    print(average_sales)
 
    # Get loyal customers with their total sales
    cursor.execute('''
        SELECT od.customer_id, c.full_name, c.email, c.mobile_number, SUM(od.quantity * i.MRP) AS total_sales
        FROM OrderDetails od
        JOIN Inventory i ON od.product_id = i.product_id
        JOIN Customer c ON od.customer_id = c.customer_id
        WHERE i.retailer_id = ?
        GROUP BY od.customer_id, c.full_name, c.email, c.mobile_number
        HAVING SUM(od.quantity * i.MRP) > (SELECT AVG(total) FROM (
            SELECT SUM(od.quantity * i.MRP) AS total
            FROM OrderDetails od
            JOIN Inventory i ON od.product_id = i.product_id
            WHERE i.retailer_id = ?
            GROUP BY od.customer_id
        ) AS subquery)
    ''', (retailer_id, retailer_id))

    loyal_customers = cursor.fetchall()

    # Get current discounts
    cursor.execute('''
        SELECT customer_id, discount FROM Discounts WHERE retailer_id = ?
    ''', (retailer_id,))
    discounts_dict = {row.customer_id: row.discount for row in cursor.fetchall()}
 
    cursor.close()
    conn.close()
 
    return render_template(
        'retailer/customer_management.html',
        loyal_customers=loyal_customers,
        discounts=discounts_dict
    )

# @app.route('/retailer/dashboard')
# def dashboard():
#     if 'user' not in session or session.get('user_type').lower() != 'retailer':
#         return redirect(url_for('login'))
#     return render_template('retailer/dashboard.html')

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
        WHERE stock_qty < 110 and i.retailer_id= ?;
    '''
    cursor.execute(fetch_query,session['user_id'])

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


@app.route('/retailer/dashboard')
def dashboard():
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))
   
    conn=get_db_connection()
 
    query = """
        SELECT
            pc.category_name,
            p.product_name,
            ps.subcategory_name,
            SUM(od.quantity) AS total_quantity,
            SUM(od.quantity * od.unit_price) AS total_sales
        FROM OrderDetails od
        JOIN Products p ON od.product_id = p.product_id
        JOIN ProductCategory pc ON p.category_id = pc.category_id
        JOIN ProductSubcategory ps ON p.subcategory_id = ps.subcategory_id
        WHERE retailer_id = ?
        GROUP BY pc.category_name,p.product_name, ps.subcategory_name
    """
 
    df = pd.read_sql(query, conn, params=(session['user_id']))
 
    query1=''' SELECT c.city, SUM(od.quantity * od.unit_price) AS total_sales, month(od.order_date) as month
        FROM OrderDetails od
        JOIN Customer c ON od.customer_id = c.customer_id
        WHERE retailer_id = ?
        GROUP BY c.city, month(od.order_date)'''
   
    df1 = pd.read_sql(query1, conn, params=(session['user_id']))
    # Plot 1: Quantity per category
    fig1 = px.bar(df, x='category_name', y='total_quantity', title='Total Quantity Sold per Category')
    fig1.update_layout(xaxis_title='Category', yaxis_title='Quantity')
    chart1 = fig1.to_html(full_html=False)
 
    # Plot 2: Sales per category
    fig2 = px.bar(df, x='category_name', y='total_sales', title='Total Sales per Category', color='category_name')
    fig2.update_layout(xaxis_title='Category', yaxis_title='Sales')
    chart2 = fig2.to_html(full_html=False)
 
    # Plot 3 : pie chart sales by product
 
    fig3 = px.pie(df,values='total_quantity',names='product_name',title='Total Quantity Ordered by Product Name', hover_data=['total_sales'],labels={'total_sales': 'Total Sales '})
    fig3.update_traces(textposition='inside',textinfo='percent+label')
    chart3=fig3.to_html(full_html=False)
 
    # Plot 4: Quantity per subcategory
    fig4 = px.pie(df,values='total_quantity',names='subcategory_name',title='Total Quantity by Product subcategory', hover_data=['total_sales'],labels={'total_sales': 'Total Sales '})
    fig4.update_traces(textposition='inside',textinfo='percent+label')
    chart4=fig4.to_html(full_html=False)
 
     # Plot 4: amount per subcategory
    fig5 = px.bar(df, x='subcategory_name', y='total_sales', title='Total Sales per SubCategory', color='subcategory_name')
    fig5.update_layout(xaxis_title='SubCategory', yaxis_title='Sales')
    chart5 = fig5.to_html(full_html=False)
 
    # Plot 6: amount per region
    fig6 = px.bar(df1, x="total_sales", y="city", color='city', orientation='h',
             # hover_data=["tip", "size"],
             height=400,
             title='Regional Sales Distribution')
    fig6.update_layout(xaxis_title='Sales', yaxis_title='City')
    chart6 = fig6.to_html(full_html=False)
 
    # Plot 6: amount per month
    fig7 = px.line(df1, x='city', y='total_sales', title='Sales per City')
    fig7.update_layout(xaxis_title='City', yaxis_title='Sales')
    chart7 = fig7.to_html(full_html=False)
 
    return render_template('/retailer/dashboard.html', chart1=chart1, chart2=chart2, chart3=chart3, chart4=chart4, chart5=chart5, chart6=chart6, chart7=chart7)

@app.route('/retailer/return_inventory')
def retailer_return_inventory():
    if 'user' not in session or session.get('user_type').lower() != 'retailer':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    query='''
        SELECT o.order_id, p.product_name, c.full_name, 
               f.request, f.feedback_description,f.r_quantity
        FROM OrderDetails o
        JOIN Customer c ON o.customer_id = c.customer_id
        JOIN Feedback f ON o.order_id = f.order_id
        join products p on o.product_id= p.product_id
        WHERE f.request IN ('Return', 'Replace') and f.retailer_id= ?
    '''
    
    cursor.execute(query,session['user_id'])

    orders = [
        {
            'order_id': row[0],
            'product_name' : row[1],
            'full_name' :row[2],
            'request': row[3],
            'feedback_description' :row[4],
            'r_quantity' :  row[5]
        }
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()

    return render_template('/retailer/return_inventory.html', orders=orders)

@app.route('/update_return_inventory', methods=['POST'])
def update_return_inventory():
    order_id = request.form['order_id']
    status = request.form['status']

    conn = get_db_connection()
    cur = conn.cursor()

    # ✅ Get feedback row instead of order
    cur.execute("SELECT * FROM Feedback WHERE order_id = ?", (order_id,))
    row = cur.fetchone()

    if row:
        # Convert to dictionary if needed
        columns = [col[0] for col in cur.description]
        feedback = dict(zip(columns, row))

        product_id = feedback['product_id']
        retailer_id = feedback['retailer_id']
        request_type = feedback['request']

        # ✅ Update the feedback request
        cur.execute("UPDATE Feedback SET request = ? WHERE order_id = ?", (status, order_id))

        # ✅ If accepted and it's a return, update inventory
        if status == 'Accepted' and request_type == 'Return':
            cur.execute("SELECT r_quantity FROM feedback WHERE product_id = ? AND retailer_id = ?", (product_id, retailer_id))
            product_row = cur.fetchone()

            if product_row:
                new_quantity = product_row[0] + 1
                cur.execute("UPDATE Inventory SET stock_qty = stock_qty + ?  WHERE product_id = ? AND retailer_id = ?", (new_quantity, product_id, retailer_id))

        conn.commit()
        flash("Order status updated successfully.", "success")
    else:
        flash("Feedback not found for this order.", "danger")

    conn.close()
    return redirect(url_for('retailer_return_inventory'))


if __name__ == "__main__":
    app.run(debug=True)

