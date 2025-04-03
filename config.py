import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session

# SQL Server connection
def get_db_connection():
    
    server = 'NICESS-LP264' 
    database = 'retail management DB'
    username = 'sa'  
    password = 'training@123'  

    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 13 for SQL Server};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
    )

    return conn

def get_products(search_query):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT product_id, product_name, description, unit_price, image_url
        FROM Products
        WHERE product_name LIKE ? OR description LIKE ?
    '''
    cursor.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
    products = [
        {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': row[3],
            'image_url': row[4]
        }
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()
    return products

