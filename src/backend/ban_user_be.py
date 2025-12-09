import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
from .auth import get_db_connection

def send_ban_notification_email(email, username, reason):
    """Send ban notification email to user"""
    sender_email = "daiwin7a@gmail.com"
    sender_password = "clag drtm scea hcgu"
    receiver_email = email
    subject = "Account Banned - GameHub"
    
    # English email content
    body = f"""Dear {username},

Your GameHub account has been banned by our administration team.

Reason for ban: {reason}

This action was taken in accordance with our Terms of Service and Community Guidelines. If you believe this was done in error, please contact our support team.

Best regards,
GameHub Administration Team"""

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Ban notification email sent successfully to {email}")
        return True
    except Exception as e:
        print(f"Failed to send ban notification email: {e}")
        return False

def ban_user(user_id, reason):
    """Ban user by setting isDeleted=1 and send email notification"""
    connection = get_db_connection()
    if not connection:
        print("Database connection failed")
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # First, get user information before banning
        query = "SELECT username, email FROM users WHERE id = %s AND isDeleted = 0"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"No active user found with ID: {user_id}")
            return False
        
        # Ban the user by setting isDeleted = 1
        ban_query = "UPDATE users SET isDeleted = 1 WHERE id = %s"
        cursor.execute(ban_query, (user_id,))
        
        if cursor.rowcount == 0:
            print(f"No user found with ID: {user_id}")
            connection.rollback()
            return False
        
        # Send ban notification email
        email_sent = send_ban_notification_email(user['email'], user['username'], reason)
        
        if email_sent:
            connection.commit()
            print(f"User {user['username']} banned successfully and email notification sent")
            return True
        else:
            # Even if email fails, still ban the user but log the issue
            connection.commit()
            print(f"User {user['username']} banned successfully but email notification failed")
            return True
            
    except Exception as e:
        print(f"Error banning user: {e}")
        if connection.is_connected():
            connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_by_id(user_id):
    """Get user information by ID"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            id,
            username,
            email,
            fullname,
            age,
            gender,
            coin,
            role_id,
            isDeleted,
            phone
        FROM users 
        WHERE id = %s
        """
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        return user
        
    except Error as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
