import flet as ft
from .home import build_menu_row, build_footer
from ...backend.game_detail_be import get_top_rated_games, get_game_detail_by_id
from ...backend.cart_be import add_to_cart


def game_detail_screen(page, state, render):
    # Lấy thông tin game từ state
    selected_game = state.get("selected_game", {
        "id": 1,
        "name": "Assassin's Creed Mirage",
        "image": "https://cdn1.epicgames.com/offer/9bcf5a4dc1d54cb6ab1a42f3a70c5cf4/amwide_2560x1440-5fe11b7b8703d49072b7f66ec75e5083",
        "price": 0
    })
    
    # Lấy user_id từ state
    user_id = state.get("user_id")
    if user_id is None:
        # Nếu không có user_id, thử lấy từ username
        username = state.get("username", "")
        if username:
            # Tìm user_id từ username
            try:
                from backend.auth import get_user_by_username
                user_data = get_user_by_username(username)
                if user_data:
                    user_id = user_data[0]['id']
                else:
                    user_id = None
            except Exception as e:
                user_id = None
        else:
            user_id = None
    
    # Lấy chi tiết game từ backend nếu có id
    if selected_game.get("id"):
        db_game = get_game_detail_by_id(selected_game["id"], user_id)
        if db_game:
            game = db_game
            print(f"DEBUG: Got game from DB - ID: {game.get('id')}, Name: {game.get('name')}, Title: {game.get('title')}")
        else:
            game = selected_game
            print(f"DEBUG: Using selected_game - ID: {game.get('id')}, Name: {game.get('name')}, Title: {game.get('title')}")
    else:
        game = selected_game
        print(f"DEBUG: Using selected_game (no ID) - Name: {game.get('name')}, Title: {game.get('title')}")
    
    # Debug: In ra tất cả keys trong game object
    print(f"DEBUG: Game object keys: {list(game.keys())}")
    print(f"DEBUG: Game object: {game}")
    
    if "price" not in game:
        game["price"] = selected_game.get("price", 0)
    
    def set_home(e=None):
        state["screen"] = "home"
        render()

    def set_privacy(e=None):
        state["screen"] = "privacy_policy"
        render()

    def set_terms(e=None):
        state["screen"] = "terms_of_use"
        render()

    def set_about_us(e=None):
        state["screen"] = "about_us"
        render()

    def set_contact_us(e=None):
        state["screen"] = "contact_us"
        render()

    def handle_menu(action):
        if action == "logout":
            state.clear()
            state.update({
                "screen": "login",
                "login_error": "",
                "login_email": "",
                "login_password": ""
            })
            render()
        elif action == "account":
            state["screen"] = "account"
            render()
        elif action == "payment":
            state["screen"] = "payment"
            render()
        elif action == "cart":
            state["screen"] = "cart"
            render()
        elif action == "history":
            state["screen"] = "history"
            render()
        elif action == "allgame":
            state["screen"] = "allgame"
            render()
        elif action == "ai_chat":
            state["screen"] = "ai_chat"
            render()

    def add_to_cart(e):
        # Lấy user_id từ state, nếu không có thì lấy từ username
        user_id = state.get("user_id")
        if user_id is None:
            # Nếu không có user_id, thử lấy từ username
            username = state.get("username", "")
            if username:
                # Tìm user_id từ username
                try:
                    from backend.auth import get_user_by_username
                    user_data = get_user_by_username(username)
                    if user_data:
                        user_id = user_data[0]['id']
                    else:
                        user_id = 1  # Fallback
                except:
                    user_id = 1  # Fallback
            else:
                user_id = 1  # Fallback
        
        game_id = game.get("id", 1)
        
        try:
            # Import function từ cart_be
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from backend.cart_be import add_to_cart as add_to_cart_db, get_cart_count
            
            # Thêm game vào cart qua backend
            success = add_to_cart_db(user_id, game_id, 1)
            
            if success:
                # Cập nhật state để button chuyển thành "In your cart"
                game["in_cart"] = True
                
                # Cập nhật cart count trong state
                cart_count = get_cart_count(user_id)
                state["cart"] = [None] * cart_count  # Tạo list với số lượng items
                
                # Hiển thị thông báo thành công
                page.snack_bar = ft.SnackBar(
                    ft.Text("Game added to cart successfully!", color="white"), 
                    bgcolor="#22c55e"
                )
                page.snack_bar.open = True
                
                # Render lại để cập nhật button và cart count
                render()
            else:
                # Hiển thị thông báo lỗi
                page.snack_bar = ft.SnackBar(
                    ft.Text("Failed to add game to cart", color="white"), 
                    bgcolor="#e74c3c"
                )
                page.snack_bar.open = True
                page.update()
            
        except Exception as e:
            print(f"Error adding to cart: {e}")
            page.snack_bar = ft.SnackBar(
                ft.Text("Error adding game to cart", color="white"), 
                bgcolor="#e74c3c"
            )
            page.snack_bar.open = True
            page.update()

    # Hero Section
    hero_section = ft.Stack([
        ft.Image(
            src=game.get("image", "") or "https://via.placeholder.com/1920x600/232b39/ffffff?text=No+Image+Available",
            width=1920,
            height=600,
            fit=ft.ImageFit.COVER,
        ),
        ft.Container(
            ft.Column([
                ft.Text(
                    game.get("name", "Unknown Game").upper(),
                    size=36,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Row([
                    # Genres container - có thể wrap
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                ft.Text(genre.strip().upper(), size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor="#333",
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=4
                            ) for genre in (game.get('genres', '').split(', ') if game.get('genres') else [])
                        ], wrap=True, spacing=8),
                        expand=True
                    ),
                    # Rating luôn ở bên phải
                    ft.Row([
                        ft.Icon(ft.Icons.STAR, color=ft.Colors.WHITE, size=16),
                        ft.Text(
                            f"{game.get('rating', 4.5)}/5",
                            size=16,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            f"{game.get('ratings_count', '50K')} Ratings",
                            size=14,
                            color="#b0b0b0"
                        )
                    ], spacing=4)
                ], alignment=ft.MainAxisAlignment.START),
                ft.Row([
                    ft.Text(
                        "Free" if game['price'] == 0 else (f"${game['price']:.2f}" if isinstance(game['price'], (int, float)) else game['price']),
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Purchased" if game.get('is_purchased', False) else ("In your cart" if game.get('in_cart', False) else "Add to cart"),
                        icon=ft.Icons.CHECK_CIRCLE if game.get('is_purchased', False) else (ft.Icons.SHOPPING_BAG if game.get('in_cart', False) else ft.Icons.SHOPPING_CART),
                        bgcolor="#6b7280" if game.get('is_purchased', False) else ("#f59e0b" if game.get('in_cart', False) else "#22c55e"),
                        color=ft.Colors.WHITE,
                        height=48,
                        width=160,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=None if (game.get('is_purchased', False) or game.get('in_cart', False)) else add_to_cart,
                        disabled=game.get('is_purchased', False) or game.get('in_cart', False)
                    )
                ], alignment=ft.MainAxisAlignment.START),
                ft.Text(
                    "For buying and downloading the beta and the game, you agree to the GameHub Privacy and Policy and GameHub Terms of Use.",
                    size=12,
                    color="#b0b0b0",
                    width=500
                )
            ], spacing=16, alignment=ft.MainAxisAlignment.START),
            bgcolor="#232b39",
            padding=ft.padding.all(32),
            border_radius=12,
            width=600,
            left=56,
            bottom=56,
            alignment=ft.alignment.bottom_left,
        ),
    ], width=1920, height=600)

    # Description Section
    description_section = ft.Container(
        ft.Column([
            ft.Text(
                "Description",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            ft.Text(
                game.get("description", f"{game.get('name', 'This game')} is an exciting game that offers immersive gameplay and stunning graphics. Experience the adventure and discover what makes this game special."),
                size=16,
                color="#b0b0b0",
                width=800
            )
        ], spacing=20, alignment=ft.MainAxisAlignment.START),
        bgcolor="#232b39",
        padding=ft.padding.all(28),
        border_radius=12,
        width=850
    )

    # Minimum Configuration Section
    min_config = game.get('min_config', {})
    min_config_section = ft.Container(
        ft.Column([
            ft.Text(
                "Minimum Configuration",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            ft.Column([
                ft.Text(f"Processor: {min_config.get('processor', min_config.get('cpu', ''))}", size=16, color="#b0b0b0"),
                ft.Text(f"Memory: {min_config.get('memory', min_config.get('ram', ''))}", size=16, color="#b0b0b0"),
                ft.Text(f"Graphics: {min_config.get('graphics', min_config.get('gpu', ''))}", size=16, color="#b0b0b0"),
                ft.Text(f"Storage: {min_config.get('storage', '')}", size=16, color="#b0b0b0"),
            ], spacing=12)
        ], spacing=20, alignment=ft.MainAxisAlignment.START),
        bgcolor="#232b39",
        padding=ft.padding.all(28),
        border_radius=12,
        width=850
    )

    # Top Rated Games Section
    top_rated_games_result = get_top_rated_games(10)  # Lấy 10 game top rated
    top_rated_games = top_rated_games_result if isinstance(top_rated_games_result, list) else []
    
    # Loại bỏ game hiện tại khỏi danh sách top rated
    current_game_id = game.get("id")
    if current_game_id:
        top_rated_games = [g for g in top_rated_games if g.get("id") != current_game_id]
    
    # Chỉ lấy 10 game đầu tiên (sau khi loại bỏ game hiện tại)
    top_rated_games = top_rated_games[:10]

    def top_rated_card(game):
        def open_game_detail(e):
            state["selected_game"] = {"id": game["id"]}
            state["screen"] = "game_detail"
            render()
        
        def on_hover(e):
            container.border = ft.border.all(2, "#ffffff") if e.data == "true" else None
            container.bgcolor = "#2a3441" if e.data == "true" else "#232b39"
            page.update()
        
        container = ft.Container(
            ft.Column([
                ft.Image(
                    src=game.get("image", "") or "https://via.placeholder.com/300x120/232b39/ffffff?text=No+Image",
                    width=300,
                    height=120,
                    fit=ft.ImageFit.COVER,
                    border_radius=8
                ),
                ft.Text(
                    game.get("name", "Unknown Game"),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                ),
                ft.Text(
                    str(game.get("genres", "")),
                    size=14,
                    color="#b0b0b0"
                ),
                ft.Container(height=8),
                ft.ElevatedButton(
                    "See more",
                    bgcolor="#22c55e",
                    color=ft.Colors.WHITE,
                    height=32,
                    width=120,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=open_game_detail
                )
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            width=300,
            bgcolor="#232b39",
            padding=ft.padding.all(16),
            border_radius=8,
            margin=ft.margin.only(bottom=16),
            on_hover=on_hover,
        )
        return container

    # Tạo ListView để hiển thị top rated games với scroll
    top_rated_list = ft.ListView(
        [top_rated_card(game) for game in top_rated_games],
        spacing=12,
        height=400,  # Chiều cao cố định để hiển thị khoảng 2-3 game
        auto_scroll=False
    )

    top_rated_section = ft.Container(
        ft.Column([
            ft.Text(
                "Top rated!!!",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            ft.Text(
                f"Showing {len(top_rated_games)} top rated games",
                size=12,
                color="#b0b0b0"
            ),
            top_rated_list
        ], spacing=20, alignment=ft.MainAxisAlignment.START),
        bgcolor="#232b39",
        padding=ft.padding.all(28),
        border_radius=12,
        width=350
    )

    # Main Content Layout
    main_content = ft.Column([
        hero_section,
        ft.Container(height=40),  # Tăng khoảng cách giữa banner và nội dung
        ft.Container(
            ft.Row([
                ft.Column([
                    description_section,
                    ft.Container(height=24),
                    min_config_section
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(expand=True),  # Thêm expand để đẩy phần top rated sang phải
                top_rated_section
            ], alignment=ft.MainAxisAlignment.START),
            padding=ft.padding.symmetric(horizontal=40)  # Thêm padding cho phần nội dung
        )
    ], alignment=ft.MainAxisAlignment.START)

    page.controls.clear()
    page.add(
        ft.Column([
            build_menu_row(state, render, set_home, handle_menu, None, None),
            ft.Container(
                main_content,
                padding=ft.padding.symmetric(horizontal=0, vertical=0),  # Bỏ tất cả padding để banner sát menu
                expand=True
            ),
            build_footer(set_terms, set_privacy, set_home, set_about_us, set_contact_us)
        ], expand=True, scroll="auto")
    )
    page.update() 