import flet as ft
from ...backend.admin_interface_be import get_all_games_from_db, search_games_from_db, get_all_users_from_db, search_users_from_db, delete_game as delete_game_backend, delete_user as delete_user_backend
from ...backend.ban_user_be import ban_user as ban_user_backend
import asyncio
import os

search_debounce_task = None  # Biến toàn cục debounce

def admin_interface_screen(page, state, render):
    # Lấy đường dẫn tuyệt đối đến file logo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "..", "..", "data", "images", "Logo_game_rmb.png")
   
    # State cho admin interface
    if "admin_search" not in state:
        state["admin_search"] = ""
    if "admin_current_page" not in state:
        state["admin_current_page"] = 1
    if "admin_games_per_page" not in state:
        state["admin_games_per_page"] = 10
    if "admin_selected_category" not in state:
        state["admin_selected_category"] = "all"
    if "admin_view" not in state:
        state["admin_view"] = "games"
    
    # State cho user management
    if "admin_user_search" not in state:
        state["admin_user_search"] = ""
    if "admin_user_current_page" not in state:
        state["admin_user_current_page"] = 1
    if "admin_user_per_page" not in state:
        state["admin_user_per_page"] = 5
    if "admin_user_ban_reasons" not in state:
        state["admin_user_ban_reasons"] = {}
    if "admin_user_ban_reason_entered" not in state:
        state["admin_user_ban_reason_entered"] = {}  # Theo dõi trạng thái lần đầu nhập lý do
    
    def handle_menu(menu_item):
        if menu_item == "logout":
            state.clear()
            state.update({
                "screen": "login",
                "login_error": "",
                "login_email": "",
                "login_password": "",
                "username": "",
                "cart": [],
                "cart_selected": [],
                "purchase_history": []
            })
            render()
            return
        elif menu_item == "allgame":
            state["screen"] = "allgame"
            render()
            return
    
    def build_menu_row():
        return ft.Row([
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        content=ft.Row([ft.Icon(ft.Icons.LOGOUT, size=18), ft.Text("Logout", size=14)]),
                        on_click=lambda e: handle_menu("logout")
                    ),
                ],
                icon=ft.Icons.MENU
            ),
            ft.Text("ADMIN", color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    async def on_search_change(e):
        state["admin_search"] = e.control.value

    def on_search_click(e):
        state["admin_current_page"] = 1
        render()
    
    def on_category_change(e):
        state["admin_selected_category"] = e.control.value
        state["admin_current_page"] = 1
        render()
    
    def get_all_games():
        try:
            all_games = get_all_games_from_db()
            return all_games
        except Exception as e:
            print(f"Error getting games from database: {e}")
            return []
    
    def filter_games():
        search_term = state["admin_search"]
        selected_category = state["admin_selected_category"]
        
        try:
            if search_term:
                all_games = search_games_from_db(search_term, selected_category)
            else:
                all_games = get_all_games_from_db()
                
            if selected_category != "all":
                filtered_games = []
                for game in all_games:
                    game_category = game.get("category", "")
                    if game_category and selected_category in game_category:
                        filtered_games.append(game)
                all_games = filtered_games
            
            return all_games
        except Exception as e:
            print(f"Error filtering games: {e}")
            return []
    
    def get_paginated_games():
        filtered_games = filter_games()
        start_idx = (state["admin_current_page"] - 1) * state["admin_games_per_page"]
        end_idx = start_idx + state["admin_games_per_page"]
        return filtered_games[start_idx:end_idx], len(filtered_games)
    
    def change_page(page_num):
        state["admin_current_page"] = page_num
        render()
    
    def switch_view(view_type):
        state["admin_view"] = view_type
        state["admin_current_page"] = 1
        render()
    
    def on_user_search_change(e):
        state["admin_user_search"] = e.control.value

    def on_user_search_click(e):
        state["admin_user_current_page"] = 1
        render()

    def filter_users():
        search_term = state["admin_user_search"]
        
        try:
            if search_term:
                all_users = search_users_from_db(search_term)
            else:
                all_users = get_all_users_from_db()
            
            filtered_users = [user for user in all_users if user.get("role", "") == "user"]
            
            return filtered_users
        except Exception as e:
            print(f"Error filtering users: {e}")
            return []

    def get_paginated_users():
        filtered_users = filter_users()
        start_idx = (state["admin_user_current_page"] - 1) * state["admin_user_per_page"]
        end_idx = start_idx + state["admin_user_per_page"]
        return filtered_users[start_idx:end_idx], len(filtered_users)

    def change_user_page(page_num):
        state["admin_user_current_page"] = page_num
        render()

    if "admin_user_deleting_index" not in state:
        state["admin_user_deleting_index"] = None

    def set_user_deleting_index(idx):
        state["admin_user_deleting_index"] = idx
        render()

    def set_ban_reason(idx, reason):
        """Set ban reason for a specific user index"""
        state["admin_user_ban_reasons"][idx] = reason
        # Chỉ cập nhật UI, không render lại toàn bộ trang
        page.update()

    def build_user_card(user, index):
        action_controls = []
        if state.get("admin_user_deleting_index") == index:
            reason_field = ft.TextField(
                hint_text="Ban reason...",
                width=200,
                value=state["admin_user_ban_reasons"].get(index, ""),
                on_change=lambda e: set_ban_reason(index, e.control.value)
            )
            
            # Thêm error message nếu có
            error_message = None
            if state.get("admin_show_ban_error") == index:
                error_message = ft.Container(
                    content=ft.Text(
                        "Please enter a ban reason!",
                        color=ft.Colors.RED_400,
                        size=12
                    ),
                    margin=ft.margin.only(top=5)
                )
            
            action_controls.append(reason_field)
            if error_message:
                action_controls.append(error_message)
            action_controls.append(
                ft.ElevatedButton(
                    "Ban User",
                    icon=ft.Icons.BLOCK,
                    on_click=lambda e, idx=index: do_ban_user(idx),
                    bgcolor=ft.Colors.RED_600,
                    color=ft.Colors.WHITE,
                    height=36,
                    width=100
                )
            )
        else:
            action_controls.append(
                ft.IconButton(
                    icon=ft.Icons.BLOCK,
                    icon_color=ft.Colors.RED_400,
                    icon_size=20,
                    tooltip="Ban User",
                    on_click=lambda e, idx=index: set_user_deleting_index(idx)
                )
            )
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                f"Full Name: {user.get('fullname', 'N/A')}",
                                color=ft.Colors.WHITE,
                                size=16,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                f"Username: {user['username']}",
                                color=ft.Colors.GREY_400,
                                size=14,
                                weight=ft.FontWeight.NORMAL
                            ),
                            ft.Text(f"Email: {user['email']}", color=ft.Colors.GREY_400, size=14),
                            ft.Text(f"Balance: ${user['balance']:.2f}", color=ft.Colors.GREEN_400, size=14),
                            ft.Text(f"Phone: {user['phone']}", color=ft.Colors.GREY_400, size=14),
                            ft.Text(f"Age: {user['age']} | Gender: {user['gender']}", color=ft.Colors.GREY_400, size=14),
                        ], spacing=2),
                        expand=True
                    ),
                    *action_controls
                ]),
            ]),
            bgcolor=ft.Colors.GREY_900,
            padding=ft.padding.all(16),
            border_radius=8,
            margin=ft.margin.only(bottom=12)
        )

    def do_ban_user(idx):
        filtered_users = filter_users()
        actual_index = (state["admin_user_current_page"] - 1) * state["admin_user_per_page"] + idx
        
        if 0 <= actual_index < len(filtered_users):
            user_to_ban = filtered_users[actual_index]
            ban_reason = state["admin_user_ban_reasons"].get(idx, "").strip()
            
            print(f"Debug: Ban reason for index {idx}: '{ban_reason}'")
            
            if not ban_reason:
                # Hiển thị thông báo lỗi màu đỏ
                state["admin_show_ban_error"] = idx
                print(f"Debug: Setting error for index {idx}")
                render()  # Force render lại để hiển thị error
                return
            
            # Xóa thông báo lỗi nếu có
            if "admin_show_ban_error" in state:
                del state["admin_show_ban_error"]
            
            ban_user(user_to_ban, ban_reason)
            state["admin_user_deleting_index"] = None
            if idx in state["admin_user_ban_reasons"]:
                del state["admin_user_ban_reasons"][idx]
            render()
        else:
            print(f"Error: Invalid index {actual_index} for filtered_users length {len(filtered_users)}")
    
    def do_delete_user(idx):
        filtered_users = filter_users()
        actual_index = (state["admin_user_current_page"] - 1) * state["admin_user_per_page"] + idx
        
        if 0 <= actual_index < len(filtered_users):
            user_to_delete = filtered_users[actual_index]
            delete_user(user_to_delete)
            state["admin_user_deleting_index"] = None
            render()
        else:
            print(f"Error: Invalid index {actual_index} for filtered_users length {len(filtered_users)}")

    def ban_user(user, reason):
        print(f"Ban user called for: {user['username']} with reason: {reason}")
        result = ban_user_backend(user["id"], reason)
        if result:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"User '{user['username']}' banned successfully! Email notification sent."))
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Failed to ban user '{user['username']}'!"))
        page.snack_bar.open = True
        render()
        page.update()
    
    def delete_user(user):
        print(f"Delete user called for: {user['username']}")
        result = delete_user_backend(user["id"])
        if result:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"User '{user['username']}' deleted successfully!"))
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Failed to delete user '{user['username']}'!"))
        page.snack_bar.open = True
        render()
        page.update()
    
    def build_user_pagination(total_users):
        total_pages = (total_users + state["admin_user_per_page"] - 1) // state["admin_user_per_page"]
        if total_pages <= 1:
            return ft.Container()
        
        current_page = state["admin_user_current_page"]
        pages = []
        
        if current_page > 1:
            pages.append(ft.TextButton("<<", on_click=lambda e: change_user_page(1)))
            pages.append(ft.TextButton("<", on_click=lambda e: change_user_page(current_page - 1)))
        
        start_page = max(1, current_page - 2)
        end_page = min(total_pages, current_page + 2)
        
        for page_num in range(start_page, end_page + 1):
            if page_num == current_page:
                pages.append(ft.TextButton(str(page_num), style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600)))
            else:
                pages.append(ft.TextButton(str(page_num), on_click=lambda e, p=page_num: change_user_page(p)))
        
        if current_page < total_pages:
            pages.append(ft.TextButton(">", on_click=lambda e: change_user_page(current_page + 1)))
            pages.append(ft.TextButton(">>", on_click=lambda e: change_user_page(total_pages)))
        
        return ft.Row(pages, alignment=ft.MainAxisAlignment.CENTER)
    
    def edit_game(game_index):
        filtered_games = filter_games()
        actual_index = (state["admin_current_page"] - 1) * state["admin_games_per_page"] + game_index
        
        if actual_index < len(filtered_games):
            game_to_edit = filtered_games[actual_index]
            if game_to_edit.get("source_list") == "database":
                state["game_to_edit"] = game_to_edit
            else:
                if isinstance(game_to_edit.get("genres"), str):
                    game_to_edit["genres"] = [g.strip() for g in game_to_edit["genres"].split(",") if g.strip()]
                elif not isinstance(game_to_edit.get("genres"), list):
                    game_to_edit["genres"] = []
                state["game_to_edit"] = game_to_edit
            state["screen"] = "edit_game"
            render()
    
    def delete_game(game_index):
        filtered_games = filter_games()
        actual_index = (state["admin_current_page"] - 1) * state["admin_games_per_page"] + game_index

        if 0 <= actual_index < len(filtered_games):
            game_to_delete = filtered_games[actual_index]
            result = delete_game_backend(game_to_delete["id"])
            if result:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Game '{game_to_delete['name']}' deleted successfully!"))
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Failed to delete game '{game_to_delete['name']}'!"))
            page.snack_bar.open = True
            render()
            page.update()
        else:
            print(f"Error: Invalid index {actual_index} for filtered_games length {len(filtered_games)}")
    
    def add_new_game():
        print("Add new game function called!")
        state["screen"] = "add_game"
        print(f"Screen set to: {state['screen']}")
        render()
    
    if "admin_editing_index" not in state:
        state["admin_editing_index"] = None
    if "admin_deleting_index" not in state:
        state["admin_deleting_index"] = None

    def set_editing_index(idx):
        state["admin_editing_index"] = idx
        state["admin_deleting_index"] = None
        render()

    def set_deleting_index(idx):
        state["admin_deleting_index"] = idx
        state["admin_editing_index"] = None
        render()

    def do_edit(idx):
        state["admin_editing_index"] = None
        edit_game(idx)

    def do_delete(idx):
        state["admin_deleting_index"] = None
        delete_game(idx)

    def build_game_card(game, index):
        price_display = game.get("price_display", "")
        if not price_display:
            price_value = game.get("price", 0)
            if price_value == 0:
                price_display = "Free"
            else:
                price_display = f"${price_value:.2f}"
        category = game.get("category", "Database Games")
        action_controls = []
        if state.get("admin_editing_index") == index:
            action_controls.append(
                ft.ElevatedButton(
                    "Edit",
                    icon=ft.Icons.EDIT,
                    on_click=lambda e, idx=index: do_edit(idx),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE),
                    height=36,
                    width=80,
                )
            )
        else:
            action_controls.append(
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color=ft.Colors.BLUE_400,
                    icon_size=20,
                    on_click=lambda e, idx=index: set_editing_index(idx)
                )
            )
        if state.get("admin_deleting_index") == index:
            action_controls.append(
                ft.ElevatedButton(
                    "Delete",
                    icon=ft.Icons.DELETE,
                    on_click=lambda e, idx=index: do_delete(idx),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE),
                    height=36,
                    width=90,
                )
            )
        else:
            action_controls.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED_400,
                    icon_size=20,
                    on_click=lambda e, idx=index: set_deleting_index(idx)
                )
            )
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Container(
                        width=80,
                        height=80,
                        border_radius=8,
                        content=ft.Image(
                            src=game["image"],
                            width=80,
                            height=80,
                            fit=ft.ImageFit.COVER,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Column([
                            ft.Text(game["name"], size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(f"Release: {game.get('release_date', 'Unknown')}", size=12, color=ft.Colors.GREY_400),
                            ft.Text(price_display, size=14, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD),
                            ft.Text(category, size=10, color=ft.Colors.BLUE_400),
                        ], spacing=4)
                    ),
                    ft.Row(action_controls)
                ], alignment=ft.MainAxisAlignment.START),
                padding=16,
                bgcolor=ft.Colors.GREY_900,
                border_radius=8,
            ),
            margin=ft.margin.only(bottom=8)
        )
    
    def build_pagination(total_games):
        total_pages = (total_games + state["admin_games_per_page"] - 1) // state["admin_games_per_page"]
        if total_pages <= 1:
            return ft.Container()
        
        current_page = state["admin_current_page"]
        pages = []
        
        if current_page > 1:
            pages.append(ft.TextButton("<<", on_click=lambda e: change_page(1)))
            pages.append(ft.TextButton("<", on_click=lambda e: change_page(current_page - 1)))
        
        start_page = max(1, current_page - 2)
        end_page = min(total_pages, current_page + 2)
        
        for page_num in range(start_page, end_page + 1):
            if page_num == current_page:
                pages.append(ft.TextButton(str(page_num), style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600)))
            else:
                pages.append(ft.TextButton(str(page_num), on_click=lambda e, p=page_num: change_page(p)))
        
        if current_page < total_pages:
            pages.append(ft.TextButton(">", on_click=lambda e: change_page(current_page + 1)))
            pages.append(ft.TextButton(">>", on_click=lambda e: change_page(total_pages)))
        
        return ft.Row(pages, alignment=ft.MainAxisAlignment.CENTER)
    
    current_games, total_games = get_paginated_games()
    game_cards = [build_game_card(game, i) for i, game in enumerate(current_games)]
    current_users, total_users = get_paginated_users()
    user_cards = [build_user_card(user, i) for i, user in enumerate(current_users)]
    
    categories = [
        ft.dropdown.Option("all", "All Categories"),
        ft.dropdown.Option("Action", "Action"),
        ft.dropdown.Option("Adventure", "Adventure"),
        ft.dropdown.Option("RPG", "RPG"),
        ft.dropdown.Option("Strategy", "Strategy"),
        ft.dropdown.Option("Simulation", "Simulation"),
        ft.dropdown.Option("Sports", "Sports"),
        ft.dropdown.Option("Racing", "Racing"),
        ft.dropdown.Option("Puzzle", "Puzzle"),
        ft.dropdown.Option("Horror", "Horror"),
        ft.dropdown.Option("Fighting", "Fighting"),
        ft.dropdown.Option("Shooter", "Shooter"),
        ft.dropdown.Option("Stealth", "Stealth"),
        ft.dropdown.Option("Survival", "Survival"),
        ft.dropdown.Option("Open World", "Open World"),
        ft.dropdown.Option("Sandbox", "Sandbox"),
        ft.dropdown.Option("Visual Novel", "Visual Novel"),
        ft.dropdown.Option("Roguelike", "Roguelike"),
        ft.dropdown.Option("Metroidvania", "Metroidvania"),
        ft.dropdown.Option("Platformer", "Platformer"),
        ft.dropdown.Option("Arcade", "Arcade"),
        ft.dropdown.Option("Indie", "Indie"),
        ft.dropdown.Option("Casual", "Casual"),
        ft.dropdown.Option("Educational", "Educational"),
        ft.dropdown.Option("Music", "Music"),
        ft.dropdown.Option("Party", "Party"),
        ft.dropdown.Option("Trivia", "Trivia"),
        ft.dropdown.Option("Board Game", "Board Game"),
        ft.dropdown.Option("Card Game", "Card Game"),
        ft.dropdown.Option("Tower Defense", "Tower Defense"),
        ft.dropdown.Option("MOBA", "MOBA"),
        ft.dropdown.Option("MMO", "MMO"),
        ft.dropdown.Option("Battle Royale", "Battle Royale"),
        ft.dropdown.Option("RTS", "RTS"),
        ft.dropdown.Option("Turn-based", "Turn-based"),
        ft.dropdown.Option("Real-time", "Real-time"),
        ft.dropdown.Option("Co-op", "Co-op"),
        ft.dropdown.Option("Multiplayer", "Multiplayer"),
        ft.dropdown.Option("Single Player", "Single Player"),
        ft.dropdown.Option("Local Multiplayer", "Local Multiplayer"),
        ft.dropdown.Option("Online Multiplayer", "Online Multiplayer"),
    ]
    
    content = ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Image(
                        src=logo_path,
                        width=50,
                        height=50,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Text("GAME HUB", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
                ]),
                build_menu_row()
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(bottom=20)
        ),
        
        ft.Container(
            content=ft.Row([
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Text("Games", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if state["admin_view"] == "games" else ft.Colors.GREY_400),
                        bgcolor=ft.Colors.GREEN_600 if state["admin_view"] == "games" else ft.Colors.GREY_800,
                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                        border_radius=8
                    ),
                    on_tap=lambda e: switch_view("games")
                ),
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Text("User", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if state["admin_view"] == "users" else ft.Colors.GREY_400),
                        bgcolor=ft.Colors.GREEN_600 if state["admin_view"] == "users" else ft.Colors.GREY_800,
                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                        border_radius=8
                    ),
                    on_tap=lambda e: switch_view("users")
                ),
            ], spacing=0),
            margin=ft.margin.only(bottom=20)
        ),
        
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    expand=True,
                                    content=ft.TextField(
                                        hint_text="Search for Games",
                                        value=state["admin_search"],
                                        on_change=on_search_change,
                                        on_submit=on_search_click,
                                        bgcolor=ft.Colors.GREY_800,
                                        border_color=ft.Colors.GREY_700,
                                        text_style=ft.TextStyle(color=ft.Colors.WHITE),
                                        hint_style=ft.TextStyle(color=ft.Colors.GREY_400),
                                        prefix_icon=ft.Icons.SEARCH
                                    ),
                                ),
                                ft.Container(width=10),
                                ft.IconButton(
                                    icon=ft.Icons.SEARCH,
                                    icon_color=ft.Colors.GREEN_400,
                                    icon_size=24,
                                    on_click=on_search_click,
                                    tooltip="Search"
                                ),
                                ft.Container(width=20),
                                ft.Container(
                                    width=200,
                                    content=ft.Dropdown(
                                        label="Category",
                                        value=state["admin_selected_category"],
                                        options=categories,
                                        on_change=on_category_change,
                                        bgcolor=ft.Colors.GREY_800,
                                        border_color=ft.Colors.GREY_700,
                                        text_style=ft.TextStyle(color=ft.Colors.WHITE),
                                        label_style=ft.TextStyle(color=ft.Colors.GREY_400),
                                        menu_height=300,
                                    ),
                                ),
                            ]),
                            margin=ft.margin.only(bottom=20)
                        ),
                        
                        ft.Container(
                            content=ft.Column(
                                controls=game_cards,
                                scroll="auto",
                                spacing=8
                            ),
                            height=600,
                            expand=True,
                        ),
                        
                        ft.Container(
                            content=ft.ElevatedButton(
                                content=ft.Text("Add Game", size=16, weight=ft.FontWeight.BOLD),
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.GREEN_600,
                                    color=ft.Colors.WHITE,
                                    padding=ft.padding.symmetric(horizontal=30, vertical=15),
                                ),
                                on_click=lambda e: add_new_game()
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(bottom=20)
                        ),
                        
                        build_pagination(total_games)
                    ]),
                    visible=state["admin_view"] == "games"
                ),
                
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    expand=True,
                                    content=ft.TextField(
                                        hint_text="Search for Users",
                                        value=state["admin_user_search"],
                                        on_change=on_user_search_change,
                                        on_submit=on_user_search_click,
                                        bgcolor=ft.Colors.GREY_800,
                                        border_color=ft.Colors.GREY_700,
                                        text_style=ft.TextStyle(color=ft.Colors.WHITE),
                                        hint_style=ft.TextStyle(color=ft.Colors.GREY_400),
                                        prefix_icon=ft.Icons.SEARCH
                                    ),
                                ),
                                ft.Container(width=10),
                                ft.IconButton(
                                    icon=ft.Icons.SEARCH,
                                    icon_color=ft.Colors.GREEN_400,
                                    icon_size=24,
                                    on_click=on_user_search_click,
                                    tooltip="Search"
                                ),
                            ]),
                            margin=ft.margin.only(bottom=20)
                        ),
                        
                        ft.Container(
                            content=ft.Column(
                                controls=user_cards,
                                scroll="auto",
                                spacing=8
                            ),
                            height=600,
                            expand=True,
                        ),
                        
                        build_user_pagination(total_users)
                    ]),
                    visible=state["admin_view"] == "users"
                ),
            ])
        )
    ])
    
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[content],
                scroll="auto"
            ),
            padding=20,
            expand=True,
            bgcolor=ft.Colors.BLACK
        )
    )
    page.update()