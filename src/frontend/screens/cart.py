import flet as ft
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.cart_be import get_user_cart, remove_from_cart, update_cart_quantity, get_cart_total, checkout_selected
from backend.auth import get_user_by_id  # Thêm import lấy balance

def cart_screen(page, state, render, footer):
    # Lấy user_id từ state, nếu không có thì lấy từ username
    user_id = state.get("user_id")
    if user_id is None:
        username = state.get("username", "")
        if username:
            try:
                from backend.auth import get_user_by_username
                user_data = get_user_by_username(username)
                if user_data:
                    user_id = user_data[0]['id']
                else:
                    user_id = 20  # Test với user 20
            except Exception as e:
                user_id = 20  # Test với user 20
        else:
            user_id = 20  # Test với user 20
    # Load cart từ database
    try:
        cart_items_from_db = get_user_cart(user_id)
        cart_games_list = []
        for item in cart_items_from_db:
            game_data = {
                "id": item['game_id'],
                "name": item.get('game_title', 'Unknown Game'),
                "price": float(item.get('game_price', 0)),
                "description": item.get('game_description', 'No description available'),
                "image": item.get('game_image', 'https://via.placeholder.com/90x90'),
                "cart_item_id": item['id']
            }
            cart_games_list.append(game_data)
    except Exception as e:
        cart_games_list = state.get("cart", [])
    
    # Khởi tạo cart_selected
    if "cart_selected" not in state or not isinstance(state["cart_selected"], dict):
        state["cart_selected"] = {}
    for i, game in enumerate(cart_games_list):
        game_id = f"cart_game_{i}"
        if game_id not in state["cart_selected"]:
            state["cart_selected"][game_id] = False  # Mặc định không chọn
    if "cart_success" not in state:
        state["cart_success"] = False

    # Lấy balance (coin) của user
    try:
        user_info = get_user_by_id(user_id)
        if user_info and 'coin' in user_info[0]:
            balance = float(user_info[0]['coin'])
        else:
            balance = 0.0
    except Exception as e:
        balance = 0.0

    def remove_game(cart_item_id):
        state["cart_success"] = False
        try:
            success = remove_from_cart(cart_item_id)
            if success:
                cart_items_from_db = get_user_cart(user_id)
                cart_games_list.clear()
                for item in cart_items_from_db:
                    game_data = {
                        "id": item['game_id'],
                        "name": item.get('game_title', 'Unknown Game'),
                        "price": float(item.get('game_price', 0)),
                        "description": item.get('game_description', 'No description available'),
                        "image": item.get('game_image', 'https://via.placeholder.com/90x90'),
                        "cart_item_id": item['id']
                    }
                    cart_games_list.append(game_data)
        except Exception as e:
            print(f"Error removing game: {e}")
        render()

    def toggle_game_selection(game_id):
        state["cart_success"] = False
        selected = not state["cart_selected"].get(game_id, False)
        state["cart_selected"][game_id] = selected
        
        # Force recalculate selected_games
        selected_games = []
        total = 0.0
        for i, game in enumerate(cart_games_list):
            game_id_check = f"cart_game_{i}"
            is_selected = state["cart_selected"].get(game_id_check, False)
            if is_selected:
                selected_games.append(game)
                price = game['price'] if isinstance(game['price'], (int, float)) else 0
                total += price
        
        render()

    def game_item(game, index):
        cart_item_id = game.get("cart_item_id", 0)
        game_id = f"cart_game_{index}"
        checked = state["cart_selected"].get(game_id, False)  # Mặc định không chọn
        return ft.Container(
            ft.Row([
                ft.Image(src=game["image"], width=90, height=90, fit=ft.ImageFit.COVER, border_radius=8),
                ft.Container(
                    ft.Column([
                        ft.Row([
                            ft.Checkbox(
                                value=checked,
                                on_change=lambda e, gid=game_id: toggle_game_selection(gid),
                                fill_color="#22c55e",
                                check_color="white"
                            ),
                            ft.Text(game["name"], size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Container(expand=True),
                            ft.Text(f"${game['price']:.2f}" if isinstance(game['price'], (int, float)) else game['price'], size=18, color="#22c55e", weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color="#e74c3c",
                                tooltip="Remove",
                                on_click=lambda e, cid=cart_item_id: remove_game(cid)
                            ),
                        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Text(game.get("description", "Game description not available"), size=13, color="#b0b0b0", max_lines=3, overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=6),
                    expand=True,
                    padding=ft.padding.only(left=16)
                )
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#232b39",
            border_radius=12,
            padding=ft.padding.all(16),
            margin=ft.margin.only(bottom=16)
        )

    left_col_items = [
        ft.Container(
            ft.Text("Your Shopping Cart", size=28, weight=ft.FontWeight.BOLD, color="#b0b0b0"),
            margin=ft.margin.only(bottom=16)
        ),
        *[game_item(g, i) for i, g in enumerate(cart_games_list)]
    ]
    if not cart_games_list:
        left_col_items.append(ft.Text("No games in cart.", color="#b0b0b0"))

    left_col = ft.Column(left_col_items, alignment=ft.MainAxisAlignment.START, expand=True, scroll=ft.ScrollMode.AUTO)

    # Tính toán các game được chọn và tổng tiền
    selected_games = []
    total = 0.0
    for i, game in enumerate(cart_games_list):
        game_id = f"cart_game_{i}"
        is_selected = state["cart_selected"].get(game_id, False)  # Mặc định không chọn
        if is_selected:
            selected_games.append(game)
            price = game['price'] if isinstance(game['price'], (int, float)) else 0
            total += price

    remaining_balance = balance - total

    def do_payment(e=None):
        try:
            # Kiểm tra balance trước khi thanh toán (cho phép mua game free)
            if total > 0 and total > balance:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Insufficient balance! You need ${total:.2f} but have ${balance:.2f}", color="white"),
                    bgcolor="#e74c3c",
                    duration=4000
                )
                page.snack_bar.open = True
                page.update()
                return
            
            selected_cart_item_ids = [g['cart_item_id'] for g in selected_games]
            success = checkout_selected(user_id, selected_cart_item_ids)
            if success:
                state["cart_success"] = True
                # Reset cart selection state sau khi mua thành công
                state["cart_selected"] = {}
                
                # Reload cart data từ database
                try:
                    cart_items_from_db = get_user_cart(user_id)
                    
                    # Cập nhật cart_games_list với data mới
                    cart_games_list.clear()
                    for item in cart_items_from_db:
                        game_data = {
                            "id": item['game_id'],
                            "name": item.get('game_title', 'Unknown Game'),
                            "price": float(item.get('game_price', 0)),
                            "description": item.get('game_description', 'No description available'),
                            "image": item.get('game_image', 'https://via.placeholder.com/90x90'),
                            "cart_item_id": item['id']
                        }
                        cart_games_list.append(game_data)
                    
                    # Reset selection state cho games mới
                    state["cart_selected"] = {}
                    for i, game in enumerate(cart_games_list):
                        game_id = f"cart_game_{i}"
                        state["cart_selected"][game_id] = False  # Mặc định không chọn
                except Exception as e:
                    print(f"Error reloading cart data: {e}")
                
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Payment successful! ${total:.2f} deducted from your balance. Games added to library.", color="white"),
                    bgcolor="#22c55e",
                    duration=4000
                )
                page.snack_bar.open = True
                page.update()
                
                # Force refresh UI sau khi mua
                render()
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Payment failed. Insufficient balance or server error.", color="white"),
                    bgcolor="#e74c3c",
                    duration=4000
                )
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            print(f"Error processing payment: {e}")
            state["cart_success"] = False
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Payment failed. Please try again.", color="white"),
                bgcolor="#e74c3c",
                duration=3000
            )
            page.snack_bar.open = True
            page.update()

    def confirm_cart(e):
        if len(selected_games) == 0:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please select at least one game to proceed.", color="white"),
                bgcolor="#e74c3c",
                duration=3000
            )
            page.snack_bar.open = True
            page.update()
            return
        # Gọi trực tiếp do_payment thay vì hiển thị dialog
        do_payment()

    game_list_column = ft.Container(
        ft.Column([
            ft.Row([
                ft.Image(src=g["image"], width=32, height=32, fit=ft.ImageFit.COVER, border_radius=6),
                ft.Text(g["name"], size=14, color=ft.Colors.WHITE, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Container(expand=True),
                ft.Text(f"${g['price']:.2f}" if isinstance(g['price'], (int, float)) else g['price'], size=14, color="#22c55e", weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.START)
            for g in selected_games
        ], spacing=8, scroll=ft.ScrollMode.AUTO),
        height=min(300, len(selected_games) * 60),  # Tăng height để hiển thị nhiều games hơn
        expand=True
    )

    right_col_items = [
        ft.Text("Your Cart", size=20, weight=ft.FontWeight.BOLD, color="#b0b0b0"),
        ft.Container(height=8),
        ft.Text(f"Selected: {len(selected_games)} games", size=14, color="#666", weight=ft.FontWeight.W_500),
    ]
    if selected_games:
        right_col_items.append(game_list_column)
    else:
        right_col_items.append(ft.Text("No games selected.", color="#b0b0b0"))

    right_col_items += [
        ft.Divider(height=2, color="#333", thickness=1),
        ft.Row([
            ft.Text("Balance:", size=14, color="#b0b0b0"),
            ft.Container(expand=True),
            ft.Text(f"${balance:.2f}", size=14, color="#22c55e", weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.START),
        ft.Row([
            ft.Text("Items selected:", size=14, color="#b0b0b0"),
            ft.Container(expand=True),
            ft.Text(f"{len(selected_games)}", size=14, color="white", weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.START),
        ft.Row([
            ft.Text("Total amount:", size=16, color="#b0b0b0"),
            ft.Container(expand=True),
            ft.Text(f"${total:.2f}", size=18, color="#22c55e", weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.START),
        ft.Row([
            ft.Text("Remaining:", size=14, color="#b0b0b0"),
            ft.Container(expand=True),
            ft.Text(f"${remaining_balance:.2f}", size=14, color="#22c55e" if remaining_balance >= 0 else "#e74c3c", weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.START),
        ft.Text("Insufficient balance, please top up to proceed with payment", size=12, color="#e74c3c") if remaining_balance < 0 else ft.Container(height=0),
        ft.Container(height=24),
        # Thêm thông báo khi không có item nào được chọn
        ft.Text("Please choose items to purchase", size=12, color="#e74c3c", text_align=ft.TextAlign.CENTER) if len(selected_games) == 0 else ft.Container(height=0),
        ft.Container(
            ft.ElevatedButton(
                "Confirm Purchase",
                bgcolor="#22c55e" if (len(selected_games) > 0 and remaining_balance >= 0) else "#666666",
                color="white",
                width=200,
                height=48,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=confirm_cart,
                disabled=len(selected_games) == 0 or remaining_balance < 0
            ),
            alignment=ft.alignment.center
        ),
        ft.Container(height=16),
    ]

    # Tính toán height dựa trên số lượng selected games
    min_height = 500  # Tăng min height để hiển thị đủ nút Confirm
    height_per_selected_game = 60  # Height cho mỗi selected game
    dynamic_height = min_height + (len(selected_games) * height_per_selected_game)
    
    right_col = ft.Container(
        ft.Column(right_col_items, alignment=ft.MainAxisAlignment.START, spacing=16),
        bgcolor="#232b39",
        border_radius=12,
        padding=ft.padding.all(24),
        width=320,
        height=dynamic_height,
        margin=ft.margin.only(left=24, top=40)
    )

    if state["cart_success"]:
        def on_ok(e=None):
            state["cart_success"] = False
            render()
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Payment successful!",
                    size=48,
                    color="#22c55e",
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=32),
                ft.ElevatedButton(
                    "OK",
                    bgcolor="#22c55e",
                    color="white",
                    width=160,
                    height=48,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=on_ok
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )

    
    return ft.Column([
        ft.Container(
            ft.Row([
                left_col,
                right_col
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
            padding=ft.padding.symmetric(horizontal=40)
        ),
        footer
    ], expand=True, spacing=0, alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.AUTO)