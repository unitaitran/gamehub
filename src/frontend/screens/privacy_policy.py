import flet as ft

def privacy_policy_screen(page, state, render, footer):
    def go_home(e):
        state["screen"] = "home"
        render()

    content = ft.Column([
        ft.Row([
            ft.IconButton(icon=ft.Icons.HOME, icon_color="white", on_click=go_home),
            ft.Container(expand=True)
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Container(
            ft.Text("Privacy Policy", size=32, color="white", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
            alignment=ft.alignment.center,
            margin=ft.margin.only(top=10, bottom=20),
            border=ft.Border(
                left=ft.BorderSide(2, "#22c55e"),
                top=ft.BorderSide(2, "#22c55e"),
                right=ft.BorderSide(2, "#22c55e"),
                bottom=ft.BorderSide(2, "#22c55e"),
            ),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=40, vertical=8)
        ),
        ft.Container(
            ft.Column([
                ft.Container(
                    ft.Text("1. Acceptance of Terms", size=18, color="white", weight=ft.FontWeight.BOLD),
                    border=ft.Border(left=ft.BorderSide(6, "#22c55e")),
                    padding=ft.padding.only(left=12, bottom=4),
                    margin=ft.margin.only(bottom=4)
                ),
                ft.Text(
                    "By downloading or using the Game, you confirm that you have read, understood, and agreed to these Terms. If you do not agree, please discontinue use immediately.",
                    size=15, color="white", weight=ft.FontWeight.BOLD
                ),
                ft.Container(height=16),
                ft.Container(
                    ft.Text("2. Account Registration", size=18, color="white", weight=ft.FontWeight.BOLD),
                    border=ft.Border(left=ft.BorderSide(6, "#22c55e")),
                    padding=ft.padding.only(left=12, bottom=4),
                    margin=ft.margin.only(bottom=4)
                ),
                ft.Column([
                    ft.Text("• You may be required to create an account to access certain features.", size=15, color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("• You agree to provide accurate and current information.", size=15, color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("• You are responsible for maintaining the confidentiality of your account and password.", size=15, color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("• We reserve the right to suspend or terminate accounts that violate these Terms, including cheating, fraud, or inappropriate behavior.", size=15, color="white", weight=ft.FontWeight.BOLD),
                ], spacing=2),
                ft.Container(height=16),
                ft.Container(
                    ft.Text("3. Intellectual Property", size=18, color="white", weight=ft.FontWeight.BOLD),
                    border=ft.Border(left=ft.BorderSide(6, "#22c55e")),
                    padding=ft.padding.only(left=12, bottom=4),
                    margin=ft.margin.only(bottom=4)
                ),
                ft.Column([
                    ft.Text("• All content in the Game, including graphics, sounds, code, and other assets, is the property of the Company or its licensors.", size=15, color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("• You may not copy, modify, distribute, sell, or exploit any part of the Game without written permission.", size=15, color="white", weight=ft.FontWeight.BOLD),
                ], spacing=2)
            ], alignment=ft.MainAxisAlignment.START),
            bgcolor="#232b39",
            border_radius=12,
            padding=ft.padding.all(24),
            margin=ft.margin.only(top=8)
        )
    ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    return ft.Container(
        content=ft.Column([
            content,
            ft.Container(expand=True),  # Spacer để đẩy footer xuống dưới
            footer
        ], expand=True, spacing=0),
        expand=True,
        height=page.height
    ) 