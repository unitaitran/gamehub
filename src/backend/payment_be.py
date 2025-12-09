import mysql.connector
from mysql.connector import Error
from .auth import get_db_connection

def get_user_balance(username):
    """
    Retrieve the current balance (coin) of a user from the database in USD.
    """
    try:
        connection = get_db_connection()
        if connection is None:
            return {"success": False, "message": "Database connection failed"}
        
        cursor = connection.cursor(dictionary=True)
        query = "SELECT coin FROM users WHERE username = %s AND isDeleted = 0"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            return {"success": True, "balance": result["coin"] or 0.0}
        else:
            return {"success": False, "message": "User not found"}
            
    except Error as e:
        return {"success": False, "message": f"Error retrieving balance: {e}"}

def update_user_balance(username, amount_usd):
    """
    Update user balance by adding the exact USD amount displayed in the frontend to the existing balance.
    """
    try:
        connection = get_db_connection()
        if connection is None:
            return {"success": False, "message": "Database connection failed"}
        
        cursor = connection.cursor()
        # Update the user's coin balance with the exact amount
        query = """
        UPDATE users 
        SET coin = COALESCE(coin, 0) + %s 
        WHERE username = %s AND isDeleted = 0
        """
        cursor.execute(query, (amount_usd, username))
        connection.commit()
        
        # Get the updated balance
        cursor.execute("SELECT coin FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            return {"success": True, "new_balance": result[0] or 0.0}
        else:
            return {"success": False, "message": "User not found"}
            
    except Error as e:
        if connection:
            connection.rollback()
        return {"success": False, "message": f"Error updating balance: {e}"}