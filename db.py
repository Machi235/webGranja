import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="granjaaa",
        autocommit=True,
        buffered=True 
    )
