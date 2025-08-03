from database.db_connection import connect

class UserModel:
    @staticmethod
    def login(username, password):
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        conn.close()
        return user
