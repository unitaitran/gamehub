import mysql.connector
from mysql.connector import Error
from .auth import get_db_connection

def authenticate_user(email, password):
    try:
        connection = get_db_connection()
        if connection is None:
            return {"success": False, "error": "Cannot connect to database!"}
        
        cursor = connection.cursor(dictionary=True)
        # Query to check email, password and isDeleted status
        query = "SELECT username, email, role_id FROM users WHERE email = %s AND password = %s AND isDeleted = 0"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            # Determine role based on role_id
            role = "admin" if user["role_id"] == 1 else "user"
            return {
                "success": True,
                "username": user["username"],
                "email": user["email"],
                "role": role
            }
        else:
            return {"success": False, "error": "Email hoặc mật khẩu không đúng!"}

    except Error as e:
        return {"success": False, "error": f"Lỗi kết nối cơ sở dữ liệu: {e}"}