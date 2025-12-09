import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
import random
import string
from .auth import get_db_connection

def send_otp_email(email, otp):
    sender_email = "daiwin7a@gmail.com"
    sender_password = "clag drtm scea hcgu"
    receiver_email = email
    subject = "Your OTP for Password Reset"
    body = f"Your OTP for password reset is: {otp}. This code is valid for 10 minutes."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return {"success": True}
    except Exception as e:
        print(f"Failed to send email: {e}")
        return {"success": False, "errors": {"database": f"Failed to send email: {e}"}}

def check_email_exists(email):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        query = "SELECT email FROM users WHERE email = %s AND isDeleted = 0"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result is not None
    return False

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def update_password(email, new_password):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        query = "UPDATE users SET password = %s WHERE email = %s"
        cursor.execute(query, (new_password, email))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    return False

def handle_forgot_password(email, otp, new_password, confirm_password, stored_otp):
    errors = {"email": "", "otp": "", "new_password": "", "confirm_password": "", "database": ""}
    
    if not check_email_exists(email):
        errors["email"] = "Email does not exist."
        return {"success": False, "errors": errors}
    
    if otp != stored_otp:
        errors["otp"] = "Invalid OTP."
        return {"success": False, "errors": errors}
    
    if new_password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."
        return {"success": False, "errors": errors}
    
    # Check if new password is different from old password
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        query = "SELECT password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        old_password = cursor.fetchone()
        cursor.close()
        connection.close()
        if old_password and new_password == old_password[0]:
            errors["new_password"] = "New password cannot be the same as the old password."
            return {"success": False, "errors": errors}
    
    if not update_password(email, new_password):
        errors["database"] = "Failed to update password."
        return {"success": False, "errors": errors}
    
    return {"success": True, "errors": errors}