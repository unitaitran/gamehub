import flet as ft
import pandas as pd
import warnings

# Suppress sklearn warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

from ...backend.home_page import get_top_rated_games, get_top_paid_games, get_top_free_games, get_banner_games, get_custom_banner_games
from ...backend.recommendation import get_content_based, get_item_based_cf, get_hybrid, fetch_data_from_db, initialize_recommendation_data, get_trained_models, get_game_details_by_ids
from ...backend.auth import get_all_users
import webbrowser
import asyncio
import requests

# Get users from MySQL
users_data = get_all_users()
if not users_data:
    users_data = []


def build_menu_row(state, render, set_home, handle_menu, on_search_change, search_results_container, set_about_us=None, set_contact_us=None, clear_search_func=None):
    # Lấy cart count từ database
    cart_count = 0
    try:
        from backend.cart_be import get_cart_count
        from backend.auth import get_user_by_username
        
        username = state.get("username", "")
        if username:
            user_data = get_user_by_username(username)
            if user_data:
                user_id = user_data[0]['id']
                cart_count = get_cart_count(user_id)
    except Exception as e:
        print(f"Error getting cart count: {e}")
        cart_count = len(state.get("cart", []))

    menu_items = [
        ft.Image(src=r"gamehub-dev/src/data/images/Logo_game_rmb.png",
                 width=100, height=100),
        ft.Container(width=20),
        ft.Text("GAME HUB", size=20, weight=ft.FontWeight.BOLD, color="#7fff00"),
        ft.Container(width=60),
        ft.TextButton("Home", style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#181f2a",
                      padding=ft.padding.symmetric(horizontal=20)), on_click=set_home),
        ft.TextButton("All Games", style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#181f2a",
                      padding=ft.padding.symmetric(horizontal=20)), on_click=lambda e: handle_menu("allgame")),
        ft.TextButton("AI Chat", style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#181f2a",
                      padding=ft.padding.symmetric(horizontal=20)), on_click=lambda e: handle_menu("ai_chat")),
    ]

    # Thêm About us button nếu có
    if set_about_us:
        menu_items.append(ft.TextButton("About us", style=ft.ButtonStyle(
            color=ft.Colors.WHITE, bgcolor="#181f2a", padding=ft.padding.symmetric(horizontal=20)), on_click=set_about_us))

    # Thêm Contact button nếu có
    if set_contact_us:
        menu_items.append(ft.TextButton("Contact", style=ft.ButtonStyle(
            color=ft.Colors.WHITE, bgcolor="#181f2a", padding=ft.padding.symmetric(horizontal=20)), on_click=set_contact_us))
    
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
    
    # Tạo một Row riêng cho search_box và username để đẩy về bên phải
    right_section = ft.Row(
        controls=[
            search_box,
            ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE, size=22),
            ft.PopupMenuButton(
                content=ft.Row([
                    ft.Text(state.get("username", ""),
                            color=ft.Colors.WHITE, size=15),
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN,
                            color=ft.Colors.WHITE, size=18)
                ]),
                items=[
                    ft.PopupMenuItem(
                        content=ft.Row(
                            [ft.Icon(ft.Icons.PERSON, size=18), ft.Text("Manage Account", size=14)]),
                        on_click=lambda e: handle_menu("account")
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row(
                            [ft.Icon(ft.Icons.PAYMENT, size=18), ft.Text("Payment", size=14)]),
                        on_click=lambda e: handle_menu("payment")
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row([ft.Icon(ft.Icons.SHOPPING_CART, size=18), ft.Text("Cart", size=14),
                                        ft.Container(
                                            ft.Text(str(cart_count)),
                                            bgcolor="#22c55e",
                                            border_radius=10,
                                            padding=ft.padding.symmetric(
                                                    horizontal=6, vertical=2),
                                            margin=ft.margin.only(left=8)
                                        ) if cart_count > 0 else ft.Container()
                                        ]),
                        on_click=lambda e: handle_menu("cart")
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row(
                            [ft.Icon(ft.Icons.HISTORY, size=18), ft.Text("Purchase History", size=14)]),
                        on_click=lambda e: handle_menu("history")
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row([ft.Icon(ft.Icons.LOGOUT, size=18, color="red"), ft.Text(
                            "Logout", size=14, color="red")]),
                        on_click=lambda e: handle_menu("logout")
                    ),
                ] + ([
                    ft.PopupMenuItem(
                        content=ft.Row([ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=18), ft.Text(
                            "Admin Panel", size=14)]),
                        on_click=lambda e: handle_menu("admin")
                    )
                ] if any(user["username"] == state.get("username", "") and user.get("role_id") == 1 for user in users_data) else [])
            ),
        ],
        spacing=10,  # Khoảng cách giữa search_box và username
        alignment=ft.MainAxisAlignment.END,  # Căn phải
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Sử dụng Row chính để chứa menu_items và right_section
    menu_content = ft.Row(
        controls=[
            ft.Row(
                menu_items,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                height=80,
            ),
            ft.Container(expand=True),  # Đẩy right_section về cuối
            right_section
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        height=80,
    )

    # Lưu reference đến search_results_container để có thể control từ on_search_change
    if "search_results_container" not in state:
        state["search_results_container"] = search_results_container

    return ft.Container(
        content=menu_content,
        bgcolor="#181f2a"
    )

def build_footer(set_terms, set_privacy, set_home, set_about_us=None, set_contact_us=None):
    # Social media icons
    socials = [
        {"icon": ft.Icons.FACEBOOK, "url": "#"},
        {"icon": ft.Icons.ALTERNATE_EMAIL, "url": "#"},
        {"icon": ft.Icons.PLAY_CIRCLE, "url": "#"},
        {"icon": ft.Icons.CAMERA_ALT, "url": "#"},
        {"icon": ft.Icons.BUSINESS_CENTER, "url": "#"},
    ]
    social_row = ft.Row([
        ft.IconButton(icon=s["icon"], icon_color="#b0b0b0", url=s["url"], tooltip=s["icon"].name, icon_size=28)
        for s in socials
    ], spacing=12)

    # Navigation links row 1
    nav_links_row1 = ft.Row([
        ft.TextButton("Home", style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=8), color="#b0b0b0", text_style=ft.TextStyle(size=15)), on_click=set_home),
        ft.TextButton("About us", style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=8), color="#b0b0b0", text_style=ft.TextStyle(size=15)), on_click=set_about_us if set_about_us else None),
        ft.TextButton("Contact", style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=8), color="#b0b0b0", text_style=ft.TextStyle(size=15)), on_click=set_contact_us if set_contact_us else None),
        ft.TextButton("Privacy policy", style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=8), color="#b0b0b0", text_style=ft.TextStyle(size=15)), on_click=set_privacy),
        ft.TextButton("Terms of use", style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=8), color="#b0b0b0", text_style=ft.TextStyle(size=15)), on_click=set_terms),
    ], spacing=10)

    # Main footer content with 3 sections
    footer_content = ft.Row([
        # Section 1: Logo (lớn hơn) - dịch sang phải
        ft.Container(
            ft.Image(src="gamehub-dev/src/data/images/Logo_game_rmb.png", width=150, height=150),
            alignment=ft.alignment.center,
            padding=ft.padding.only(left=20)
        ),
        
        # Section 2: GameHub and description - dịch sang phải
        ft.Container(
            ft.Column([
                ft.Text("GameHub", size=24, weight=ft.FontWeight.BOLD, color="#7fff00"),
                ft.Text(
                    "GameHub is your go-to platform for discovering the latest Vietnamese-localized PC games with high-speed downloads and no cost at all. At GameHub, we bring you the newest translated PC game titles along with fast and completely free download links.",
                    size=14, color="#b0b0b0", width=400
                ),
            ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.START, spacing=8),
            expand=True,
            padding=ft.padding.only(left=40)
        ),
        
        # Section 3: Navigation and social links - dịch sang trái
        ft.Container(
            ft.Column([
                # Row 1: Navigation links
                nav_links_row1,
                ft.Container(height=12),
                # Row 2: Social media icons
                social_row,
            ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.START),
            padding=ft.padding.only(right=20)
        ),
    ], alignment=ft.MainAxisAlignment.START, spacing=20)

    # Copyright row (căn giữa)
    copyright_row = ft.Row([
        ft.Container(expand=True),
        ft.Text("Copyright © 2024 GameHub", size=15, color="#b0b0b0", weight=ft.FontWeight.BOLD),
        ft.Container(expand=True)
    ], alignment=ft.MainAxisAlignment.CENTER)

    return ft.Container(
        ft.Column([
            ft.Divider(height=2, color="#333"),
            footer_content,
            ft.Container(height=16),
            copyright_row
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
        padding=ft.padding.only(top=24, bottom=40),
        bgcolor="#181f2a"
    )


def HomeScreen(page, state, render):
    # Định nghĩa callback TRƯỚC

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

    def on_search_change(e):
        keyword = e.control.value
        if not keyword:
            search_results_column.controls.clear()
            search_results_container.visible = False
            page.update()
            return

        try:
            response = requests.get(
                f"http://127.0.0.1:5000/api/search?q={keyword}")
            data = response.json()

            search_results_column.controls.clear()
            if not data["games"]:
                search_results_column.controls.append(
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
                        state["selected_game"] = {"id": game_data["id"]}
                        state["screen"] = "game_detail"
                        # Ẩn search results
                        search_results_column.controls.clear()
                        search_results_container.visible = False
                        render()
                    
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
                                            width=350  # Tăng width để text dài hơn theo dropdown
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
                        bgcolor="#2a3441" if i == 3 else "transparent",  # Highlight item thứ 4 như trong hình
                        border_radius=5,
                        on_hover=lambda e, idx=i: on_search_item_hover(e, idx),
                        on_click=lambda e, game_data=game: open_search_game_detail(e, game_data),
                        key=f"search_item_{i}",  # Thêm key để có thể update
                        width=480  # Tăng width của item để phù hợp với dropdown rộng hơn
                    )
                    search_results_column.controls.append(game_item)
            search_results_container.visible = True
            page.update()
        except Exception as ex:
            print("Search error:", ex)
            # Show dropdown even when API fails for UI testing
            search_results_column.controls.clear()
            search_results_column.controls.append(
                ft.Container(
                    ft.Text("Server not available", color=ft.Colors.GREY, size=14),
                    padding=ft.padding.all(10)
                )
            )
            search_results_container.visible = True
            page.update()

    def on_search_item_hover(e, idx):
        # Xử lý hover effect cho search items
        if e.data == "true":
            # Hover in
            e.control.bgcolor = "#2a3441"
        else:
            # Hover out
            e.control.bgcolor = "transparent"
        page.update()

    def clear_search(e):
        # Clear search box và ẩn results
        search_results_column.controls.clear()
        search_results_container.visible = False
        page.update()

    def set_home(e=None):
        # Force clear page để HomeScreen được khởi tạo lại
        page.controls.clear()
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
        elif action == "admin":
            state["screen"] = "admin"
            render()
        elif action == "allgame":
            state["screen"] = "allgame"
            render()
        elif action == "ai_chat":
            state["screen"] = "ai_chat"
            render()

    global menu_row
    if "banner_idx" not in state:
        state["banner_idx"] = 0

    # Đảm bảo các biến page được khởi tạo trong state
    if "top_picks_page" not in state:
        state["top_picks_page"] = 0
    if "just_for_you_page" not in state:
        state["just_for_you_page"] = 0
    if "players_like_you_page" not in state:
        state["players_like_you_page"] = 0

    # Đảm bảo các biến phân trang đặc biệt được khởi tạo
    if "top_rated_games" not in state:
        state["top_rated_games"] = 0
    if "top_paid_page" not in state:
        state["top_paid_page"] = 0
    if "top_free_page" not in state:
        state["top_free_page"] = 0

    def open_link(url):
        webbrowser.open(url)

    # Hàm để tùy chỉnh ID game cho banner
    def get_banner_game_ids():
        """Trả về danh sách 4 ID game cho banner - TÙY CHỈNH Ở ĐÂY"""
        # Thay đổi các ID này theo ý muốn
        return [2277012, 2277013, 2277014, 2277015]  # Ví dụ: 4 game cụ thể
    
    # Lấy banner games theo ID tùy chỉnh
    banner_game_ids = get_banner_game_ids()
    banner_result = get_custom_banner_games(banner_game_ids)
    if not banner_result["success"]:
        print("Error getting banner games:", banner_result["error"])
        banner_games = []
    else:
        banner_games = banner_result["games"]
    
    def get_banner_content():
        if not banner_games:
            # Fallback nếu không có dữ liệu từ database
            return ft.GestureDetector(
                content=ft.Stack(
                    [
                        ft.Image(
                            src="gamehub-dev/src/data/images/Logo_game_rmb.png", # Fallback image
                            width=1200,
                            height=520,
                            fit=ft.ImageFit.COVER,
                            border_radius=28,
                        ),
                        ft.Container(
                            ft.Text(
                                "GameHub Banner", # Fallback title
                                size=44,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            left=56,
                            bottom=56,
                            alignment=ft.alignment.bottom_left,
                        ),
                    ],
                    width=1200,
                    height=520,
                ),
                on_tap=lambda e: None
            )
        
        banner = banner_games[state["banner_idx"]]

        def open_banner_game_detail(e):
            state["selected_game"] = {"id": banner["id"]}
            state["screen"] = "game_detail"
            render()

        return ft.GestureDetector(
            content=ft.Stack(
                [
                    ft.Image(
                        src=banner["image_url_horizontal"] or banner["image_url_vertical"] or "",
                        width=1200,
                        height=520,
                        fit=ft.ImageFit.COVER,
                        border_radius=28,
                    ),
                    ft.Container(
                        ft.Text(
                            banner["title"],
                            size=44,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        left=56,
                        bottom=56,
                        alignment=ft.alignment.bottom_left,
                    ),
                ],
                width=1200,
                height=520,
            ),
            on_tap=open_banner_game_detail
        )

    # AnimatedSwitcher cho hiệu ứng chuyển mượt
    if "switcher" not in state:
        state["switcher"] = ft.AnimatedSwitcher(
            content=get_banner_content(),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=500,
        )
    switcher = state["switcher"]

    def prev_banner(e=None):
        if "banner_idx" not in state:
            state["banner_idx"] = 0
        # Sử dụng len(banner_games) nếu có dữ liệu,否则 fallback về 1
        banner_count = len(banner_games) if banner_games else 1
        state["banner_idx"] = (state["banner_idx"] - 1) % banner_count
        switcher.content = get_banner_content()
        page.update()

    def next_banner(e=None):
        if "banner_idx" not in state:
            state["banner_idx"] = 0
        # Sử dụng len(banner_games) nếu có dữ liệu,否则 fallback về 1
        banner_count = len(banner_games) if banner_games else 1
        state["banner_idx"] = (state["banner_idx"] + 1) % banner_count
        switcher.content = get_banner_content()
        page.update()

    # Auto chuyển banner sau mỗi 4 giây
    async def auto_next_banner():
        while True:
            await asyncio.sleep(4)
            if "banner_idx" not in state:
                state["banner_idx"] = 0
            next_banner()
    if not state.get("auto_banner_started"):
        page.run_task(auto_next_banner)
        state["auto_banner_started"] = True

    # --- GAME LISTS ---
    def game_card(game):
        def open_game_detail(e):
            state["selected_game"] = game
            state["screen"] = "game_detail"
            render()

        def on_hover(e):
            container.border = ft.border.all(
                2, "#ffffff") if e.data == "true" else None
            container.bgcolor = "#2a3441" if e.data == "true" else "#232b39"
            page.update()

        # Xử lý dữ liệu từ recommendation hoặc dữ liệu cũ
        game_name = game.get("name", game.get("title", "Unknown Game"))
        game_image = game.get("image", "https://cdn.cloudflare.steamstatic.com/steam/apps/default/header.jpg")
        game_categories = game.get("categories", "Action, Adventure")
        game_old_price = game.get("old_price", 29.99)
        game_price = game.get("price", 19.99)
        game_discount = game.get("discount", 33)

        # Tất cả card có kích thước cố định để đảm bảo cân đối

        container = ft.Container(
            content=ft.Column([
                # Phần hình ảnh - chiều cao cố định
                ft.GestureDetector(
                    content=ft.Image(
                        src=game_image, width=160, height=180, fit=ft.ImageFit.COVER, border_radius=10),
                    on_tap=open_game_detail
                ),
                # Phần title - chiều cao cố định
                ft.GestureDetector(
                    content=ft.Container(
                        ft.Text(game_name, size=15, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        height=40  # Chiều cao cố định cho title
                    ),
                    on_tap=open_game_detail
                ),
                # Phần categories - chiều cao cố định
                ft.Container(
                    ft.Text(game_categories, size=12, color="#b0b0b0", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    height=16  # Chiều cao cố định cho categories
                ),
                # Phần giá - chiều cao cố định
                ft.Container(
                    ft.Row([
                        ft.Text(f"${game_old_price:.2f}", size=12, color="#b0b0b0", style=ft.TextStyle(
                            decoration=ft.TextDecoration.LINE_THROUGH)),
                        ft.Container(
                            ft.Text(f"-{game_discount}%",
                                    size=12, color="white"),
                            bgcolor="#e74c3c",
                            border_radius=5,
                            padding=ft.padding.symmetric(horizontal=4, vertical=1),
                            margin=ft.margin.only(left=4)
                        ),
                        ft.Container(
                            ft.Text(f"${game_price:.2f}", size=14,
                                    weight=ft.FontWeight.BOLD, color="#2ecc40"),
                            margin=ft.margin.only(left=8)
                        ),
                    ], alignment=ft.MainAxisAlignment.START, spacing=4),
                    height=20  # Chiều cao cố định cho phần giá
                ),
            ], spacing=2, alignment=ft.MainAxisAlignment.START),  # Spacing nhỏ và cố định
            width=160,
            height=280,  # Chiều cao tổng thể cố định
            padding=ft.padding.all(8),
            bgcolor="#232b39",
            border_radius=10,
            margin=ft.margin.only(right=14, bottom=12),  # Căn chỉnh margin với top_rated_card
            on_hover=on_hover,
        )
        return container

    # --- TOP RATED CARD ---
    def top_rated_card(game):
        # Debug: In ra thông tin game
        print(f"Creating top_rated_card for: ID={game.get('id')}, Title={game.get('title')}")
        
        def open_game_detail(e):
            state["selected_game"] = game
            state["screen"] = "game_detail"
            render()

        def on_hover(e):
            container.border = ft.border.all(
                2, "#ffffff") if e.data == "true" else None
            container.bgcolor = "#2a3441" if e.data == "true" else "#232b39"
            page.update()

        # Tính toán số dòng của title để điều chỉnh kích thước hình ảnh
        title = game["title"]
        title_lines = len(title.split('\n')) if '\n' in title else 1
        if len(title) > 30:  # Ước tính nếu title dài hơn 30 ký tự thì có thể 2 dòng
            title_lines = 2
        
        # Điều chỉnh chiều cao hình ảnh dựa trên số dòng title
        image_height = 160 if title_lines == 1 else 140  # Hình ảnh cao hơn nếu title 1 dòng
        title_height = 50 if title_lines == 2 else 40  # Tăng chiều cao title nếu 2 dòng
        
        container = ft.Container(
            content=ft.Stack([
                ft.Column([
                    ft.GestureDetector(
                        content=ft.Image(
                            src=game.get("image_url_horizontal") or game.get("image_url_vertical"),
                            width=300,
                            height=image_height,
                            fit=ft.ImageFit.COVER,
                            border_radius=10
                        ),
                        on_tap=open_game_detail
                    ),
                    ft.GestureDetector(
                        content=ft.Container(
                            ft.Text(
                                game["title"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            padding=ft.padding.only(top=7, left=9, right=9),
                            height=title_height
                        ),
                        on_tap=open_game_detail
                    ),
                    ft.Container(expand=True),  # Đẩy button xuống dưới cùng
                    ft.Container(
                        ft.Row([
                            ft.ElevatedButton(
                                "See more",
                                bgcolor="#22c55e",
                                color=ft.Colors.WHITE,
                                height=28,
                                width=90,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)),
                                on_click=open_game_detail
                            ),
                            ft.Container(expand=True),
                                                        ft.Row([
                                ft.Text(
                                    f"${float(game.get('price_original', 0)):.2f}",
                                    size=12,
                                    color="#b0b0b0",
                                    style=ft.TextStyle(
                                        decoration=ft.TextDecoration.LINE_THROUGH
                                    )
                                ) if game.get("price_original", 0) > 0 and game.get("price_original", 0) != game.get("price", 0) else ft.Container(),
                                ft.Container(
                                    ft.Text(f"-{game.get('discount_percentage', 0)}%",
                                            size=12, color="white"),
                                    bgcolor="#e74c3c",
                                    border_radius=5,
                                    padding=ft.padding.symmetric(horizontal=4, vertical=1),
                                    margin=ft.margin.only(left=4)
                                ) if game.get("discount_percentage", 0) > 0 else ft.Container(),
                                ft.Text(
                                    "Free" if (game.get("price", 0) == 0) else f"${float(game.get('price', 0)):.2f}",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#2ecc40" if (game.get("price", 0) == 0) else "#22c55e"
                                ),
                            ], spacing=4, alignment=ft.MainAxisAlignment.END),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=ft.padding.only(left=9, right=9, bottom=7),
                        height=42
                    ),
                ], spacing=0, alignment=ft.MainAxisAlignment.START),
            ]),
            width=300,
            height=242,
            bgcolor="#232b39",
            border_radius=10,
            margin=ft.margin.only(right=14, bottom=12),
            on_hover=on_hover,
        )

        return container

    # --- PAID GAME CARD ---

    def paid_game_card(game):
        def open_game_detail(e):
            state["selected_game"] = game
            state["screen"] = "game_detail"
            render()

        def on_hover(e):
            container.border = ft.border.all(
                2, "#ffffff") if e.data == "true" else None
            container.bgcolor = "#2a3441" if e.data == "true" else "#232b39"
            page.update()

        price = game.get('price', 0)
        price_display = "Free" if (price == 0) else f"${float(price):.2f}"
        price_color = "#2ecc40" if (price == 0) else "#22c55e"
        
        # Tính toán số dòng của title để điều chỉnh kích thước hình ảnh
        title = game["title"]
        title_lines = len(title.split('\n')) if '\n' in title else 1
        if len(title) > 30:  # Ước tính nếu title dài hơn 30 ký tự thì có thể 2 dòng
            title_lines = 2
        
        # Điều chỉnh chiều cao hình ảnh dựa trên số dòng title
        image_height = 160 if title_lines == 1 else 140  # Hình ảnh cao hơn nếu title 1 dòng
        title_height = 50 if title_lines == 2 else 40  # Tăng chiều cao title nếu 2 dòng
        
        container = ft.Container(
            content=ft.Stack([
                ft.Column([
                    ft.GestureDetector(
                        content=ft.Image(
                            src=game.get("image_url_horizontal") or game.get("image_url_vertical"),
                            width=300,
                            height=image_height,
                            fit=ft.ImageFit.COVER,
                            border_radius=10
                        ),
                        on_tap=open_game_detail
                    ),
                    ft.GestureDetector(
                        content=ft.Container(
                            ft.Text(
                                game["title"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            padding=ft.padding.only(top=7, left=9, right=9),
                            height=title_height
                        ),
                        on_tap=open_game_detail
                    ),
                    ft.Container(expand=True),  # Đẩy button xuống dưới cùng
                    ft.Container(
                        ft.Row([
                            ft.ElevatedButton(
                                "See more",
                                bgcolor="#22c55e",
                                color=ft.Colors.WHITE,
                                height=28,
                                width=90,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)),
                                on_click=open_game_detail
                            ),
                            ft.Container(expand=True),
                            ft.Row([
                                ft.Text(
                                    f"${float(game.get('price_original', 0)):.2f}",
                                    size=12,
                                    color="#b0b0b0",
                                    style=ft.TextStyle(
                                        decoration=ft.TextDecoration.LINE_THROUGH
                                    )
                                ) if game.get("price_original", 0) > 0 and game.get("price_original", 0) != game.get("price", 0) else ft.Container(),
                                ft.Container(
                                    ft.Text(f"-{game.get('discount_percentage', 0)}%",
                                            size=12, color="white"),
                                    bgcolor="#e74c3c",
                                    border_radius=5,
                                    padding=ft.padding.symmetric(horizontal=4, vertical=1),
                                    margin=ft.margin.only(left=4)
                                ) if game.get("discount_percentage", 0) > 0 else ft.Container(),
                                ft.Text(
                                    price_display,
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=price_color
                                ),
                            ], spacing=4, alignment=ft.MainAxisAlignment.END),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=ft.padding.only(left=9, right=9, bottom=7),
                        height=42
                    ),
                ], spacing=0, alignment=ft.MainAxisAlignment.START),
            ]),
            width=300,
            height=242,
            bgcolor="#232b39",
            border_radius=10,
            margin=ft.margin.only(right=14, bottom=12),
            on_hover=on_hover,
        )

        return container

    # --- FREE GAME CARD ---

    def free_game_card(game):
        def open_game_detail(e):
            state["selected_game"] = game
            state["screen"] = "game_detail"
            render()

        def on_hover(e):
            container.border = ft.border.all(
                2, "#ffffff") if e.data == "true" else None
            container.bgcolor = "#2a3441" if e.data == "true" else "#232b39"
            page.update()

        # Tính toán số dòng của title để điều chỉnh kích thước hình ảnh
        title = game["title"]
        title_lines = len(title.split('\n')) if '\n' in title else 1
        if len(title) > 30:  # Ước tính nếu title dài hơn 30 ký tự thì có thể 2 dòng
            title_lines = 2
        
        # Điều chỉnh chiều cao hình ảnh dựa trên số dòng title
        image_height = 160 if title_lines == 1 else 140  # Hình ảnh cao hơn nếu title 1 dòng
        title_height = 50 if title_lines == 2 else 40  # Tăng chiều cao title nếu 2 dòng

        container = ft.Container(
            content=ft.Stack([
                ft.Column([
                    ft.GestureDetector(
                        content=ft.Image(
                            src=game.get("image_url_horizontal") or game.get("image_url_vertical"),
                            width=300,
                            height=image_height,
                            fit=ft.ImageFit.COVER,
                            border_radius=10
                        ),
                        on_tap=open_game_detail
                    ),
                    ft.GestureDetector(
                        content=ft.Container(
                            ft.Text(
                                game["title"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            padding=ft.padding.only(top=7, left=9, right=9),
                            height=title_height
                        ),
                        on_tap=open_game_detail
                    ),
                    ft.Container(expand=True),  # Đẩy button xuống dưới cùng
                    ft.Container(
                        ft.Row([
                            ft.ElevatedButton(
                                "See more",
                                bgcolor="#22c55e",
                                color=ft.Colors.WHITE,
                                height=28,
                                width=90,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)),
                                on_click=open_game_detail
                            ),
                            ft.Container(expand=True),
                            ft.Row([
                                ft.Text(
                                    f"${float(game.get('price_original', 0)):.2f}",
                                    size=12,
                                    color="#b0b0b0",
                                    style=ft.TextStyle(
                                        decoration=ft.TextDecoration.LINE_THROUGH
                                    )
                                ) if game.get("price_original", 0) > 0 and game.get("price_original", 0) != game.get("price", 0) else ft.Container(),
                                ft.Container(
                                    ft.Text(f"-{game.get('discount_percentage', 0)}%",
                                            size=12, color="white"),
                                    bgcolor="#e74c3c",
                                    border_radius=5,
                                    padding=ft.padding.symmetric(horizontal=4, vertical=1),
                                    margin=ft.margin.only(left=4)
                                ) if game.get("discount_percentage", 0) > 0 else ft.Container(),
                                ft.Text(
                                    "Free",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#2ecc40"
                                ),
                            ], spacing=4, alignment=ft.MainAxisAlignment.END),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=ft.padding.only(left=9, right=9, bottom=7),
                        height=42
                    ),
                ], spacing=0, alignment=ft.MainAxisAlignment.START),
            ]),
            width=300,
            height=242,
            bgcolor="#232b39",
            border_radius=10,
            margin=ft.margin.only(right=14, bottom=12),
            on_hover=on_hover,
        )
        return container

    # Sửa hàm render_game_list để chỉ cập nhật nội dung AnimatedSwitcher
    def render_game_list(title, games, page_key):
        page_idx = state.get(page_key, 0)
        per_page = 9  # Hiển thị 9 games thay vì 10
        total_pages = (len(games) + per_page - 1) // per_page  # Sửa công thức tính total_pages

        def next_page(e):
            if state[page_key] < total_pages - 1:
                state[page_key] += 1
            else:
                state[page_key] = 0
            switcher_key = f"{page_key}_{state[page_key]}"
            state[f"{page_key}_switcher"].content = ft.Row(
                [game_card(game) for game in games[state[page_key]
                                                   * per_page:(state[page_key] + 1) * per_page]],
                spacing=4,
                expand=True,
                key=switcher_key
            )
            page.update()  # Chỉ cập nhật page, không render lại toàn bộ

        start = page_idx * per_page
        end = start + per_page
        page_games = games[start:end]

        switcher_key = f"{page_key}_{page_idx}"
        # Lưu AnimatedSwitcher vào state để tái sử dụng
        if f"{page_key}_switcher" not in state:
            state[f"{page_key}_switcher"] = ft.AnimatedSwitcher(
                content=ft.Container(
                    content=ft.Row([game_card(game) for game in page_games],
                                   spacing=12, key=switcher_key),
                    width=1600,  # Width cố định để căn chỉnh với Top rated
                    alignment=ft.alignment.center_left
                ),  # Container với width cố định
                transition=ft.AnimatedSwitcherTransition.FADE,
                duration=800
            )

        return ft.Column([
            ft.Row([
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    icon_color="#22c55e",
                    on_click=next_page,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            state[f"{page_key}_switcher"],
            ft.Container(height=18)
        ], alignment=ft.MainAxisAlignment.START)

    # Hàm phân trang cho các list đặc biệt
    def render_paged_list(title, games, page_key, card_fn, per_page=4):
        if page_key not in state:
            state[page_key] = 0
        page_idx = state.get(page_key, 0)
        total_pages = (len(games) - 1) // per_page + 1
        
        # Debug: In ra thông tin về games
        print(f"render_paged_list - {title}: {len(games)} games, page {page_idx + 1}/{total_pages}")
        if len(games) > 0:
            print(f"  First game: ID={games[0].get('id')}, Title={games[0].get('title')}")

        def next_page(e):
            if state[page_key] < total_pages - 1:
                state[page_key] += 1
            else:
                state[page_key] = 0
            switcher_key = f"{page_key}_{state[page_key]}"
            current_page_games = games[state[page_key] * per_page:(state[page_key] + 1) * per_page]
            print(f"  Next page: showing {len(current_page_games)} games")
            state[f"{page_key}_switcher"].content = ft.Container(
                content=ft.Row(
                    [card_fn(game) for game in current_page_games],
                    spacing=12,  # Giữ spacing cố định
                    key=switcher_key
                ),
                width=1600,  # Width cố định để căn chỉnh với Top rated
                alignment=ft.alignment.center_left
            )
            page.update()

        start = page_idx * per_page
        end = start + per_page
        page_games = games[start:end]
        switcher_key = f"{page_key}_{page_idx}"
        if f"{page_key}_switcher" not in state:
            state[f"{page_key}_switcher"] = ft.AnimatedSwitcher(
                content=ft.Container(
                    content=ft.Row([card_fn(game) for game in page_games],
                                   spacing=12, key=switcher_key),
                    width=1600,  # Width cố định để căn chỉnh với Top rated
                    alignment=ft.alignment.center_left
                ),  # Container với width cố định
                transition=ft.AnimatedSwitcherTransition.FADE,
                duration=800
            )
        return ft.Column([
            ft.Row([
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    icon_color="#22c55e",
                    on_click=next_page,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            state[f"{page_key}_switcher"],
            ft.Container(height=18)
        ], alignment=ft.MainAxisAlignment.START)

    # Lấy dữ liệu recommendation cho user hiện tại
    # Get user_id from login information
    current_user_id = 1  # Default is 1, will be changed based on logged in user
    
    # Find user_id based on logged in username
    username = state.get("username", "")
    for user in users_data:
        if user["username"] == username:
            # Use fixed ID from users_data
            current_user_id = user["id"]
            break
    else:
        current_user_id = 1
    
    def convert_recommendation_to_ui_format(recommendation_df):
        """Chuyển đổi DataFrame recommendation thành format phù hợp với UI"""
        if recommendation_df.empty:
            return []
        
        # Lấy danh sách game_ids từ recommendation_df
        game_ids = recommendation_df['id'].tolist()
        
        # Lấy thông tin chi tiết từ database
        game_details = get_game_details_by_ids(game_ids)
        
        ui_games = []
        for _, row in recommendation_df.iterrows():
            game_id = row['id']
            score = row['score']
            
            # Tìm thông tin chi tiết tương ứng
            game_detail = next((g for g in game_details if g['id'] == game_id), None)
            
            if game_detail:
                game = {
                    "id": game_detail['id'],
                    "name": game_detail['title'],
                    "image": game_detail['image_url_vertical'] or "https://cdn.cloudflare.steamstatic.com/steam/apps/default/header.jpg",
                    "categories": game_detail.get('categories', 'Action, Adventure'),
                    "old_price": game_detail['price_original'] or game_detail['price'],
                    "price": game_detail['price'],
                    "discount": game_detail['discount_percentage'],
                    "score": score
                }
            else:
                # Fallback nếu không tìm thấy thông tin chi tiết
                game = {
                    "id": game_id,
                    "name": f"Game {game_id}",
                    "image": "https://cdn.cloudflare.steamstatic.com/steam/apps/default/header.jpg",
                    "categories": "Action, Adventure",
                    "old_price": 29.99,
                    "price": 19.99,
                    "discount": 33,
                    "score": score
                }
            ui_games.append(game)
        return ui_games
    
    try:
        # Lấy tfidf_df và item_sim_df từ recommendation module
        tfidf_df, item_sim_df = get_trained_models()
        
        # Thử lấy dữ liệu từ database
        train_df, games_df_recommendation = fetch_data_from_db()
        
        if train_df is not None and games_df_recommendation is not None:
            # Get content-based recommendations
            content_based_df = get_content_based(current_user_id, train_df, tfidf_df, games_df_recommendation, k=15)
            content_based_games = convert_recommendation_to_ui_format(content_based_df)
            
            # Get collaborative filtering recommendations  
            collaborative_df = get_item_based_cf(current_user_id, train_df, item_sim_df, games_df_recommendation, k=15)
            collaborative_games = convert_recommendation_to_ui_format(collaborative_df)
            
            # Get hybrid recommendations
            hybrid_df = get_hybrid(current_user_id, train_df, tfidf_df, item_sim_df, games_df_recommendation, k=15)
            hybrid_games = convert_recommendation_to_ui_format(hybrid_df)
        else:
            print("Cannot connect to database, using sample data")
            # Use sample data from recommendation.py
            train_df, games_df = initialize_recommendation_data()
            content_based_games = convert_recommendation_to_ui_format(
                get_content_based(current_user_id, train_df, tfidf_df, games_df, k=15)
            )
            collaborative_games = convert_recommendation_to_ui_format(
                get_item_based_cf(current_user_id, train_df, item_sim_df, games_df, k=15)
            )
            hybrid_games = convert_recommendation_to_ui_format(
                get_hybrid(current_user_id, train_df, tfidf_df, item_sim_df, games_df, k=15)
            )
    except Exception as e:
        print(f"Error getting recommendation data: {e}")
        # Use sample data if error occurs
        tfidf_df, item_sim_df = get_trained_models()
        train_df, games_df = initialize_recommendation_data()
        content_based_games = convert_recommendation_to_ui_format(
            get_content_based(current_user_id, train_df, tfidf_df, games_df, k=15)
        )
        collaborative_games = convert_recommendation_to_ui_format(
            get_item_based_cf(current_user_id, train_df, item_sim_df, games_df, k=15)
        )
        hybrid_games = convert_recommendation_to_ui_format(
            get_hybrid(current_user_id, train_df, tfidf_df, item_sim_df, games_df, k=15)
        )

    # Get top_rated_games data
    result = get_top_rated_games()
    if not result["success"]:
        print("Error getting top rated games:", result["error"])
        top_rated_games = []
    else:
        # Loại bỏ duplicate games dựa trên ID
        seen_ids = set()
        top_rated_games = []
        for game in result["games"]:
            if game["id"] not in seen_ids:
                seen_ids.add(game["id"])
                top_rated_games.append(game)
        
        # Debug: In ra thông tin games để kiểm tra
        print(f"Top rated games count: {len(top_rated_games)}")
        for i, game in enumerate(top_rated_games[:5]):  # Chỉ in 5 game đầu
            print(f"  {i+1}. ID: {game.get('id')}, Title: {game.get('title')}")

    # Get top_paid_games data
    result_paid = get_top_paid_games()
    if not result_paid["success"]:
        print("Error getting top paid games:", result_paid["error"])
        top_paid_games = []
    else:
        # Loại bỏ duplicate games dựa trên ID
        seen_ids = set()
        top_paid_games = []
        for game in result_paid["games"]:
            if game["id"] not in seen_ids:
                seen_ids.add(game["id"])
                top_paid_games.append(game)
        
        # Debug: In ra thông tin games để kiểm tra
        print(f"Top paid games count: {len(top_paid_games)}")
        for i, game in enumerate(top_paid_games[:5]):  # Chỉ in 5 game đầu
            print(f"  {i+1}. ID: {game.get('id')}, Title: {game.get('title')}")

    # Get top_free_games data
    result_paid = get_top_free_games()
    if not result_paid["success"]:
        print("Error getting top free games:", result_paid["error"])
        top_free_games = []
    else:
        # Loại bỏ duplicate games dựa trên ID
        seen_ids = set()
        top_free_games = []
        for game in result_paid["games"]:
            if game["id"] not in seen_ids:
                seen_ids.add(game["id"])
                top_free_games.append(game)
        
        # Debug: In ra thông tin games để kiểm tra
        print(f"Top free games count: {len(top_free_games)}")
        for i, game in enumerate(top_free_games[:5]):  # Chỉ in 5 game đầu
            print(f"  {i+1}. ID: {game.get('id')}, Title: {game.get('title')}")

    # Wrap content below menu in scrollable Column
    banner_row = ft.Row(
        [
            ft.IconButton(
                icon=ft.Icons.ARROW_LEFT,
                icon_color="white",
                icon_size=56,
                style=ft.ButtonStyle(
                    bgcolor="#232b39", shape=ft.RoundedRectangleBorder(radius=18)),
                on_click=prev_banner,
            ),
            switcher,
            ft.IconButton(
                icon=ft.Icons.ARROW_RIGHT,
                icon_color="white",
                icon_size=56,
                style=ft.ButtonStyle(
                    bgcolor="#232b39", shape=ft.RoundedRectangleBorder(radius=18)),
                on_click=next_banner,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=40,
    )
    scrollable_content = ft.Column(
        [
            ft.Container(height=30),
            ft.Container(
                banner_row, alignment=ft.alignment.center, padding=20),
            ft.Container(
                ft.Column([
                    render_game_list("Games You May Like",
                                     content_based_games, "top_picks_page"),
                    render_game_list(
                        "Players Also Enjoyed", collaborative_games, "just_for_you_page"),
                    render_game_list(
                        "Smart Picks For You", hybrid_games, "players_like_you_page"),
                                         render_paged_list(
                         "Top rated !!!", top_rated_games, "top_rated_page", top_rated_card, per_page=5),
                     render_paged_list(
                         "Top paid game", top_paid_games, "top_paid_page", paid_game_card, per_page=5),
                     render_paged_list(
                         "Top free game", top_free_games, "top_free_page", free_game_card, per_page=5),
                ], alignment=ft.MainAxisAlignment.START),
                alignment=ft.alignment.center,
                padding=ft.padding.symmetric(horizontal=40, vertical=10),
                expand=True
            ),
            build_footer(set_terms, set_privacy, set_home, set_about_us, set_contact_us)
        ],
        expand=True,
        scroll="auto"
    )

    menu_row = build_menu_row(state, render, set_home,
                              handle_menu, on_search_change, search_results_container, set_about_us, set_contact_us, clear_search)

    # Tạo Stack để search results có thể đè lên banner nhưng vẫn cho phép scroll
    main_stack = ft.Stack(
        controls=[
            scrollable_content,
            search_results_container
        ],
        expand=True
    )

    page.add(
        menu_row,   
        main_stack
    )

    page.update()


__all__ = ["set_terms", "set_privacy", "set_home",
           "build_menu_row", "build_footer", "handle_menu"]
