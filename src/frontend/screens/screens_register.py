import flet as ft
import re
import webbrowser
import os
from ...backend.register_be import register_user
import os

def register_screen(page, state, render):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "..", "..", "data", "images", "Logo_game_rmb.png")
    logo_url = logo_path      
    logo = ft.Image(src=logo_url, width=180, height=180, fit=ft.ImageFit.CONTAIN)
    slogan = ft.Text(
        "Your ultimate gaming marketplace",
        size=14,
        color="#9ca3af",
        text_align=ft.TextAlign.CENTER
    )
    def switch_to_login(e):
        state["screen"] = "login"
        render()

    # Store form values and errors
    if "form" not in state:
        state["form"] = {"email": "", "phone": "", "age": "", "gender": "Male", "password": "", "fullname": "", "accept": False}
    if "errors" not in state:
        state["errors"] = {"email": "", "phone": "", "age": "", "password": "", "fullname": "", "database": ""}

    def on_email_change(e):
        state["form"]["email"] = e.control.value
        state["errors"]["email"] = ""
        state["errors"]["database"] = ""
    def on_phone_change(e):
        state["form"]["phone"] = e.control.value
        state["errors"]["phone"] = ""
        state["errors"]["database"] = ""
    def on_age_change(e):
        state["form"]["age"] = e.control.value
        state["errors"]["age"] = ""
        state["errors"]["database"] = ""
    def on_gender_change(e):
        state["form"]["gender"] = e.control.value
        render()
    def on_password_change(e):
        state["form"]["password"] = e.control.value
        state["errors"]["password"] = ""
        state["errors"]["database"] = ""
    def on_fullname_change(e):
        state["form"]["fullname"] = e.control.value
        state["errors"]["fullname"] = ""
        state["errors"]["database"] = ""
    def on_accept_change(e):
        state["form"]["accept"] = e.control.value
        render()

    def validate_and_register(e):
        if not state["form"]["accept"]:
            page.snack_bar = ft.SnackBar(ft.Text("Please accept the terms and privacy policy!", color="white"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        result = register_user(
            state["form"]["email"],
            state["form"]["phone"],
            state["form"]["age"],
            state["form"]["gender"],
            state["form"]["password"],
            state["form"]["fullname"]
        )

        if result["success"]:
            state["screen"] = "login"
            state["login_username"] = result["username"]
            state["login_password"] = state["form"]["password"]
            page.snack_bar = ft.SnackBar(ft.Text("Registration successful!", color="white"), bgcolor="#22c55e")
            page.snack_bar.open = True
            render()
        else:
            state["errors"] = result["errors"]
            page.snack_bar = ft.SnackBar(ft.Text("Registration failed! Please check your information.", color="white"), bgcolor="red")
            page.snack_bar.open = True
            render()

    def open_terms(e):
        webbrowser.open("https://your-terms-link.com")
    
    tab_buttons = ft.Container(
        bgcolor="#232b34",
        border_radius=12,
        padding=ft.padding.all(4),
        width=400,
        content=ft.Row([
            ft.Container(
                content=ft.Row([
                    ft.Text("Login", color="#ffffff", size=16, weight=ft.FontWeight.W_500)
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#374151",
                border_radius=8,
                padding=ft.padding.symmetric(vertical=12),
                alignment=ft.alignment.center,
                expand=True,
                on_click=switch_to_login,
            ),
            ft.Container(
                content=ft.Row([
                    ft.Text("Register", color="#ffffff", size=16, weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#22c55e",
                border_radius=8,
                padding=ft.padding.symmetric(vertical=12),
                alignment=ft.alignment.center,
                expand=True,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=0)
    )
    email = ft.TextField(
        label="Email",
        hint_text="Enter your email",
        border_radius=8,
        filled=True,
        fill_color="#2d323b",
        border_color="#38404a",
        label_style=ft.TextStyle(color="#d1d5db", size=13),
        text_style=ft.TextStyle(color="#ffffff", size=15),
        height=48,
        value=state["form"]["email"],
        on_change=on_email_change,
    )
    email_error = ft.Text(state["errors"].get("email", ""), color="red", size=12) if state["errors"].get("email", "") else ft.Container(height=0)
    fullname = ft.TextField(
        label="Full Name",
        hint_text="Enter your full name",
        border_radius=8,
        filled=True,
        fill_color="#2d323b",
        border_color="#38404a",
        label_style=ft.TextStyle(color="#d1d5db", size=13),
        text_style=ft.TextStyle(color="#ffffff", size=15),
        height=48,
        value=state["form"]["fullname"],
        on_change=on_fullname_change,
    )
    fullname_error = ft.Text(state["errors"].get("fullname", ""), color="red", size=12) if state["errors"].get("fullname", "") else ft.Container(height=0)
    phone = ft.TextField(
        label="Phone Number",
        hint_text="Enter your phone number",
        border_radius=8,
        filled=True,
        fill_color="#2d323b",
        border_color="#38404a",
        label_style=ft.TextStyle(color="#d1d5db", size=13),
        text_style=ft.TextStyle(color="#ffffff", size=15),
        height=48,
        value=state["form"]["phone"],
        on_change=on_phone_change,
    )
    phone_error = ft.Text(state["errors"].get("phone", ""), color="red", size=12) if state["errors"].get("phone", "") else ft.Container(height=0)
    age = ft.TextField(
        label="Age",
        hint_text="18",
        border_radius=8,
        filled=True,
        fill_color="#2d323b",
        border_color="#38404a",
        width=120,
        label_style=ft.TextStyle(color="#d1d5db", size=13),
        text_style=ft.TextStyle(color="#ffffff", size=15),
        height=48,
        value=state["form"]["age"],
        on_change=on_age_change,
    )
    age_error = ft.Text(state["errors"].get("age", ""), color="red", size=12) if state["errors"].get("age", "") else ft.Container(height=0)
    gender = ft.Dropdown(
        label="Gender",
        options=[
            ft.dropdown.Option("Male", text="Male"),
            ft.dropdown.Option("Female", text="Female"),
            ft.dropdown.Option("Other", text="Other"),
        ],
        value=state["form"]["gender"],
        border_radius=8,
        filled=True,
        fill_color="#2d323b",
        border_color="#38404a",
        width=120,
        label_style=ft.TextStyle(color="#d1d5db", size=13),
        text_style=ft.TextStyle(color="#ffffff", size=15),
        on_change=on_gender_change,
    )
    password = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        border_radius=8,
        filled=True,
        fill_color="#2d323b",
        border_color="#38404a",
        label_style=ft.TextStyle(color="#d1d5db", size=13),
        text_style=ft.TextStyle(color="#ffffff", size=15),
        height=48,
        value=state["form"]["password"],
        on_change=on_password_change,
    )
    password_error = ft.Text(state["errors"].get("password", ""), color="red", size=12) if state["errors"].get("password", "") else ft.Container(height=0)
    database_error = ft.Text(state["errors"].get("database", ""), color="red", size=12) if state["errors"].get("database", "") else ft.Container(height=0)
    accept_terms = ft.Checkbox(
        value=state["form"]["accept"],
        on_change=on_accept_change,
        label=ft.Row([
            ft.Text("Accept the ", color="#ffffff", size=13),
            ft.TextButton(
                "Terms & Conditions and Privacy Policy",
                style=ft.ButtonStyle(
                    color="#22c55e",
                    padding=ft.padding.only(left=0, right=0),
                    text_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)
                ),
                on_click=open_terms
            )
        ]),
        label_position=ft.LabelPosition.RIGHT
    )
    register_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(name="login", color="#ffffff"),
            ft.Text("Register", size=18, weight=ft.FontWeight.BOLD, color="#ffffff"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor="#22c55e",
        color="#ffffff",
        height=52,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=validate_and_register,
    )
    content = ft.Column([
        logo,
        slogan,
        ft.Container(height=12),
        tab_buttons,
        ft.Container(height=16),
        email,
        email_error,
        fullname,
        fullname_error,
        phone,
        phone_error,
        ft.Row([
            age,
            gender
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        age_error,
        password,
        password_error,
        database_error,
        accept_terms,
        ft.Container(height=12),
        register_btn,
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, width=400, expand=True)
    page.add(
        ft.Row([
            ft.Container(content, alignment=ft.alignment.center),
        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
    )