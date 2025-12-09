import flet as ft
from ...backend.forgot_be import check_email_exists, generate_otp, send_otp_email, handle_forgot_password
import os

def forgot_screen(page, state, render):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "..", "..", "data", "images", "Logo_game_rmb.png")
    logo_url = logo_path    
    logo = ft.Image(src=logo_url, width=180, height=180, fit=ft.ImageFit.CONTAIN)    
    logo = ft.Image(src=logo_url, width=120, height=120, fit=ft.ImageFit.CONTAIN)
    slogan = ft.Text(
        "Your ultimate gaming marketplace",
        size=14,
        color="#9ca3af",
        text_align=ft.TextAlign.CENTER
    )

    def back_to_login(e):
        state["screen"] = "login"
        render()

    # Store form values and errors
    if "forgot_form" not in state:
        state["forgot_form"] = {"email": "", "otp": "", "new_password": "", "confirm_password": ""}
    if "forgot_errors" not in state:
        state["forgot_errors"] = {"email": "", "otp": "", "new_password": "", "confirm_password": "", "database": ""}
    stored_otp = ft.Ref[str]()

    # Refs for error widgets
    email_error_ref = ft.Ref[ft.Container]()
    otp_error_ref = ft.Ref[ft.Container]()
    new_password_error_ref = ft.Ref[ft.Container]()
    confirm_password_error_ref = ft.Ref[ft.Container]()
    database_error_ref = ft.Ref[ft.Container]()

    def update_errors():
        email_error_ref.current.content = ft.Text(state["forgot_errors"]["email"], color="red", size=12) if state["forgot_errors"]["email"] else ft.Container(height=0)
        otp_error_ref.current.content = ft.Text(state["forgot_errors"]["otp"], color="red", size=12) if state["forgot_errors"]["otp"] else ft.Container(height=0)
        new_password_error_ref.current.content = ft.Text(state["forgot_errors"]["new_password"], color="red", size=12) if state["forgot_errors"]["new_password"] else ft.Container(height=0)
        confirm_password_error_ref.current.content = ft.Text(state["forgot_errors"]["confirm_password"], color="red", size=12) if state["forgot_errors"]["confirm_password"] else ft.Container(height=0)
        database_error_ref.current.content = ft.Text(state["forgot_errors"]["database"], color="red", size=12) if state["forgot_errors"]["database"] else ft.Container(height=0)
        page.update()

    def on_email_change(e):
        state["forgot_form"]["email"] = e.control.value
        state["forgot_errors"]["email"] = ""
        state["forgot_errors"]["database"] = ""
        update_errors()

    def on_otp_change(e):
        state["forgot_form"]["otp"] = e.control.value
        state["forgot_errors"]["otp"] = ""
        state["forgot_errors"]["database"] = ""
        update_errors()

    def on_new_password_change(e):
        state["forgot_form"]["new_password"] = e.control.value
        state["forgot_errors"]["new_password"] = ""
        state["forgot_errors"]["database"] = ""
        update_errors()

    def on_confirm_password_change(e):
        state["forgot_form"]["confirm_password"] = e.control.value
        state["forgot_errors"]["confirm_password"] = ""
        state["forgot_errors"]["database"] = ""
        update_errors()

    def send_code(e):
        email = email_field.value
        if check_email_exists(email):
            otp = generate_otp()
            stored_otp.current = otp
            result = send_otp_email(email, otp)
            if result["success"]:
                page.snack_bar = ft.SnackBar(ft.Text("OTP sent to your email!", color="white"), bgcolor="#22c55e")
            else:
                state["forgot_errors"]["database"] = result["errors"].get("database", "Failed to send OTP")
                page.snack_bar = ft.SnackBar(ft.Text("Failed to send OTP!", color="white"), bgcolor="red")
        else:
            state["forgot_errors"]["email"] = "Email does not exist."
            page.snack_bar = ft.SnackBar(ft.Text("Email does not exist!", color="white"), bgcolor="red")
        page.snack_bar.open = True
        update_errors()

    def complete(e):
        result = handle_forgot_password(
            email_field.value,
            otp_field.value,
            new_password_field.value,
            confirm_password_field.value,
            stored_otp.current
        )
        if result["success"]:
            state["forgot_form"] = {"email": "", "otp": "", "new_password": "", "confirm_password": ""}
            state["forgot_errors"] = {"email": "", "otp": "", "new_password": "", "confirm_password": "", "database": ""}
            stored_otp.current = None
            page.snack_bar = ft.SnackBar(ft.Text("Password updated successfully!", color="white"), bgcolor="#22c55e")
            page.snack_bar.open = True
            state["screen"] = "login"
            render()
        else:
            state["forgot_errors"] = result["errors"]
            page.snack_bar = ft.SnackBar(ft.Text("Password update failed! Please check your information.", color="white"), bgcolor="red")
            page.snack_bar.open = True
            update_errors()

    # Input fields
    email_label = ft.Text("Email", color="#ffffff", size=13, weight=ft.FontWeight.BOLD)
    email_field = ft.TextField(
        hint_text="Enter your email",
        border_radius=12,
        filled=True,
        fill_color="#232b34",
        border_color="#4b5563",
        text_style=ft.TextStyle(color="#ffffff", size=15),
        hint_style=ft.TextStyle(color="#9ca3af", size=15),
        height=52,
        value=state["forgot_form"]["email"],
        on_change=on_email_change,
    )
    email_error = ft.Container(
        ref=email_error_ref,
        content=ft.Text(state["forgot_errors"]["email"], color="red", size=12) if state["forgot_errors"]["email"] else ft.Container(height=0)
    )
    otp_label = ft.Text("Otp", color="#ffffff", size=13, weight=ft.FontWeight.BOLD)
    otp_field = ft.TextField(
        hint_text="Enter Otp",
        border_radius=12,
        filled=True,
        fill_color="#232b34",
        border_color="#4b5563",
        text_style=ft.TextStyle(color="#ffffff", size=15),
        hint_style=ft.TextStyle(color="#9ca3af", size=15),
        height=52,
        value=state["forgot_form"]["otp"],
        on_change=on_otp_change,
        suffix=ft.ElevatedButton(
            content=ft.Text("send code", size=12, color="#ffffff"),
            bgcolor="#22c55e",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=send_code
        )
    )
    otp_error = ft.Container(
        ref=otp_error_ref,
        content=ft.Text(state["forgot_errors"]["otp"], color="red", size=12) if state["forgot_errors"]["otp"] else ft.Container(height=0)
    )
    new_password_label = ft.Text("New password", color="#ffffff", size=13, weight=ft.FontWeight.BOLD)
    new_password_field = ft.TextField(
        hint_text="Enter your new password",
        password=True,
        can_reveal_password=True,
        border_radius=12,
        filled=True,
        fill_color="#232b34",
        border_color="#4b5563",
        text_style=ft.TextStyle(color="#ffffff", size=15),
        hint_style=ft.TextStyle(color="#9ca3af", size=15),
        height=52,
        value=state["forgot_form"]["new_password"],
        on_change=on_new_password_change,
    )
    new_password_error = ft.Container(
        ref=new_password_error_ref,
        content=ft.Text(state["forgot_errors"]["new_password"], color="red", size=12) if state["forgot_errors"]["new_password"] else ft.Container(height=0)
    )
    confirm_password_label = ft.Text("Confirm new password", color="#ffffff", size=13, weight=ft.FontWeight.BOLD)
    confirm_password_field = ft.TextField(
        hint_text="Confirm password",
        password=True,
        can_reveal_password=True,
        border_radius=12,
        filled=True,
        fill_color="#232b34",
        border_color="#4b5563",
        text_style=ft.TextStyle(color="#ffffff", size=15),
        hint_style=ft.TextStyle(color="#9ca3af", size=15),
        height=52,
        value=state["forgot_form"]["confirm_password"],
        on_change=on_confirm_password_change,
    )
    confirm_password_error = ft.Container(
        ref=confirm_password_error_ref,
        content=ft.Text(state["forgot_errors"]["confirm_password"], color="red", size=12) if state["forgot_errors"]["confirm_password"] else ft.Container(height=0)
    )
    database_error = ft.Container(
        ref=database_error_ref,
        content=ft.Text(state["forgot_errors"]["database"], color="red", size=12) if state["forgot_errors"]["database"] else ft.Container(height=0)
    )
    complete_btn = ft.ElevatedButton(
        content=ft.Text("Complete", size=16, weight=ft.FontWeight.BOLD, color="#ffffff"),
        bgcolor="#22c55e",
        color="#ffffff",
        height=44,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        width=400,
        on_click=complete,
    )
    back_link = ft.TextButton("Back to sign in", style=ft.ButtonStyle(color="#9ca3af"), on_click=back_to_login)

    # Layout
    logo_slogan = ft.Column([
        logo,
        slogan,
        ft.Container(height=16),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    form_fields = ft.Column([
        email_label,
        email_field,
        email_error,
        otp_label,
        otp_field,
        otp_error,
        new_password_label,
        new_password_field,
        new_password_error,
        confirm_password_label,
        confirm_password_field,
        confirm_password_error,
        database_error,
    ], horizontal_alignment=ft.CrossAxisAlignment.START)
    content = ft.Column([
        logo_slogan,
        form_fields,
        ft.Container(height=16),
        complete_btn,
        ft.Container(height=8),
        ft.Row([
            back_link
        ], alignment=ft.MainAxisAlignment.START, width=400),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, width=400, expand=True)

    # Clear page and add new content
    page.controls.clear()
    page.add(
        ft.Row([
            ft.Container(content, alignment=ft.alignment.center),
        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
    )
    page.update()