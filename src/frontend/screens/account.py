import flet as ft
from src.backend.account_be import get_user_profile, update_user_profile, delete_user_account, change_password

def account_screen(page, state, render, footer):
    # --- Phần lấy dữ liệu và khởi tạo state (giữ nguyên) ---
    if "edit_state" not in state: state["edit_state"] = {"username": False, "fullname": False, "phone": False, "age": False, "gender": False}
    if "show_success_message" not in state: state["show_success_message"] = False
    if "password_success" not in state: state["password_success"] = False
    if "password_error" not in state: state["password_error"] = ""
    if "edit_error" not in state: state["edit_error"] = ""
    if "show_delete_dialog" not in state: state["show_delete_dialog"] = False
    current_username = state.get("username", "")
    profile_result = get_user_profile(current_username)
    if profile_result.get("success"):
        user_data = profile_result["data"]
        state["user_info"] = {
            "username": user_data.get("username", ""), "fullname": user_data.get("fullname", ""),
            "email": user_data.get("email", ""), "phone": user_data.get("phone", ""), 
            "age": str(user_data.get("age") or ""), "gender": user_data.get("gender", "Male"),
            "balance": user_data.get("coin", 0.0)
        }
    else:
        error_message = profile_result.get("error", "Unknown error.")
        page.snack_bar = ft.SnackBar(ft.Text(f"Error: {error_message}", color="white"), bgcolor="red")
        page.snack_bar.open = True
        state["user_info"] = { "username": "Error", "fullname": "Error", "email": "Error", "phone": "", "age": "", "gender": "Male", "balance": 0.0 }
    
    edit_state = state["edit_state"]
    user_info = state["user_info"]

    # --- Các hàm xử lý sự kiện ---
    def on_update_click(field): edit_state[field] = True; render()
    
    def on_save(e):
        # Clear previous error
        state["edit_error"] = ""
        
        # Get values from fields
        username_val = username.value
        fullname_val = fullname.value
        phone_val = phone.value
        age_val = age.value
        gender_val = gender.value
        
        # Validation: Check if all fields are filled
        if not username_val or not fullname_val or not phone_val or not age_val or not gender_val:
            state["edit_error"] = "Please fill in all information."
            render()
            return
        
        # Validation: Check username length
        if len(username_val.strip()) < 3:
            state["edit_error"] = "Username must be at least 3 characters long."
            render()
            return
        
        # Validation: Check username format (only letters, numbers, underscore, hyphen)
        if not username_val.replace("_", "").replace("-", "").isalnum():
            state["edit_error"] = "Username can only contain letters, numbers, underscore and hyphen."
            render()
            return
        
        # Validation: Check fullname length
        if len(fullname_val.strip()) < 2:
            state["edit_error"] = "Full name must be at least 2 characters long."
            render()
            return
        
        # Validation: Check if fullname contains numbers
        if any(char.isdigit() for char in fullname_val):
            state["edit_error"] = "Full name cannot contain numbers."
            render()
            return
        
        # Validation: Check phone number length
        if len(phone_val) != 10:
            state["edit_error"] = "Phone number must have exactly 10 digits."
            render()
            return
        
        # Validation: Check if phone contains only digits
        if not phone_val.isdigit():
            state["edit_error"] = "Phone number must contain only digits."
            render()
            return
        
        # Validation: Check age is a number
        if not age_val.isdigit():
            state["edit_error"] = "Age must be a number."
            render()
            return
        
        # Validation: Check age range
        age_num = int(age_val)
        if age_num < 1 or age_num > 120:
            state["edit_error"] = "Age must be between 1 and 120."
            render()
            return
        
        data_to_update = {"username": username_val, "fullname": fullname_val, "phone": phone_val, "age": age_val, "gender": gender_val}
        result = update_user_profile(current_username, data_to_update)
        if result.get("success"):
            state["show_success_message"] = True
            state["edit_error"] = ""
            for k in edit_state: edit_state[k] = False
            
            # Cập nhật username trong state nếu có thay đổi
            if result.get("new_username"):
                state["username"] = result["new_username"]
                # Cập nhật user_info để hiển thị username mới
                state["user_info"]["username"] = result["new_username"]
        else:
            state["edit_error"] = result.get("error", "An error occurred.")
        render()

    def on_ok(e):
        state["show_success_message"] = False
        render()

    def on_password_ok(e):
        state["password_success"] = False
        render()

    def on_change_password(e):
        current_pwd = current_password_field.value
        new_pwd = new_password_field.value
        confirm_pwd = confirm_password_field.value
        
        # Clear previous error
        state["password_error"] = ""
        
        # Validation: Check if all fields are filled
        if not current_pwd or not new_pwd or not confirm_pwd:
            state["password_error"] = "Please fill in all information."
            render()
            return
        
        # Validation: Check if new password matches confirmation
        if new_pwd != confirm_pwd:
            state["password_error"] = "New password and confirmation password do not match."
            render()
            return
        
        # Validation: Check minimum password length
        if len(new_pwd) < 6:
            state["password_error"] = "New password must be at least 6 characters long."
            render()
            return
        
        # Call backend to change password
        result = change_password(current_username, current_pwd, new_pwd)
        
        if result.get("success"):
            state["password_success"] = True
            state["password_error"] = ""
            # Clear password fields only on success
            current_password_field.value = ""
            new_password_field.value = ""
            confirm_password_field.value = ""
            render()
        else:
            # Show specific error message from backend without clearing fields
            error_msg = result.get("error", "An error occurred.")
            state["password_error"] = error_msg
            render()

    # --- HÀM MỚI: Xử lý xóa trực tiếp ---
    def show_delete_dialog(e):
        """
        Hiển thị dialog xác nhận xóa tài khoản
        """
        state["show_delete_dialog"] = True
        render()
    
    def confirm_delete_account(e):
        """
        Xác nhận xóa tài khoản
        """
        result = delete_user_account(current_username)
        
        if result.get("success"):
            page.snack_bar = ft.SnackBar(ft.Text(result.get("message"), color="white"), bgcolor="#22c55e")
            # Đăng xuất người dùng
            state.clear()
            state.update({"screen": "login"})
        else:
            error_msg = result.get("error", "Unknown error.")
            page.snack_bar = ft.SnackBar(ft.Text(error_msg, color="white"), bgcolor="red")
            
        page.snack_bar.open = True
        render()
    
    def cancel_delete_account(e):
        """
        Hủy bỏ xóa tài khoản
        """
        state["show_delete_dialog"] = False
        render()

    # --- Giao diện (UI Components) ---
    username = ft.TextField(value=user_info["username"], width=260, label="User name:", label_style=ft.TextStyle(color="#b0b0b0"), filled=True, fill_color="#232b39", border_color="#232b39", text_style=ft.TextStyle(color="white"), disabled=not edit_state["username"])
    fullname = ft.TextField(value=user_info["fullname"], width=260, label="Full name:", label_style=ft.TextStyle(color="#b0b0b0"), filled=True, fill_color="#232b39", border_color="#232b39", text_style=ft.TextStyle(color="white"), disabled=not edit_state["fullname"])
    email = ft.TextField(value=user_info["email"], width=260, label="Email:", label_style=ft.TextStyle(color="#b0b0b0"), filled=True, fill_color="#232b39", border_color="#232b39", text_style=ft.TextStyle(color="white"), disabled=True)
    phone = ft.TextField(value=user_info["phone"], width=260, label="Phone number:", label_style=ft.TextStyle(color="#b0b0b0"), filled=True, fill_color="#232b39", border_color="#232b39", text_style=ft.TextStyle(color="white"), disabled=not edit_state["phone"])
    age = ft.TextField(value=user_info["age"], width=120, label="Age:", label_style=ft.TextStyle(color="#b0b0b0"), filled=True, fill_color="#232b39", border_color="#232b39", text_style=ft.TextStyle(color="white"), disabled=not edit_state["age"])
    gender = ft.Dropdown(label="Gender:", label_style=ft.TextStyle(color="#b0b0b0"), width=120, filled=True, fill_color="#232b39", border_color="#232b39", text_style=ft.TextStyle(color="white"), options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female"), ft.dropdown.Option("Other")], value=user_info["gender"], disabled=not edit_state["gender"])
    balance = ft.TextField(value=f"${user_info.get('balance', 0.0):.2f}", width=260, label="Balance:", label_style=ft.TextStyle(color="#b0b0b0"), filled=True, fill_color="#232b39", border_color="#232b39", text_style=ft.TextStyle(color="#22c55e", weight=ft.FontWeight.BOLD), disabled=True)
    
    # --- Bố cục (Layout) ---
    def make_update_btn(field): return ft.ElevatedButton("Update", bgcolor="#232b39", color="#22c55e", width=90, height=36, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), side=ft.BorderSide(2, "#22c55e")), on_click=lambda e: on_update_click(field))
    
    # Left column - Profile info
    left_col = ft.Column([ft.Row([username, make_update_btn("username")]), ft.Row([fullname, make_update_btn("fullname")]), ft.Row([email]), ft.Row([phone, make_update_btn("phone")])], spacing=24, alignment=ft.MainAxisAlignment.START)
    
    # Right column - Additional info
    right_col = ft.Column([ft.Row([age, make_update_btn("age")]), ft.Row([gender, make_update_btn("gender")]), ft.Row([balance])], spacing=24, alignment=ft.MainAxisAlignment.START)
    
    # Password fields
    current_password_field = ft.TextField(
        label="Current Password",
        password=True,
        width=260,
        label_style=ft.TextStyle(color="#b0b0b0"),
        filled=True,
        fill_color="#232b39",
        border_color="#232b39",
        text_style=ft.TextStyle(color="white")
    )
    new_password_field = ft.TextField(
        label="New Password",
        password=True,
        width=260,
        label_style=ft.TextStyle(color="#b0b0b0"),
        filled=True,
        fill_color="#232b39",
        border_color="#232b39",
        text_style=ft.TextStyle(color="white")
    )
    confirm_password_field = ft.TextField(
        label="Confirm New Password",
        password=True,
        width=260,
        label_style=ft.TextStyle(color="#b0b0b0"),
        filled=True,
        fill_color="#232b39",
        border_color="#232b39",
        text_style=ft.TextStyle(color="white")
    )

    # Password change section
    if state.get("password_success"):
        # Show success message within the password section
        password_content = ft.Column([
            ft.Text(
                "Password changed successfully!",
                size=32,
                color="#22c55e",
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=24),
            ft.ElevatedButton(
                "OK",
                bgcolor="#22c55e",
                color="white",
                width=160,
                height=44,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=on_password_ok
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    else:
        # Show normal password change content
        password_error_text = ft.Text(state["password_error"], color="red", size=13) if state["password_error"] else ft.Container(height=0)
        password_content = ft.Column([
            ft.Text("Change Password", size=18, weight=ft.FontWeight.BOLD, color="#b0b0b0"),
            current_password_field,
            new_password_field,
            confirm_password_field,
            password_error_text,
            ft.Container(height=16),
            ft.ElevatedButton(
                "Change Password",
                bgcolor="#22c55e",
                color="white",
                width=260,
                height=44,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=on_change_password
            )
        ], spacing=16, alignment=ft.MainAxisAlignment.START)
    
    password_section = ft.Container(
        password_content,
        bgcolor="#232b39",
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=48, vertical=40),
        margin=ft.margin.only(top=24, bottom=24)
    )
    
    # Main form with profile and additional info, including Save button inside
    if state.get("show_success_message"):
        # Show success message within the form
        form_content = ft.Column([
            ft.Text(
                "Update successful!",
                size=32,
                color="#22c55e",
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=24),
            ft.ElevatedButton(
                "OK",
                bgcolor="#22c55e",
                color="white",
                width=160,
                height=44,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=on_ok
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    else:
        # Show normal form content
        edit_error_text = ft.Text(state["edit_error"], color="red", size=13) if state["edit_error"] else ft.Container(height=0)
        form_content = ft.Column([
            ft.Row([
                left_col, 
                ft.Container(width=40), 
                right_col
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
            edit_error_text,
            ft.Container(height=24),  # Spacer
            ft.Row([
                ft.Container(expand=True),
                ft.ElevatedButton("Save", bgcolor="#22c55e", color="white", width=180, height=44, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=on_save)
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=0)
    
    form = ft.Container(
        form_content,
        bgcolor="#232b39", 
        border_radius=16, 
        padding=ft.padding.symmetric(horizontal=60, vertical=50),  # Increased padding
        margin=ft.margin.only(top=24, bottom=24)
    )
    
    # Layout with form and password section side by side, centered on screen
    main_layout = ft.Row([
        ft.Container(expand=True),  # Left spacer
        form,
        ft.Container(width=60),  # Spacer between forms
        password_section,
        ft.Container(expand=True)   # Right spacer
    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START)
    
    # Only Delete account button outside
    btn_row = ft.Container(ft.Row([
        ft.Container(expand=True), 
        ft.ElevatedButton(
            "Delete account", 
            bgcolor="#e74c3c", color="white", width=180, height=44, 
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), 
            on_click=show_delete_dialog
        ),
        ft.Container(width=40)  # Thêm khoảng cách bên phải
    ], alignment=ft.MainAxisAlignment.END), margin=ft.margin.only(top=12))
    
    title = ft.Container(ft.ElevatedButton("Manage Account", style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="transparent", side=ft.BorderSide(2, "#22c55e"), shape=ft.RoundedRectangleBorder(radius=8), padding=ft.Padding(24, 12, 24, 12), text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=28)), disabled=True), alignment=ft.alignment.center, margin=ft.margin.only(bottom=24))
    main_content = ft.Column([title, main_layout, btn_row], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # Delete confirmation dialog
    if state.get("show_delete_dialog"):
        delete_dialog = ft.Column([
            ft.Text(
                "Confirm delete account?",
                size=40,
                color="white",
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=24),
            ft.Row([
                ft.ElevatedButton(
                    "Confirm",
                    bgcolor="#e74c3c",
                    color="white",
                    width=100,
                    height=36,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=confirm_delete_account
                ),
                ft.Container(width=12),
                ft.ElevatedButton(
                    "Cancel",
                    bgcolor="#22c55e",
                    color="white",
                    width=100,
                    height=36,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=cancel_delete_account
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        return ft.Container(
            content=ft.Column([
                ft.Container(expand=True),
                delete_dialog,
                ft.Container(expand=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            height=page.height,
            padding=ft.padding.only(top=40, bottom=0)
        )

    return ft.Container(content=ft.Column([main_content, ft.Container(expand=True), footer], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True), expand=True, height=page.height, padding=ft.padding.only(top=40, bottom=0))
