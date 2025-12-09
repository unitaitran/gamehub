import flet as ft
from ...backend.edit_game_be import get_all_categories_from_db, get_game_genres_from_db, update_game_in_db, get_game_by_id_for_edit
import os

def edit_game_screen(page, state, render):
    # Lấy đường dẫn tuyệt đối đến file logo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "..", "..", "data", "images", "Logo_game_rmb.png")
    
    # Check if user is admin
    current_user = state.get("username", "")
    if current_user.lower() != "admin":
        state["screen"] = "home"
        render()
        return

    # Get game data from state
    game_to_edit = state.get("game_to_edit", {})    
    if not game_to_edit:
        state["screen"] = "admin"
        render()
        return

    # Get game data from database if it's a database game
    if game_to_edit.get("source_list") == "database":
        game_id = game_to_edit.get("id")
        if game_id:
            db_game = get_game_by_id_for_edit(game_id)
            if db_game:
                game_to_edit = db_game
                state["game_to_edit"] = db_game
            else:
                print(f"Could not fetch game with ID {game_id} from database")
                state["screen"] = "admin"
                render()
                return

    # Initialize state for edit game
    state["edit_game_name"] = game_to_edit.get("name", "")
    state["edit_game_price"] = game_to_edit.get("price", 0)
    state["edit_game_price_original"] = game_to_edit.get("price_original", 0)
    state["edit_game_description"] = game_to_edit.get("description", "")
    
    # Safely copy genres list
    genres = game_to_edit.get("genres", [])
    if isinstance(genres, list):
        state["edit_game_genres"] = genres.copy()
    else:
        if isinstance(genres, str):
            state["edit_game_genres"] = [g.strip() for g in genres.split(",") if g.strip()]
        else:
            state["edit_game_genres"] = []
    


    def handle_menu(menu_item):
        if menu_item == "logout":
            state.clear()
            state.update({
                "screen": "login",
                "login_error": "",
                "login_email": "",
                "login_password": ""
            })
        elif menu_item == "admin":
            state["screen"] = "admin"
        elif menu_item == "allgame":
            state["screen"] = "allgame"
        render()

    def build_menu_row():
        return ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=go_back
            ),
            ft.Container(expand=True),  # Spacer để đẩy logo vào giữa
            ft.Image(
                src="gamehub-dev/src/data/images/Logo_game_rmb.png",
                width=100,
                height=100,
                fit=ft.ImageFit.CONTAIN
            ),
            ft.Container(expand=True),  # Spacer để đẩy "ADMIN" sang phải
            ft.Text("ADMIN", color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.START)

    def on_name_change(e):
        state["edit_game_name"] = e.control.value

    def on_price_change(e):
        try:
            state["edit_game_price"] = float(e.control.value)
        except:
            state["edit_game_price"] = 0

    def on_price_original_change(e):
        try:
            state["edit_game_price_original"] = float(e.control.value)
        except:
            state["edit_game_price_original"] = 0

    def on_description_change(e):
        state["edit_game_description"] = e.control.value

    def toggle_genre(e, genre):
        if genre in state["edit_game_genres"]:
            state["edit_game_genres"].remove(genre)
        else:
            state["edit_game_genres"].append(genre)
        update_genre_ui()

    def update_genre_ui():
        """Update the genre selection UI"""
        selected_genres_container.content.controls = [build_selected_genres_display()]
        genre_grid_container.content.controls = [build_genre_selection_grid()]
        page.update()

    def confirm_edit():
        game_name = state["edit_game_name"].strip() if state["edit_game_name"] else ""
        description = state["edit_game_description"].strip() if state["edit_game_description"] else ""
        price = state["edit_game_price"]
        price_original = state["edit_game_price_original"]
        
        clear_all_errors()
        
        has_error = False
        
        if not game_name:
            show_field_error("game_name", "Please enter game name")
            has_error = True
        
        if not description:
            show_field_error("description", "Please enter game description")
            has_error = True
        
        if not state["edit_game_genres"]:
            show_field_error("genres", "Please select at least one genre")
            has_error = True
        
        if not price or price <= 0:
            show_field_error("price", "Please enter a valid price")
            has_error = True
        
        if not price_original or price_original <= 0:
            show_field_error("price_original", "Please enter a valid original price")
            has_error = True
        
        if has_error:
            return
        
        if game_to_edit.get("source_list") == "database":
            game_id = game_to_edit.get("id")
            if game_id:
                from ...backend.admin_interface_be import get_game_by_id
                game_check = get_game_by_id(game_id)
                if not game_check:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Game with ID {game_id} not found!"))
                    page.snack_bar.open = True
                    page.update()
                    return
                
                game_data = {
                    "name": game_name,
                    "description": description,
                    "price": price,
                    "price_original": price_original,
                    "genres": state["edit_game_genres"]
                }
                
                success = update_game_in_db(game_id, game_data)
                if success:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Game updated successfully!"))
                    page.snack_bar.open = True
                    page.update()
                    state["screen"] = "admin"
                    render()
                else:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Error updating game ID {game_id}!"))
                    page.snack_bar.open = True
                    page.update()
                    return
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("Game ID not found!"))
                page.snack_bar.open = True
                page.update()
                return
        else:
            game_to_edit["name"] = game_name
            game_to_edit["price"] = price
            game_to_edit["price_original"] = price_original
            game_to_edit["description"] = description
            game_to_edit["genres"] = state["edit_game_genres"]
            page.snack_bar = ft.SnackBar(content=ft.Text("Game updated successfully!"))
            page.snack_bar.open = True
            page.update()
            state["screen"] = "admin"
            render()

    def go_back(e=None):
        state["screen"] = "admin"
        render()

    def show_field_error(field_name, message):
        if field_name == "game_name":
            game_name_error.visible = True
            game_name_error.value = message
        elif field_name == "description":
            description_error.visible = True
            description_error.value = message
        elif field_name == "genres":
            genres_error.visible = True
            genres_error.value = message
        elif field_name == "price":
            price_error.visible = True
            price_error.value = message
        elif field_name == "price_original":
            price_original_error.visible = True
            price_original_error.value = message
        page.update()

    def clear_all_errors():
        game_name_error.visible = False
        description_error.visible = False
        genres_error.visible = False
        price_error.visible = False
        price_original_error.visible = False
        page.update()

    def get_available_genres():
        try:
            categories = get_all_categories_from_db()
            genres = [cat["name"] for cat in categories]
            return genres
        except Exception as e:
            print(f"Error getting categories from database: {e}")
            fallback_genres = ["Action", "Adventure", "RPG", "Strategy", "Sports", "Racing", "Puzzle", "Horror", "Stealth", "FPS", "MMO", "Indie"]
            return fallback_genres

    GAME_GENRES = get_available_genres()

    def build_selected_genres_display():
        if state["edit_game_genres"]:
            return ft.Row(
                controls=[
                    ft.Chip(
                        label=ft.Text(genre, color=ft.Colors.WHITE, size=12),
                        bgcolor=ft.Colors.GREEN_600,
                        delete_icon=ft.Icon("close"),
                        on_delete=lambda e, g=genre: toggle_genre(e, g),
                        shape=ft.StadiumBorder(),
                        label_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
                    ) for genre in state["edit_game_genres"]
                ],
                wrap=True,
                spacing=8
            )
        else:
            return ft.Text("No genres selected", color=ft.Colors.GREY_500, size=12)

    def build_genre_selection_grid():
        return ft.Row(
            controls=[
                ft.ElevatedButton(
                    text=genre,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE if genre in state["edit_game_genres"] else ft.Colors.GREY_400,
                        bgcolor=ft.Colors.GREEN_600 if genre in state["edit_game_genres"] else ft.Colors.GREY_800,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=12, vertical=8)
                    ),
                    on_click=lambda e, g=genre: toggle_genre(e, g)
                ) for genre in GAME_GENRES
            ],
            wrap=True,
            spacing=8
        )

    content = ft.Column([
        ft.Container(
            content=build_menu_row(),  # Sử dụng build_menu_row cho toàn bộ hàng
            padding=ft.padding.only(bottom=20)
        ),
        
        ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Edit game information", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Container(height=20),
                        
                        ft.Text("Name of Game", color=ft.Colors.WHITE, size=14),
                        ft.TextField(
                            value=state["edit_game_name"],
                            on_change=on_name_change,
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_700,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            border_radius=8
                        ),
                        game_name_error := ft.Text(
                            "Please enter game name",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=16),
                        
                        ft.Text("Game genres", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        selected_genres_container := ft.Container(
                            content=ft.Column(
                                controls=[build_selected_genres_display()]
                            ),
                            bgcolor=ft.Colors.GREY_900,
                            padding=ft.padding.all(12),
                            border_radius=8,
                            border=ft.border.all(1, ft.Colors.GREY_700)
                        ),
                        ft.Container(height=8),
                        genre_grid_container := ft.Container(
                            content=ft.Column(
                                controls=[build_genre_selection_grid()]
                            ),
                            padding=ft.padding.all(16),
                            bgcolor=ft.Colors.GREY_900,
                            border_radius=8
                        ),
                        genres_error := ft.Text(
                            "Please select at least one genre",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=16),
                        
                        ft.Text("Price", color=ft.Colors.WHITE, size=14),
                        ft.TextField(
                            value=str(state["edit_game_price"]),
                            on_change=on_price_change,
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_700,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            border_radius=8,
                            suffix_text="₫"
                        ),
                        price_error := ft.Text(
                            "Please enter valid price",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=16),
                        
                        ft.Text("Original Price", color=ft.Colors.WHITE, size=14),
                        ft.TextField(
                            value=str(state["edit_game_price_original"]),
                            on_change=on_price_original_change,
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_700,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            border_radius=8,
                            suffix_text="₫"
                        ),
                        price_original_error := ft.Text(
                            "Please enter valid original price",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=16),
                        
                        ft.Text("Description", color=ft.Colors.WHITE, size=14),
                        ft.TextField(
                            value=state["edit_game_description"],
                            on_change=on_description_change,
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_700,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            border_radius=8,
                            multiline=True,
                            min_lines=4,
                            max_lines=6
                        ),
                        description_error := ft.Text(
                            "Please enter game description",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                    ], spacing=8),
                    expand=True,
                    padding=ft.padding.all(20)
                ),
                
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Image(
                                src=game_to_edit.get("image", ""),
                                width=300,
                                height=400,
                                fit=ft.ImageFit.COVER,
                                border_radius=8
                            ),
                            padding=ft.padding.all(8)
                        ),
                        elevation=8
                    ),
                    border=ft.border.all(2, ft.Colors.GREY_700),
                    border_radius=12,
                    margin=ft.margin.only(left=20)
                ),
            ]),
            bgcolor=ft.Colors.GREY_900,
            border_radius=12,
            padding=ft.padding.all(20)
        ),
        
        ft.Container(
            content=ft.ElevatedButton(
                content=ft.Text("Confirm edit", size=16, weight=ft.FontWeight.BOLD),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                    padding=ft.padding.symmetric(horizontal=30, vertical=15),
                ),
                on_click=lambda e: confirm_edit()
            ),
            alignment=ft.alignment.center,
            margin=ft.margin.only(top=20)
        ),
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