import flet as ft
from ...backend.add_game_be import get_all_categories_from_db, add_game_to_db, validate_game_data
import os

# Get available genres from database
def get_available_genres():
    try:
        categories = get_all_categories_from_db()
        genres = [cat["name"] for cat in categories]
        return genres
    except Exception as e:
        # Fallback to hardcoded genres if database fails
        fallback_genres = [
            "Action", "Adventure", "RPG", "Strategy", "Simulation", 
            "Sports", "Racing", "Puzzle", "Horror", "Fighting",
            "Shooter", "Stealth", "Survival", "Open World", "Sandbox",
            "Visual Novel", "Roguelike", "Metroidvania", "Platformer", "Arcade"
        ]
        return fallback_genres

# Game genres data from database
GAME_GENRES = get_available_genres()

def add_game_screen(page, state, render):
    # Lấy đường dẫn tuyệt đối đến file logo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "..", "..", "data", "images", "Logo_game_rmb.png")
    current_user = state.get("username", "")
    
    # Check if user is admin
    if current_user.lower() != "admin":
        state["screen"] = "home"
        render()
        return

    # Initialize selected genres
    if "selected_genres" not in state:
        state["selected_genres"] = []

    def go_back(e):
        state["screen"] = "admin"
        render()

    def toggle_genre(e, genre):
        if genre in state["selected_genres"]:
            state["selected_genres"].remove(genre)
        else:
            state["selected_genres"].append(genre)
        update_genre_ui()

    def remove_genre(genre):
        if genre in state["selected_genres"]:
            state["selected_genres"].remove(genre)
            update_genre_ui()

    def update_genre_ui():
        """Update the genre selection UI"""
        selected_genres_container.content.controls = [build_selected_genres_display()]
        genre_grid_container.content.controls = [build_genre_selection_grid()]
        page.update()

    def add_game(e):
        # Get all field values
        game_name = game_name_field.value.strip() if game_name_field.value else ""
        description = description_field.value.strip() if description_field.value else ""
        price = price_field.value.strip() if price_field.value else ""
        price_original = price_original_field.value.strip() if price_original_field.value else ""
        horizontal_image = horizontal_image_field.value.strip() if horizontal_image_field.value else ""
        vertical_image = vertical_image_field.value.strip() if vertical_image_field.value else ""
        cpu = cpu_field.value.strip() if cpu_field.value else ""
        gpu = gpu_field.value.strip() if gpu_field.value else ""
        ram = ram_field.value.strip() if ram_field.value else ""
        storage = storage_field.value.strip() if storage_field.value else ""
        
        # Clear all previous errors first
        clear_all_errors()
        
        # Prepare game data
        game_data = {
            "name": game_name,
            "description": description,
            "price": float(price) if price else 0,
            "price_original": float(price_original) if price_original else 0,
            "horizontal_image": horizontal_image,
            "vertical_image": vertical_image,
            "cpu": cpu,
            "gpu": gpu,
            "ram": ram,
            "storage": storage,
            "genres": state["selected_genres"]
        }
        
        # Validate game data
        validation_errors = validate_game_data(game_data)
        if validation_errors:
            # Show first error
            if "tên game" in validation_errors[0].lower():
                show_field_error("game_name", validation_errors[0])
            elif "mô tả" in validation_errors[0].lower():
                show_field_error("description", validation_errors[0])
            elif "thể loại" in validation_errors[0].lower():
                show_field_error("genres", validation_errors[0])
            elif "giá" in validation_errors[0].lower():
                show_field_error("price", validation_errors[0])
            elif "giá gốc" in validation_errors[0].lower():
                show_field_error("price_original", validation_errors[0])
            elif "ảnh ngang" in validation_errors[0].lower():
                show_field_error("horizontal_image", validation_errors[0])
            elif "ảnh dọc" in validation_errors[0].lower():
                show_field_error("vertical_image", validation_errors[0])
            elif "cpu" in validation_errors[0].lower():
                show_field_error("cpu", validation_errors[0])
            elif "gpu" in validation_errors[0].lower():
                show_field_error("gpu", validation_errors[0])
            elif "ram" in validation_errors[0].lower():
                show_field_error("ram", validation_errors[0])
            elif "storage" in validation_errors[0].lower():
                show_field_error("storage", validation_errors[0])
            return
        
        # Add game to database
        success = add_game_to_db(game_data)
        if success:
            page.snack_bar = ft.SnackBar(
                ft.Text("Game added successfully to database!", color="white"),
                bgcolor="#22c55e"
            )
            page.snack_bar.open = True
            page.update()
            
            # Clear form
            game_name_field.value = ""
            description_field.value = ""
            price_field.value = ""
            price_original_field.value = ""
            horizontal_image_field.value = ""
            vertical_image_field.value = ""
            cpu_field.value = ""
            gpu_field.value = ""
            ram_field.value = ""
            storage_field.value = ""
            state["selected_genres"] = []
            update_genre_ui()
            
            # Go back to admin
            state["screen"] = "admin"
            render()
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text("Failed to add game to database!", color="white"),
                bgcolor="#ef4444"
            )
            page.snack_bar.open = True
            page.update()

    def show_field_error(field_name, message):
        # Update the specific error text for the field
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
        elif field_name == "horizontal_image":
            horizontal_image_error.visible = True
            horizontal_image_error.value = message
        elif field_name == "vertical_image":
            vertical_image_error.visible = True
            vertical_image_error.value = message
        elif field_name == "cpu":
            cpu_error.visible = True
            cpu_error.value = message
        elif field_name == "gpu":
            gpu_error.visible = True
            gpu_error.value = message
        elif field_name == "ram":
            ram_error.visible = True
            ram_error.value = message
        elif field_name == "storage":
            storage_error.visible = True
            storage_error.value = message
        page.update()

    def clear_all_errors():
        # Hide all error messages
        game_name_error.visible = False
        description_error.visible = False
        genres_error.visible = False
        price_error.visible = False
        price_original_error.visible = False
        horizontal_image_error.visible = False
        vertical_image_error.visible = False
        cpu_error.visible = False
        gpu_error.visible = False
        ram_error.visible = False
        storage_error.visible = False
        page.update()

    def build_selected_genres_display():
        if state["selected_genres"]:
            return ft.Row(
                controls=[
                    ft.Chip(
                        label=ft.Text(genre, color=ft.Colors.WHITE, size=12),
                        bgcolor=ft.Colors.GREEN_600,
                        delete_icon=ft.Icon("close"),
                        on_delete=lambda e, g=genre: remove_genre(g),
                        shape=ft.StadiumBorder(),
                        label_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
                    ) for genre in state["selected_genres"]
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
                        color=ft.Colors.WHITE if genre in state["selected_genres"] else ft.Colors.GREY_400,
                        bgcolor=ft.Colors.GREEN_600 if genre in state["selected_genres"] else ft.Colors.GREY_800,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=12, vertical=8)
                    ),
                    on_click=lambda e, g=genre: toggle_genre(e, g)
                ) for genre in GAME_GENRES
            ],
            wrap=True,
            spacing=8
        )

    # Header
    header = ft.Container(
        content=ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=go_back
            ),
            ft.Image(
                src=logo_path,
                width=150,
                height=150,
                fit=ft.ImageFit.CONTAIN
            ),
            ft.Text("ADMIN", color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.all(16),
        bgcolor=ft.Colors.BLACK
    )



    # Game info section
    game_info_section = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text("Add game to", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                alignment=ft.alignment.center,
                margin=ft.margin.only(bottom=8)
            ),
            ft.Text("Game info", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(height=16),
            ft.Row([
                # Left column
                ft.Container(
                    content=ft.Column([
                        ft.Text("Name of Game", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        game_name_field := ft.TextField(
                            hint_text="Enter name of game",
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            width=300
                        ),
                        game_name_error := ft.Text(
                            "Please enter game name",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=16),
                        ft.Text("Description", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        description_field := ft.TextField(
                            hint_text="Description",
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            width=300,
                            multiline=True,
                            min_lines=3,
                            max_lines=5
                        ),
                        description_error := ft.Text(
                            "Please enter game description",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=16),
                        ft.Text("Price", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        price_field := ft.TextField(
                            hint_text="Enter price",
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            width=300
                        ),
                        price_error := ft.Text(
                            "Please enter game price",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=16),
                        ft.Text("Original Price", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        price_original_field := ft.TextField(
                            hint_text="Enter original price",
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            width=300
                        ),
                        price_original_error := ft.Text(
                            "Please enter original price",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=16),
                        ft.Text("Horizontal image", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        horizontal_image_field := ft.TextField(
                            hint_text="Link",
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            width=300
                        ),
                        horizontal_image_error := ft.Text(
                            "Please enter horizontal image link",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=8),
                        ft.Text("Vertical image", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        vertical_image_field := ft.TextField(
                            hint_text="Link",
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            width=300
                        ),
                        vertical_image_error := ft.Text(
                            "Please enter vertical image link",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                    ]),
                    expand=True,
                    padding=ft.padding.only(left=20)
                ),
                # Right column - Only genres
                ft.Container(
                    content=ft.Column([
                        ft.Text("Game genres", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        # Selected genres display
                        selected_genres_container := ft.Container(
                            content=ft.Column(
                                controls=[build_selected_genres_display()]
                            ),
                            bgcolor=ft.Colors.GREY_900,
                            padding=ft.padding.all(12),
                            border_radius=8,
                            border=ft.border.all(1, ft.Colors.GREY_700)
                        ),
                        ft.Container(height=16),
                        # Genre selection grid
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
                    ]),
                    expand=True
                ),
            ], spacing=32),
        ]),
        padding=ft.padding.only(left=20, right=20, top=24, bottom=24)
    )

    # Minimum Configuration section
    min_config_section = ft.Container(
        content=ft.Column([
            ft.Text("Recommended Configuration", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(height=16),
            ft.Row([
                # Left column
                ft.Container(
                    content=ft.Column([
                        ft.Text("CPU", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        cpu_field := ft.TextField(
                            hint_text="Enter CPU requirements",
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            width=300
                        ),
                        cpu_error := ft.Text(
                            "Please enter CPU requirements",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=16),
                        ft.Text("GPU", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        gpu_field := ft.TextField(
                            hint_text="Enter GPU requirements",
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            width=300
                        ),
                        gpu_error := ft.Text(
                            "Please enter GPU requirements",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                    ]),
                    expand=True,
                    padding=ft.padding.only(left=20)
                ),
                # Right column
                ft.Container(
                    content=ft.Column([
                        ft.Text("RAM", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        ram_field := ft.TextField(
                            hint_text="Enter RAM requirements",
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            width=300
                        ),
                        ram_error := ft.Text(
                            "Please enter RAM requirements",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                        ft.Container(height=16),
                        ft.Text("Storage", color=ft.Colors.WHITE, size=14),
                        ft.Container(height=8),
                        storage_field := ft.TextField(
                            hint_text="Enter storage requirements",
                            bgcolor=ft.Colors.GREY_800,
                            border_color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(color=ft.Colors.WHITE),
                            width=300
                        ),
                        storage_error := ft.Text(
                            "Please enter storage requirements",
                            color="#ef4444",
                            size=12,
                            visible=False
                        ),
                    ]),
                    expand=True
                ),
            ], spacing=32),
        ]),
        padding=ft.padding.only(left=20, right=20, top=24, bottom=24)
    )

    # Add Game button
    add_button = ft.Container(
        content=ft.ElevatedButton(
            "Add Game",
            bgcolor="#22c55e",
            color=ft.Colors.WHITE,
            width=200,
            height=48,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=add_game
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.all(24)
    )

    # Main content card
    main_content = ft.Container(
        content=ft.Column([
            game_info_section,
            ft.Divider(color=ft.Colors.GREY_700, height=1),
            min_config_section,
            ft.Divider(color=ft.Colors.GREY_700, height=1),
            add_button,
        ]),
        bgcolor=ft.Colors.GREY_900,
        border_radius=12,
        margin=ft.margin.all(16),
        padding=ft.padding.all(0)
    )

    # Page content
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    main_content,
                ],
                scroll="auto"
            ),
            padding=20,
            expand=True,
            bgcolor=ft.Colors.BLACK
        )
    )
    page.update() 