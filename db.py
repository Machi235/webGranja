import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="granjadatos",
        autocommit=True,
        buffered=True 
    )
