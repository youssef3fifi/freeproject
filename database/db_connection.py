# database/db_connection.py
import mysql.connector

def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",  # عدلها لو عندك باسورد
        database="sharp_db"
    )
create_connection = connect