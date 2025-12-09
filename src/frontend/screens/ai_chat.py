import flet as ft
import requests
import time
from typing import List, Dict
from .home import build_menu_row
import pandas as pd
import warnings

# Suppress sklearn warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

from ...backend.auth import get_all_users


class AIChatScreen:
    def __init__(self, page: ft.Page, state: Dict, render_func):
        self.page = page
        self.state = state
        self.render = render_func
        self.chat_history: List[Dict] = []
        self.api_url = "http://localhost:8000/chat"  # URL của Gemini AI server
        
    def build(self):
        # Get users from MySQL
        users_data = get_all_users()
        if not users_data:
            print("Cannot get users from MySQL")
            users_data = []

        # Callback functions
        def set_home(e=None):
            self.state["screen"] = "home"
            self.render()
            
        def set_privacy(e=None):
            self.state["screen"] = "privacy_policy"
            self.render()
            
        def set_terms(e=None):
            self.state["screen"] = "terms_of_use"
            self.render()
            
        def set_about_us(e=None):
            self.state["screen"] = "about_us"
            self.render()
            
        def set_contact_us(e=None):
            self.state["screen"] = "contact_us"
            self.render()
            
        def handle_menu(action):
            if action == "logout":
                self.state.clear()
                self.state.update({
                    "screen": "login",
                    "login_error": "",
                    "login_email": "",
                    "login_password": ""
                })
                self.render()
            elif action == "account":
                self.state["screen"] = "account"
                self.render()
            elif action == "payment":
                self.state["screen"] = "payment"
                self.render()
            elif action == "cart":
                self.state["screen"] = "cart"
                self.render()
            elif action == "history":
                self.state["screen"] = "history"
                self.render()
            elif action == "allgame":
                self.state["screen"] = "allgame"
                self.render()
            elif action == "ai_chat":
                self.state["screen"] = "ai_chat"
                self.render()

        # Search functionality - similar to home.py
        def on_search_change(e):
            keyword = e.control.value
            if not keyword:
                search_results_container.content.controls.clear()
                search_results_container.visible = False
                self.page.update()
                return

            try:
                response = requests.get(
                    f"http://127.0.0.1:5000/api/search?q={keyword}")
                data = response.json()

                search_results_container.content.controls.clear()
                if not data["games"]:
                    search_results_container.content.controls.append(
                        ft.Container(
                            ft.Text("No results found", color=ft.Colors.GREY, size=14),
                            padding=ft.padding.all(10)
                        )
                    )
                    search_results_container.visible = True
                else:
                    for i, game in enumerate(data["games"]):
                        # Tạo game item giống như trong hình ảnh
                        price_text = "Free" if float(game.get("price", 0)) == 0 else f"{float(game.get('price', 0)):,.2f}"
                        price_color = "#22c55e" if float(game.get("price", 0)) == 0 else "#ffffff"
                        
                        def open_search_game_detail(e, game_data=game):
                            self.state["selected_game"] = {"id": game_data["id"]}
                            self.state["screen"] = "game_detail"
                            # Ẩn search results
                            search_results_container.content.controls.clear()
                            search_results_container.visible = False
                            self.render()
                        
                        game_item = ft.Container(
                            content=ft.Row(
                                [
                                    ft.Image(
                                        src=game["image_url_vertical"], 
                                        width=60, 
                                        height=80,
                                        fit=ft.ImageFit.COVER,
                                        border_radius=5
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                game["title"], 
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.WHITE,
                                                max_lines=2,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                                width=350
                                            ),
                                            ft.Text(
                                                price_text,
                                                size=12,
                                                color=price_color,
                                                weight=ft.FontWeight.BOLD
                                            )
                                        ],
                                        spacing=4,
                                        alignment=ft.MainAxisAlignment.START,
                                        expand=True
                                    )
                                ],
                                spacing=12,
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=ft.padding.all(8),
                            bgcolor="#2a3441" if i == 3 else "transparent",
                            border_radius=5,
                            on_hover=lambda e, idx=i: on_search_item_hover(e, idx),
                            on_click=lambda e, game_data=game: open_search_game_detail(e, game_data),
                            key=f"search_item_{i}",
                            width=480
                        )
                        search_results_container.content.controls.append(game_item)
                search_results_container.visible = True
                self.page.update()
            except Exception as ex:
                print("Search error:", ex)
                # Show dropdown even when API fails for UI testing
                search_results_container.content.controls.clear()
                search_results_container.content.controls.append(
                    ft.Container(
                        ft.Text("Server not available", color=ft.Colors.GREY, size=14),
                        padding=ft.padding.all(10)
                    )
                )
                search_results_container.visible = True
                self.page.update()

        def on_search_item_hover(e, idx):
            # Xử lý hover effect cho search items
            if e.data == "true":
                # Hover in
                e.control.bgcolor = "#2a3441"
            else:
                # Hover out
                e.control.bgcolor = "transparent"
            self.page.update()

        def clear_search(e):
            # Clear search box và ẩn results
            search_results_container.content.controls.clear()
            search_results_container.visible = False
            self.page.update()

        # Create search components
        search_box = ft.TextField(
            hint_text="Search for Games",
            width=220,
            height=38,
            content_padding=ft.padding.only(left=15, top=0, bottom=0, right=15),
            bgcolor="#232b39",
            color=ft.Colors.WHITE,
            border_radius=20,
            border_color="#232b39",
            cursor_color="#020302",
            hint_style=ft.TextStyle(color="#b0b0b0"),
            on_change=on_search_change
        )

        search_results_column = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=8)

        search_results_container = ft.Container(
            content=search_results_column,
            padding=ft.padding.all(10),
            margin=ft.margin.only(top=00, left=1320),  # Điều chỉnh position để căn với search box
            width=500,  # Giảm width để phù hợp
            height=500,  # Giảm height để phù hợp
            bgcolor="#232b39",  # Màu tối hơn giống header
            border_radius=10,
            border=ft.border.all(1, "#404040"),  # Thêm border
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color="#00000040",
                offset=ft.Offset(0, 5)
            ),
            visible=False
        )

        # Header with menu and search
        header = build_menu_row(
            self.state, 
            self.render, 
            set_home, 
            handle_menu, 
            on_search_change, 
            search_results_container, 
            set_about_us, 
            set_contact_us,
            clear_search
        )

        # Chat container - fixed and expanded
        self.chat_container = ft.Container(
            content=ft.Column(
                controls=[],
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
                alignment=ft.MainAxisAlignment.START,  # Start from top
            ),
            expand=True,  # Use available space
            padding=ft.padding.all(25),
            border=ft.border.all(2, "#2ecc71"),
            border_radius=15,
            bgcolor="#1c2526",
            margin=ft.margin.only(left=40, right=40, top=20, bottom=20),
            width=self.page.width - 80,  # Fixed width based on page
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.4, "#2ecc71"),
                offset=ft.Offset(0, 8),
            ),
        )

        # Sample questions
        def on_select_question(e, question):
            self.prompt_input.current.value = question
            self.prompt_input.current.update()
            self.send_message()

        self.sample_questions = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Quick questions:",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#2ecc71",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "🎮 Action games",
                            on_click=lambda e: on_select_question(e, "Recommend some action games"),
                            style=ft.ButtonStyle(
                                color="#2ecc71",
                                bgcolor="#34495e",
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            ),
                            tooltip="Get action game recommendations",
                        ),
                        ft.TextButton(
                            "🧩 Puzzle games",
                            on_click=lambda e: on_select_question(e, "Recommend some puzzle games"),
                            style=ft.ButtonStyle(
                                color="#2ecc71",
                                bgcolor="#34495e",
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            ),
                            tooltip="Get puzzle game recommendations",
                        ),
                        ft.TextButton(
                            "⭐ Top rated",
                            on_click=lambda e: on_select_question(e, "List top rated games"),
                            style=ft.ButtonStyle(
                                color="#2ecc71",
                                bgcolor="#34495e",
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            ),
                            tooltip="Get top rated game suggestions",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                    wrap=True,
                    run_spacing=10,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.only(top=20, bottom=20),
            width=self.page.width - 80,  # Match chat container width
        )

        # Welcome message when chat is empty
        if not self.chat_history:
            welcome_container = ft.Container(
                content=ft.Column([
                    ft.Icon(
                        ft.Icons.CHAT_BUBBLE_OUTLINE,
                        size=48,
                        color="#2ecc71",
                    ),
                    ft.Text(
                        "Welcome to GameHub AI Assistant!",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#2ecc71",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "I can help you find games, answer questions about GameHub, and provide recommendations. What would you like to know?",
                        size=16,
                        color="#95a5a6",
                        text_align=ft.TextAlign.CENTER,
                        width=400,
                    ),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=50, bottom=50),
            )
            self.chat_container.content.controls.append(welcome_container)
            # Add sample questions after welcome message
            self.chat_container.content.controls.append(self.sample_questions)

        # Input area
        self.prompt_input = ft.Ref[ft.TextField]()
        input_row = ft.Row(
            controls=[
                ft.TextField(
                    ref=self.prompt_input,
                    hint_text="Type your message here...",
                    hint_style=ft.TextStyle(color="#7f8c8d"),
                    text_style=ft.TextStyle(color="#ffffff"),
                    border_color="#2ecc71",
                    focused_border_color="#27ae60",
                    bgcolor="#2c3e50",
                    border_radius=10,
                    expand=True,
                    multiline=True,
                    min_lines=1,
                    max_lines=4,
                    on_submit=self.send_message,
                ),
                ft.IconButton(
                    icon=ft.Icons.SEND,
                    icon_color="#ffffff",
                    on_click=self.send_message,
                    bgcolor="#27ae60",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=15,
                    ),
                    tooltip="Send message",
                ),
            ],
            spacing=12,
            width=self.page.width - 80,  # Match chat container width
        )

        input_container = ft.Container(
            content=input_row,
            padding=ft.padding.all(20),
            bgcolor="#1c2526",
            border_radius=15,
            margin=ft.margin.only(left=40, right=40, bottom=30),
            border=ft.border.all(1, "#2ecc71"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.3, "#2ecc71"),
                offset=ft.Offset(0, 5),
            ),
        )

        # Loading indicator
        self.loading_indicator = ft.Container(
            content=ft.Row(
                controls=[
                    ft.ProgressRing(
                        color="#2ecc71",
                        width=24,
                        height=24,
                    ),
                    ft.Text(
                        "AI is thinking..." if time.time() % 2 < 1 else "Please wait...",
                        color="#2ecc71",
                        size=16,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
            ),
            visible=False,
            padding=ft.padding.all(20),
            bgcolor="#1c2526",
            border_radius=12,
            margin=ft.margin.only(left=40, right=40, bottom=15),
            border=ft.border.all(1, "#2ecc71"),
            width=self.page.width - 80,  # Match chat container width
        )

        # Main content - similar to home.py structure
        main_content = ft.Column(
            controls=[
                # Page title
                ft.Container(
                    content=ft.Text(
                        "AI Assistant",
                        size=36,
                        weight=ft.FontWeight.BOLD,
                        color="#2ecc71",
                        text_align=ft.TextAlign.CENTER,
                        font_family="Roboto",
                    ),
                    padding=ft.padding.only(top=30, bottom=30),
                    alignment=ft.alignment.center,
                ),
                # Chat section
                ft.Container(
                    content=ft.Column([
                        self.chat_container,
                        self.loading_indicator,
                        input_container,
                    ]),
                    padding=ft.padding.only(left=20, right=20),
                    expand=True,
                ),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Create Stack for proper layering like home.py
        main_stack = ft.Stack(
            controls=[
                main_content,
                search_results_container
            ],
            expand=True
        )

        # Add header and main stack to page like home.py
        self.page.add(
            header,
            main_stack
        )

        return ft.Container()  # Return empty container since we're adding to page directly

    def add_message(self, message: str, is_user: bool = True):
        """Add message to chat history"""
        message_data = {
            "text": message,
            "is_user": is_user,
            "timestamp": time.time()
        }
        self.chat_history.append(message_data)
        self.update_chat_display()

    def update_chat_display(self):
        """Update chat display"""
        self.chat_container.content.controls.clear()
        
        if not self.chat_history:
            # Show welcome message when no chat history
            welcome_container = ft.Container(
                content=ft.Column([
                    ft.Icon(
                        ft.Icons.CHAT_BUBBLE_OUTLINE,
                        size=48,
                        color="#2ecc71",
                    ),
                    ft.Text(
                        "Welcome to GameHub AI Assistant!",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#2ecc71",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "I can help you find games, answer questions about GameHub, and provide recommendations. What would you like to know?",
                        size=16,
                        color="#95a5a6",
                        text_align=ft.TextAlign.CENTER,
                        width=400,
                    ),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=50, bottom=50),
            )
            self.chat_container.content.controls.append(welcome_container)
        else:
            # Show chat messages
            for message in self.chat_history:
                message_container = self.create_message_bubble(message)
                self.chat_container.content.controls.append(message_container)
            
            # Add sample questions at the bottom when there are messages
            self.chat_container.content.controls.append(ft.Container(height=20))
            self.chat_container.content.controls.append(self.sample_questions)
        
        # Add spacing at bottom
        self.chat_container.content.controls.append(ft.Container(height=20))
        self.chat_container.update()

    def create_message_bubble(self, message_data: Dict):
        """Create message bubble"""
        is_user = message_data["is_user"]
        
        bubble = ft.Container(
            content=ft.Text(
                message_data["text"],
                color="#ffffff" if is_user else "#ecf0f1",
                size=15,
                selectable=True,
                font_family="Roboto",
            ),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor="#27ae60" if is_user else "#34495e",
            border_radius=12,
            margin=ft.margin.only(
                left=60 if is_user else 10,
                right=10 if is_user else 60,
                top=5,
                bottom=5,
            ),
            shadow=ft.BoxShadow(
                spread_radius=0.5,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.2, "#000000"),
                offset=ft.Offset(0, 2),
            ),
        )
        
        return bubble

    def send_message(self, e=None):
        """Send message to AI"""
        prompt = self.prompt_input.current.value.strip()
        if not prompt:
            return

        # Add user message
        self.add_message(prompt, is_user=True)
        self.prompt_input.current.value = ""
        self.prompt_input.current.update()

        # Show loading
        self.loading_indicator.visible = True
        self.loading_indicator.update()

        try:
            # Call Gemini API
            response = self.call_gemini_api(prompt)
            
            # Hide loading
            self.loading_indicator.visible = False
            self.loading_indicator.update()

            if response and "response" in response:
                # Add AI response
                self.add_message(response["response"], is_user=False)
            else:
                error_msg = "Sorry, an error occurred while processing your request."
                if response and "error" in response:
                    error_msg = f"Error: {response['error']}"
                self.add_message(error_msg, is_user=False)

        except Exception as e:
            # Hide loading
            self.loading_indicator.visible = False
            self.loading_indicator.update()
            
            error_msg = f"Connection error: {str(e)}"
            self.add_message(error_msg, is_user=False)

    def call_gemini_api(self, prompt: str):
        """Call Gemini API"""
        try:
            payload = {"prompt": prompt}
            
            # Use requests directly
            response = requests.post(self.api_url, json=payload, timeout=150)  # Increased timeout to 2.5 minutes
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.Timeout:
            return {"error": "Timeout - Server did not respond within 2.5 minutes"}
        except requests.exceptions.ConnectionError:
            return {"error": "Unable to connect to server"}
        except Exception as e:
            return {"error": f"Unknown error: {str(e)}"}

def ai_chat_screen(page: ft.Page, state: Dict, render_func):
    """Factory function to create AI Chat screen"""
    screen = AIChatScreen(page, state, render_func)
    return screen.build()