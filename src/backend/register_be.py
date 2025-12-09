import mysql.connector
from mysql.connector import Error
import re
from .auth import get_db_connection

def register_user(email, phone, age, gender, password, fullname):
    # Validate data
    errors = {"email": "", "phone": "", "age": "", "password": "", "fullname": "", "database": ""}
    
    # Check email format (accept various email providers)
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        errors["email"] = "Email must be valid (e.g., user@domain.com)"
    
    # Check phone number (10 digits)
    if not phone.isdigit() or len(phone) != 10:
        errors["phone"] = "Phone number must be 10 digits"
    
    # Check age (must be a number between 13 and 100)
    if not age.isdigit() or int(age) < 13 or int(age) > 100:
        errors["age"] = "Age must be a number between 13 and 100"
    
    # Check password (at least 6 characters)
    if len(password) < 6:
        errors["password"] = "Password must be at least 6 characters"
    
    # Check fullname (not empty)
    if not fullname or len(fullname.strip()) == 0:
        errors["fullname"] = "Full name is required"

    # Create username from email (remove domain part)
    username = email.split('@')[0]

    # If there are validation errors, return them
    if any(errors.values()):
        return {"success": False, "errors": errors}

    connection = get_db_connection()
    if isinstance(connection, dict):
        errors["database"] = connection["error"]
        return {"success": False, "errors": errors}

    try:
        cursor = connection.cursor(dictionary=True)

        # Check for duplicate username
        query = "SELECT * FROM users WHERE username = %s AND isDeleted = 0"
        cursor.execute(query, (username,))
        if cursor.fetchone():
            errors["email"] = "This email is already in use"
            cursor.close()
            connection.close()
            return {"success": False, "errors": errors}

        # Check for duplicate email (including banned accounts)
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            if existing_user['isDeleted'] == 1:
                errors["email"] = "Account has been banned. Cannot register with this email."
            else:
                errors["email"] = "This email is already in use"
            cursor.close()
            connection.close()
            return {"success": False, "errors": errors}

        # Check for duplicate phone number
        query = "SELECT * FROM users WHERE phone = %s AND isDeleted = 0"
        cursor.execute(query, (phone,))
        if cursor.fetchone():
            errors["phone"] = "This phone number is already in use"
            cursor.close()
            connection.close()
            return {"success": False, "errors": errors}

        # Insert new user
        query = """INSERT INTO users (username, password, email, fullname, age, gender, coin, role_id, isDeleted, phone)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (username, password, email, fullname.strip(), int(age), gender, 0.00, 2, 0, phone)
        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()
        return {"success": True, "username": username}

    except Error as e:
        errors["database"] = f"Database connection error: {e}"
        return {"success": False, "errors": errors}