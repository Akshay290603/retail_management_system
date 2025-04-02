import pyodbc

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


