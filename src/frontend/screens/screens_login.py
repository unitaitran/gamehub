import flet as ft
import os
from ...backend.login_be import authenticate_user
import os


def login_screen(page, state, render):
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
    def switch_to_register(e):
        state["screen"] = "register"
        render()
    def forgot(e):
        state["screen"] = "forgot"
        render()
    tab_buttons = ft.Container(
        bgcolor="#232b34",
        border_radius=12,
        padding=ft.padding.all(4),
        width=400,
        content=ft.Row([
            ft.Container(
                content=ft.Row([
                    ft.Text("Login", color="#ffffff", size=16, weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#22c55e",
                border_radius=8,
                padding=ft.padding.symmetric(vertical=12),
                alignment=ft.alignment.center,
                expand=True,
            ),
            ft.Container(
                content=ft.Row([
                    ft.Text("Register", color="#ffffff", size=16, weight=ft.FontWeight.W_500)
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#374151",
                border_radius=8,
                padding=ft.padding.symmetric(vertical=12),
                alignment=ft.alignment.center,
                expand=True,
                on_click=switch_to_register,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=0)
    )
    # Thông báo lỗi
    if "login_error" not in state:
        state["login_error"] = ""
    def on_email_change(e):
        state["login_email"] = e.control.value
        state["login_error"] = ""
    def on_password_change(e):
        state["login_password"] = e.control.value
        state["login_error"] = ""
    def sign_in(e):
        email = state.get("login_email", "")
        password = state.get("login_password", "")
        result = authenticate_user(email, password)
        
        if result["success"]:
            state["username"] = result["username"]
            state["login_error"] = ""
            
            # Kiểm tra role để chuyển hướng
            if result["role"] == "admin":
                state["screen"] = "admin"  # Admin chuyển đến admin interface
            else:
                state["screen"] = "home"   # User chuyển đến home
                
            render()
        else:
            state["login_error"] = "Incorrect email or password!"
            render()
    email = ft.TextField(
        label="Email",
        hint_text="Enter your email",
        border_radius=8,
        filled=True,
        fill_color="#2d323b",
        border_color="#38404a",
        label_style=ft.TextStyle(color="#d1d5db"),
        text_style=ft.TextStyle(color="#ffffff"),
        value=state.get("login_email", ""),
        on_change=on_email_change,
        on_submit=sign_in,
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
        label_style=ft.TextStyle(color="#d1d5db"),
        text_style=ft.TextStyle(color="#ffffff"),
        value=state.get("login_password", ""),
        on_change=on_password_change,
        on_submit=sign_in,
    )
    error_text = ft.Text(state["login_error"], color="red", size=13) if state["login_error"] else ft.Container(height=0)
    remember = ft.Checkbox(label="Remember me", label_style=ft.TextStyle(color="#ffffff"))
    forgot = ft.TextButton("Forgot password?", style=ft.ButtonStyle(color="#22c55e"), on_click=forgot)
    sign_in = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(name="login", color="#ffffff"),
            ft.Text("Sign In", size=18, weight=ft.FontWeight.BOLD, color="#ffffff"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor="#22c55e",
        color="#ffffff",
        height=52,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=sign_in,
    )
    content = ft.Column([
        logo,
        slogan,
        ft.Container(height=8),
        tab_buttons,
        ft.Container(height=20),
        email,
        password,
        error_text,
        ft.Row([
            remember,
            ft.Container(expand=1),
            forgot
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=20),
        sign_in,
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, width=400, expand=True)
    
    page.add(
        ft.Row([
            ft.Container(content, alignment=ft.alignment.center),
        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
    )
    page.update() 