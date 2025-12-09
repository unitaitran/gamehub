import flet as ft

def confirm_delete_screen(page, state, render):
    """
    Màn hình confirm xóa game hoặc user
    """
    item_type = state.get("confirm_item_type", "game")  # "game" hoặc "user"
    item_data = state.get("confirm_item_data", {})
    
    def on_cancel(e):
        # Xóa dữ liệu confirm và quay lại admin interface
        if "confirm_item_type" in state:
            del state["confirm_item_type"]
        if "confirm_item_data" in state:
            del state["confirm_item_data"]
        state["screen"] = "admin"
        render()
    
    def on_confirm_delete(e):
        # Hiển thị thông báo "cancelled" và quay lại admin interface
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Delete action cancelled - {item_type} remains in system"),
            bgcolor="#22c55e"
        )
        page.snack_bar.open = True
        
        # Xóa dữ liệu confirm và quay lại admin interface
        if "confirm_item_type" in state:
            del state["confirm_item_type"]
        if "confirm_item_data" in state:
            del state["confirm_item_data"]
        state["screen"] = "admin"
        render()
    
    # Header với back button
    header = ft.Container(
        content=ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                icon_size=24,
                on_click=on_cancel
            ),
            ft.Text(
                "Confirm Delete",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            ft.Container(expand=True),  # Spacer
        ]),
        padding=ft.padding.only(left=16, right=16, top=16, bottom=8)
    )
    
    # Main content
    if item_type == "game":
        title = "Delete Game"
        question = "Are you sure you want to delete this game?"
        item_name = item_data.get("name", "Unknown Game")
        item_display = f"Game: {item_name}"
    else:  # user
        title = "Delete User"
        question = "Are you sure you want to delete this user?"
        item_name = item_data.get("username", "Unknown User")
        item_display = f"User: {item_name}"
    
    # Main content container
    main_content = ft.Container(
        content=ft.Column([
            # Title
            ft.Text(
                title,
                size=32,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
                color="white"
            ),
            
            # Green divider
            ft.Divider(height=2, thickness=2, color="#22c55e"),
            ft.Container(height=16),
            
            # Question
            ft.Text(
                question,
                size=18,
                text_align=ft.TextAlign.CENTER,
                color="white"
            ),
            ft.Container(height=16),
            
            # Item info box
            ft.Container(
                content=ft.Text(
                    item_display,
                    size=16,
                    color="#22c55e",
                    weight=ft.FontWeight.BOLD
                ),
                bgcolor="#232b39",
                padding=ft.padding.all(16),
                border_radius=8,
                border=ft.border.all(1, "#22c55e")
            ),
            ft.Container(height=24),
            
            # Buttons
            ft.Row([
                ft.ElevatedButton(
                    "Cancel",
                    bgcolor="#22c55e",
                    color="white",
                    width=180,
                    height=44,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=on_cancel
                ),
                ft.ElevatedButton(
                    f"Delete {item_type}",
                    bgcolor="#e74c3c",
                    color="white",
                    width=180,
                    height=44,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=on_confirm_delete
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=32)
            
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.padding.all(16),
        bgcolor="#232b39",
        border=ft.border.all(1, "white"),
        border_radius=28,
        width=600,
        alignment=ft.alignment.center
    )
    
    # Full screen layout
    page.views.clear()
    page.views.append(
        ft.View(
            "/confirm_delete",
            [
                ft.Container(
                    content=ft.Column([
                        header,
                        ft.Container(expand=True, content=main_content)
                    ]),
                    expand=True,
                    bgcolor="#1a1a1a"
                )
            ]
        )
    ) 