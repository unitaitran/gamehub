import mysql.connector
from mysql.connector import Error
from .auth import get_db_connection

# --- Các hàm get_user_profile và update_user_profile giữ nguyên, không thay đổi ---

def get_user_profile(username):
    try:
        connection = get_db_connection()
        if connection is None: return {"success": False, "error": "Cannot connect to database."}
        cursor = connection.cursor(dictionary=True)
        query = "SELECT username, fullname, email, phone, age, gender, coin FROM users WHERE username = %s AND isDeleted = 0"
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()
        cursor.close()
        connection.close()
        return {"success": True, "data": user_data} if user_data else {"success": False, "error": "User not found."}
    except Error as e:
        return {"success": False, "error": f"Lỗi cơ sở dữ liệu: {e}"}

def update_user_profile(username, new_data):
    try:
        # Validation cho fullname - không được chứa số
        fullname = new_data.get("fullname")
        if fullname:
            if any(char.isdigit() for char in fullname):
                return {"success": False, "error": "Full name cannot contain numbers."}
            if len(fullname.strip()) < 2:
                return {"success": False, "error": "Full name must be at least 2 characters long."}
        
        # Validation cho username mới nếu có
        new_username = new_data.get("username")
        if new_username:
            if len(new_username.strip()) < 3:
                return {"success": False, "error": "Username must be at least 3 characters long."}
            if not new_username.replace("_", "").replace("-", "").isalnum():
                return {"success": False, "error": "Username can only contain letters, numbers, underscore and hyphen."}
            
            # Kiểm tra username mới có tồn tại chưa (trừ username hiện tại)
            connection = get_db_connection()
            if connection is None:
                return {"success": False, "error": "Cannot connect to database."}
            
            cursor = connection.cursor(dictionary=True)
            check_query = "SELECT username FROM users WHERE username = %s AND username != %s AND isDeleted = 0"
            cursor.execute(check_query, (new_username, username))
            existing_user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if existing_user:
                return {"success": False, "error": "Username already exists. Please choose another one."}
        
        age = new_data.get("age")
        if age and not str(age).isdigit():
            return {"success": False, "error": "Age must be a number."}
        
        phone = new_data.get("phone")
        if phone and (not phone.isdigit() or len(phone) != 10):
            return {"success": False, "error": "Phone number must have 10 digits."}
        
        connection = get_db_connection()
        if connection is None:
            return {"success": False, "error": "Cannot connect to database."}
        
        cursor = connection.cursor()
        
        # Nếu có username mới, cập nhật cả username
        if new_username:
            query = "UPDATE users SET username = %s, fullname = %s, phone = %s, age = %s, gender = %s WHERE username = %s"
            values = (new_username, fullname, new_data.get("phone"), int(age) if age else None, new_data.get("gender"), username)
        else:
            query = "UPDATE users SET fullname = %s, phone = %s, age = %s, gender = %s WHERE username = %s"
            values = (fullname, new_data.get("phone"), int(age) if age else None, new_data.get("gender"), username)
        
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        
        # Trả về username mới nếu có thay đổi
        result = {"success": True, "message": "Profile updated successfully!"}
        if new_username:
            result["new_username"] = new_username
            
        return result
        
    except Error as e:
        return {"success": False, "error": f"Lỗi cơ sở dữ liệu khi cập nhật: {e}"}
    except ValueError:
        return {"success": False, "error": "Dữ liệu không hợp lệ."}

def delete_user_account(username):
    """
    Đánh dấu tài khoản là đã bị xóa.
    """
    try:
        connection = get_db_connection()
        if connection is None:
            return {"success": False, "error": "Lỗi kết nối CSDL."}

        cursor = connection.cursor()
        query = "UPDATE users SET isDeleted = 1 WHERE username = %s"
        
        cursor.execute(query, (username,))
        
        affected_rows = cursor.rowcount
        
        if affected_rows > 0:
            connection.commit()
            success = True
            message = "Account deleted successfully."
            error = None
        else:
            connection.rollback()
            success = False
            message = None
            error = "Account not found or already deleted."

        cursor.close()
        connection.close()
        
        return {"success": success, "message": message, "error": error}

    except Error as e:
        return {"success": False, "error": f"Lỗi CSDL khi xóa: {e}"}

def change_password(username, current_password, new_password):
    """
    Thay đổi mật khẩu của người dùng.
    """
    try:
        connection = get_db_connection()
        if connection is None:
            return {"success": False, "error": "Cannot connect to database."}

        cursor = connection.cursor(dictionary=True)
        
        # Check current password
        query = "SELECT password FROM users WHERE username = %s AND isDeleted = 0"
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return {"success": False, "error": "User not found."}
        
        if user_data['password'] != current_password:
            return {"success": False, "error": "Current password is incorrect."}
        
        # Update new password
        update_query = "UPDATE users SET password = %s WHERE username = %s"
        cursor.execute(update_query, (new_password, username))
        
        if cursor.rowcount > 0:
            connection.commit()
            return {"success": True, "message": "Password changed successfully!"}
        else:
            return {"success": False, "error": "Cannot update password."}
            
    except Error as e:
        return {"success": False, "error": f"Lỗi cơ sở dữ liệu: {e}"}
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
