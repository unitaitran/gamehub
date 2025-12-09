import flet as ft
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.history_be import get_history
from backend.auth import get_user_by_username

def purchase_history_screen(page, state, render, footer):
    username = state.get("username", "")
    if not username:
        # Nếu chưa đăng nhập, chuyển về login
        state["screen"] = "login"
        render()
        return
    # Lấy user_id từ username
    try:
        user_data = get_user_by_username(username)
        user_id = user_data[0]['id'] if user_data else 1
    except Exception as e:
        print(f"Error getting user_id from username: {e}")
        user_id = 1
    # Lấy lịch sử mua game
    history_games = get_history(user_id)
    if "download_timer" not in state:
        state["download_timer"] = {}

    async def countdown(game_id):
        while state["download_timer"][game_id] > 0:
            await asyncio.sleep(1)
            state["download_timer"][game_id] -= 1
            render()
        state["download_timer"][game_id] = 0
        render()

    def start_download(game_id):
        if state["download_timer"].get(game_id) is None or state["download_timer"][game_id] == 0:
            state["download_timer"][game_id] = 30
            page.run_task(countdown, game_id)
            render()

    def game_item(game):
        download_btn = ft.ElevatedButton(
            "Download",
            url="https://www.facebook.com/",
            bgcolor="#22c55e",
            color="white",
            height=40,
            width=None,
            expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)),
        )
        return ft.Container(
            ft.Column([
                ft.Row([
                    ft.Image(src=game.get("game_image", "https://via.placeholder.com/90x90"), width=80, height=80, fit=ft.ImageFit.COVER, border_radius=8),
                    ft.Container(
                        ft.Column([
                            ft.Text(game.get("game_title", "Unknown Game"), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(game.get("game_description", "Game description not available"), size=13, color="#b0b0b0", max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f"${game.get('game_price', 0):.2f}", size=15, color="#22c55e", weight=ft.FontWeight.BOLD),
                        ], spacing=4),
                        expand=True,
                        padding=ft.padding.only(left=16)
                    )
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=8),
                ft.Row([
                    download_btn
                ], expand=True)
            ], spacing=8),
            bgcolor="#232b39",
            border_radius=12,
            padding=ft.padding.all(16),
            margin=ft.margin.only(bottom=16)
        )

    if not history_games:
        history_items = [ft.Text("No purchase history yet.", color="#b0b0b0", size=18, text_align=ft.TextAlign.CENTER)]
    else:
        history_items = [game_item(game) for game in history_games]

    # Tạo ListView để scroll mượt mà hơn
    history_list = ft.ListView(
        controls=history_items,
        spacing=16,
        padding=ft.padding.all(16),
        expand=True,
        auto_scroll=False
    )
    
    # Tạo scrollable content với footer ở cuối
    scrollable_content = ft.Column([
        ft.Text("Purchase History", size=28, weight=ft.FontWeight.BOLD, color="#b0b0b0", text_align=ft.TextAlign.CENTER),
        ft.Container(height=8),
        history_list,
        ft.Container(expand=True),  # Spacer để đẩy footer xuống cuối
        ft.Container(height=20),  # Khoảng cách trước footer
        footer  # Footer ở cuối content
    ], spacing=8, expand=True, alignment=ft.MainAxisAlignment.START)
    
    # Tạo container scrollable chính
    main_container = ft.Container(
        content=scrollable_content,
        expand=True,
        padding=ft.padding.all(16)
    )
    
    # Sử dụng Column với scroll behavior
    return ft.Column([
        main_container
    ], expand=True, scroll=ft.ScrollMode.AUTO) 