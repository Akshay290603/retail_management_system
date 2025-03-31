import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mssql+pyodbc://username:password@localhost/retail_db?driver=SQL+Server'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
