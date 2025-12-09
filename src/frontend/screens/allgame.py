import flet as ft
import requests
from datetime import datetime

def allgame_screen(page, state, render):
    from .home import build_menu_row, build_footer
    
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
        elif action == "admin":
            state["screen"] = "admin"
            render()

    # Search functionality - similar to AI Chat
    def on_search_change(e):
        keyword = e.control.value
        if not keyword:
            search_results_container.content.controls.clear()
            search_results_container.visible = False
            page.update()
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
                        state["selected_game"] = {"id": game_data["id"]}
                        state["screen"] = "game_detail"
                        # Ẩn search results
                        search_results_container.content.controls.clear()
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
            page.update()
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
        search_results_container.content.controls.clear()
        search_results_container.visible = False
        page.update()
    
    def clear_search_and_update(e):
        # Clear search trong allgame và cập nhật display
        state["allgame_search"] = ""
        state["allgame_page"] = 1
        # Clear text trong search field
        search_bar = filter_dropdowns.controls[0].controls[1]
        if isinstance(search_bar, ft.TextField):
            search_bar.value = ""
        load_games()
        update_games_display()

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
        margin=ft.margin.only(top=0, left=1320),  # Điều chỉnh position để căn với search box
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
        visible=False,
        top=60  # Position relative to header
    )

    # Khởi tạo state cho allgame
    if "allgame_page" not in state:
        state["allgame_page"] = 1
    if "allgame_per_page" not in state:
        state["allgame_per_page"] = 16  # 16 game mỗi trang
    if "allgame_filters" not in state:
        state["allgame_filters"] = {}
    if "allgame_games" not in state:
        state["allgame_games"] = []
    if "allgame_total" not in state:
        state["allgame_total"] = 0
    if "allgame_total_pages" not in state:
        state["allgame_total_pages"] = 0
    if "filter_options" not in state:
        state["filter_options"] = {}
    if "allgame_search" not in state:
        state["allgame_search"] = ""

    def load_filter_options():
        try:
            response = requests.get("http://127.0.0.1:5000/api/filter-options")
            print(f"API /api/filter-options response: {response.status_code}, {response.json()}")  # Debug
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    state["filter_options"] = data["filters"]
                    return True
                else:
                    print(f"Filter options error: {data.get('error')}")
            else:
                print(f"Filter options request failed with status: {response.status_code}")
        except Exception as e:
            print(f"Error loading filter options: {e}")
        return False

    def load_games():
        try:
            params = {
                "page": state["allgame_page"],
                "per_page": state["allgame_per_page"]
            }
            
            # Chỉ thêm filter vào params nếu có giá trị và không phải "- All -"
            active_filters = {}
            for key, value in state["allgame_filters"].items():
                if value and value != "- All -":
                    params[key] = value
                    active_filters[key] = value
            
            if state["allgame_search"]:
                params["title_contains"] = state["allgame_search"]
            
            print(f"Active filters: {active_filters}")  # Debug
            print(f"Calling API with params: {params}")  # Debug
            
            response = requests.get("http://127.0.0.1:5000/api/allgames", params=params)
            print(f"API response: {response.status_code}, {response.json()}")  # Debug
            if response.status_code == 200:
                data = response.json()
                print(f"API data: {data}")  # Debug
                if data["success"]:
                    # Lấy dữ liệu từ API
                    state["allgame_games"] = data["games"]
                    state["allgame_total"] = data["total"]
                    state["allgame_total_pages"] = data["total_pages"]
                    # Lọc client-side nếu có từ khóa tìm kiếm
                    if state["allgame_search"]:
                        search_term = state["allgame_search"].lower()
                        state["allgame_games"] = [game for game in state["allgame_games"] if search_term in game.get("title", "").lower()]
                        # Cập nhật total và total_pages dựa trên kết quả lọc cho trang hiện tại
                        state["allgame_total"] = len(state["allgame_games"])
                        state["allgame_total_pages"] = 1  # Chỉ có 1 trang dựa trên kết quả lọc của trang hiện tại
                    print(f"Loaded {len(state['allgame_games'])} games after filtering")  # Debug
                    return True
                else:
                    print(f"API error: {data.get('error')}")
            else:
                print(f"API request failed with status: {response.status_code}")
        except Exception as e:
            print(f"Error loading games: {e}")
        return False

    def create_filter_dropdown(label, options, filter_key):
        # Đảm bảo giá trị mặc định là "- All -" nếu không có filter
        current_value = state["allgame_filters"].get(filter_key, "- All -")
        if current_value == "- Tất cả -":  # Xử lý trường hợp cũ
            current_value = "- All -"
        
        def on_filter_change(e):
            selected_value = e.control.value
            if selected_value == "- All -":
                # Nếu chọn "- All -" thì xóa filter đó khỏi state
                if filter_key in state["allgame_filters"]:
                    del state["allgame_filters"][filter_key]
                    print(f"Removed filter {filter_key} from state")  # Debug
            else:
                # Nếu chọn giá trị khác thì cập nhật filter
                state["allgame_filters"][filter_key] = selected_value
                print(f"Added filter {filter_key} = {selected_value} to state")  # Debug
            
            print(f"Current filters: {state['allgame_filters']}")  # Debug
            state["allgame_page"] = 1
            load_games()
            update_games_display()
        
        return ft.Column([
            ft.Text(label, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),  # Giảm font size từ 14 xuống 12
            ft.Dropdown(
                width=120,  # Giảm width từ 150 xuống 120
                bgcolor="#232b39",
                color=ft.Colors.WHITE,
                border_color="#404040",
                value=current_value,
                options=[
                    ft.dropdown.Option("- All -"),
                    *[ft.dropdown.Option(option) for option in options]
                ],
                on_change=on_filter_change,
                menu_height=200
            )
        ], spacing=3)  # Giảm spacing từ 5 xuống 3

    def create_search_bar():
        def on_search(e):
            search_value = e.control.value.strip()
            state["allgame_search"] = search_value
            print(f"Search query set to: {state['allgame_search']}")  # Debug
            state["allgame_page"] = 1
            load_games()
            update_games_display()
        
        return ft.Column([
            ft.Text("Search:", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),  # Giảm font size từ 14 xuống 12
            ft.TextField(
                width=160,  # Giảm width từ 200 xuống 160
                bgcolor="#232b39",
                color=ft.Colors.WHITE,
                border_color="#404040",
                hint_text="Enter game name...",
                value=state["allgame_search"],
                on_submit=on_search,
                on_change=on_search,
                text_size=12,  # Giảm font size từ 14 xuống 12
                height=35  # Giảm height từ 40 xuống 35
            )
        ], spacing=3)  # Giảm spacing từ 5 xuống 3

    def create_game_card(game):
        def open_game_detail(e):
            state["selected_game"] = game
            state["screen"] = "game_detail"
            render()

        def on_hover(e):
            container.border = ft.border.all(2, "#ffffff") if e.data == "true" else None
            container.bgcolor = "#2a3441" if e.data == "true" else "#232b39"
            page.update()

        release_date = game.get("release_date", "")
        if release_date:
            try:
                if isinstance(release_date, str):
                    date_obj = datetime.strptime(release_date, "%a, %d %b %Y %H:%M:%S GMT")
                    formatted_date = date_obj.strftime("%d-%m-%Y")
                else:
                    formatted_date = release_date.strftime("%d-%m-%Y")
            except:
                formatted_date = "N/A"
        else:
            formatted_date = "N/A"

        price = game.get("price", 0)
        price_display = "Free" if float(price) == 0 else f"${float(price):.2f}"
        price_color = "#2ecc40" if float(price) == 0 else "#22c55e"

        genre = game.get("genre", "")
        genre_tags = [tag.strip() for tag in genre.split(",")] if genre else []

        container = ft.Container(
            content=ft.Column([
                ft.Image(
                    src=game.get("image_url_horizontal") or game.get("image_url_vertical") or "",
                    width=360,  # Giữ nguyên width
                    height=160,  # Giảm height từ 200 xuống 160 để có thêm chỗ cho text
                    fit=ft.ImageFit.COVER,
                    border_radius=10
                ),
                ft.Column([
                    ft.Container(
                        ft.Text(
                            game.get("title", "Unknown Game"),
                            size=15,  # Giữ nguyên font size
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        height=50,  # Chiều cao cố định cho title (đủ cho 2 dòng)
                        alignment=ft.alignment.bottom_left  # Thay đổi từ top_left thành bottom_left
                    ),
                    ft.Row(
                        [ft.Container(
                            ft.Text(tag, size=11, color=ft.Colors.WHITE),  # Giữ nguyên font size
                            bgcolor="#404040",
                            padding=ft.padding.symmetric(horizontal=7, vertical=4),  # Giữ nguyên padding
                            border_radius=8
                        ) for tag in genre_tags[:2] if tag],  # Giữ 2 tags
                        spacing=4,  # Giữ nguyên spacing
                        wrap=True
                    ) if genre_tags else ft.Container(height=0),
                    ft.Text(
                        price_display,
                        size=17,  # Giữ nguyên font size
                        weight=ft.FontWeight.BOLD,
                        color=price_color
                    ),
                    ft.Text(
                        f"Release Date: {formatted_date}",
                        size=11,  # Giữ nguyên font size
                        color="#b0b0b0"
                    )
                ], spacing=7, alignment=ft.MainAxisAlignment.START),  # Giữ nguyên spacing
            ], spacing=9, alignment=ft.MainAxisAlignment.CENTER),  # Giữ nguyên spacing
            width=360,  # Giữ nguyên width
            height=340,  # Giữ nguyên height
            bgcolor="#232b39",
            border_radius=10,
            padding=ft.padding.all(14),  # Giữ nguyên padding
            on_hover=on_hover,
            on_click=open_game_detail,
            margin=ft.margin.all(2)  # Giữ nguyên margin
        )
        return container

    def update_games_display():
        print(f"Updating games display with {len(state['allgame_games'])} games")  # Debug
        games_container.controls.clear()
        
        # Cập nhật suffix của search bar
        search_bar = filter_dropdowns.controls[0].controls[1]
        if isinstance(search_bar, ft.TextField):
            if state["allgame_search"]:
                # Tạo clear button mới mỗi lần update
                clear_button = ft.IconButton(
                    icon=ft.Icons.CLEAR,
                    icon_color="#b0b0b0",
                    icon_size=16,
                    on_click=lambda e: clear_search_and_update(e),
                    tooltip="Clear search"
                )
                search_bar.suffix = clear_button
            else:
                search_bar.suffix = None
        
        if state["allgame_games"]:
            games_rows = []
            for i in range(0, len(state["allgame_games"]), 4):  # 4 game mỗi dòng
                row_games = state["allgame_games"][i:i+4]
                games_rows.append(
                    ft.Row(
                        [create_game_card(game) for game in row_games],
                        spacing=2,  # Giảm spacing từ 4 xuống 2
                        wrap=False,  # Không wrap để giữ 4 thẻ mỗi dòng
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY  # Phân bố đều
                    )
                )
            games_container.controls.extend(games_rows)
        else:
            games_container.controls.append(
                ft.Container(
                    ft.Text("No games found", size=16, color=ft.Colors.GREY),
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(20)
                )
            )
        
        update_pagination()
        page.update()

    def update_pagination():
        pagination_container.controls.clear()
        
        total_pages = state["allgame_total_pages"]
        current_page = state["allgame_page"]
        
        if total_pages > 1:
            prev_button = ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color="#22c55e" if current_page > 1 else "#666666",
                on_click=lambda e: change_page(current_page - 1) if current_page > 1 else None
            )
            pagination_container.controls.append(prev_button)
            
            start_page = max(1, current_page - 2)
            end_page = min(total_pages, current_page + 2)
            
            for page_num in range(start_page, end_page + 1):
                page_button = ft.TextButton(
                    str(page_num),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor={"": "transparent", "hovered": "#2a3441", "focused": "#2a3441"} if page_num != current_page else {"": "#22c55e", "hovered": "#1e2a39", "focused": "#1e2a39"},
                        shape={"": ft.RoundedRectangleBorder(radius=5), "hovered": ft.RoundedRectangleBorder(radius=5), "focused": ft.RoundedRectangleBorder(radius=5)}
                    ),
                    on_click=lambda e, p=page_num: change_page(p)
                )
                pagination_container.controls.append(page_button)
            
            next_button = ft.IconButton(
                icon=ft.Icons.ARROW_FORWARD,
                icon_color="#22c55e" if current_page < total_pages else "#666666",
                on_click=lambda e: change_page(current_page + 1) if current_page < total_pages else None
            )
            pagination_container.controls.append(next_button)

    def change_page(new_page):
        if 1 <= new_page <= state["allgame_total_pages"]:
            state["allgame_page"] = new_page
            load_games()
            update_games_display()

    def change_per_page(e):
        state["allgame_per_page"] = int(e.control.value)
        state["allgame_page"] = 1
        load_games()
        update_games_display()

    def reset_filters(e):
        # Reset tất cả filters về "- All -"
        state["allgame_filters"] = {}
        state["allgame_search"] = ""
        state["allgame_page"] = 1
        
        # Reset tất cả dropdown về giá trị mặc định
        for i, control in enumerate(filter_dropdowns.controls):
            if isinstance(control, ft.Column) and len(control.controls) > 1:
                dropdown = control.controls[1]
                if isinstance(dropdown, ft.Dropdown):
                    dropdown.value = "- All -"
                    print(f"Reset dropdown {i} to '- All -'")  # Debug log
        
        # Reset search bar
        search_bar = filter_dropdowns.controls[0].controls[1]
        if isinstance(search_bar, ft.TextField):
            search_bar.value = ""
            print("Reset search bar")  # Debug log
        
        print("All filters reset, loading games...")  # Debug log
        load_games()
        update_games_display()
        
        # Force update UI để đảm bảo tất cả dropdown được cập nhật
        page.update()
        print("Reset complete")  # Debug log

    # Load data ban đầu
    if not state["filter_options"]:
        load_filter_options()
    load_games()

    games_container = ft.Column(expand=True)
    pagination_container = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    filter_options = state["filter_options"]
    filter_dropdowns = ft.Row([
        create_search_bar(),
        create_filter_dropdown("Genre:", filter_options.get("genre", []), "genre"),
        create_filter_dropdown("RAM:", filter_options.get("ram", []), "ram"),
        create_filter_dropdown("Storage:", filter_options.get("storage", []), "storage"),
        create_filter_dropdown("CPU:", filter_options.get("cpu", []), "cpu"),
        create_filter_dropdown("GPU:", filter_options.get("gpu", []), "gpu"),
        ft.IconButton(
            icon=ft.Icons.RESTART_ALT,
            icon_color="#22c55e",
            tooltip="Reset Filters",
            on_click=reset_filters
        )
    ], spacing=12, alignment=ft.MainAxisAlignment.CENTER)  # Giảm spacing từ 20 xuống 12

    per_page_dropdown = ft.Dropdown(
        width=100,
        bgcolor="#232b39",
        color=ft.Colors.WHITE,
        border_color="#404040",
        value=str(state["allgame_per_page"]),
        options=[
            ft.dropdown.Option("16"),
            ft.dropdown.Option("24"),
            ft.dropdown.Option("36"),
            ft.dropdown.Option("48")
        ],
        on_change=change_per_page,
        menu_height=150
    )

    update_games_display()

    # Header with menu and search - similar to AI Chat
    header = build_menu_row(
        state, 
        render, 
        set_home, 
        handle_menu, 
        on_search_change, 
        search_results_container, 
        set_about_us, 
        set_contact_us,
        clear_search
    )

    footer = build_footer(set_terms, set_privacy, set_home, set_about_us, set_contact_us)

    # Main content - similar to AI Chat structure
    main_content = ft.Column([
        ft.Container(
            filter_dropdowns,
            padding=ft.padding.only(bottom=20)
        ),
        ft.Container(
            content=games_container,
            expand=True,
            padding=ft.padding.only(bottom=20)
        ),
        ft.Container(
            ft.Row([
                ft.Text(f"Total {state['allgame_total']}", size=14, color=ft.Colors.WHITE),
                ft.Container(expand=True),
                ft.Row([
                    ft.Text("per page:", size=14, color=ft.Colors.WHITE),
                    per_page_dropdown
                ], spacing=10),
                ft.Container(expand=True),
                pagination_container
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(bottom=20)
        )
    ], expand=True, scroll=ft.ScrollMode.AUTO)

    # Create Stack for proper layering like AI Chat
    main_stack = ft.Stack(
        controls=[
            main_content
        ],
        expand=True
    )

    # Add header and main stack to page like AI Chat
    page.add(
        ft.Stack([
            ft.Column([
                header,
                ft.Container(
                    ft.Column([
                        ft.Container(
                            main_stack,
                            padding=ft.padding.symmetric(horizontal=10, vertical=20),
                            expand=True
                        ),
                        footer
                    ], expand=True, scroll=ft.ScrollMode.AUTO),
                    expand=True
                )
            ], expand=True),
            search_results_container
        ], expand=True)
    )

    page.update()