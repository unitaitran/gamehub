import flet as ft
from ...backend.payment_be import get_user_balance, update_user_balance

def payment_screen(page, state, render, footer):
    # Get current user balance from database
    def get_current_user_balance():
        current_username = state.get("username", "admin")
        result = get_user_balance(current_username)
        if result["success"]:
            return result["balance"]
        return 0.0

    # Title
    title = ft.Container(
        ft.ElevatedButton(
            "Deposit",
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor="transparent",
                side=ft.BorderSide(2, "#22c55e"),
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding(24, 12, 24, 12),
                text_style=ft.TextStyle(
                    weight=ft.FontWeight.BOLD,
                    size=28,
                ),
            ),
            disabled=True
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(bottom=32, top=32)
    )

    # Denominations in USD and QR images
    denominations = [
        "$4.99", "$9.99", "$19.99",
        "$49.99", "$69.99", "$99.99"
    ]
    qr_images = {
        "$4.99": "https://useless-gold-stingray.myfilebase.com/ipfs/QmQdK7w4zzMDchZEcnK2sBrwjufWagzyCpJdouT6J4AZ5w",
        "$9.99": "https://useless-gold-stingray.myfilebase.com/ipfs/QmQs4Y5abs7pgmeCbN2dm5isB2qSmG9yT6GmV37biZJobe",
        "$19.99": "https://useless-gold-stingray.myfilebase.com/ipfs/QmVNPJrjftQ3aKAymST65pgGR33ASEvBAiH8SxdZ3KZMF8",
        "$49.99": "https://useless-gold-stingray.myfilebase.com/ipfs/QmQjXf4m4uJQL8crDm4zENtmm3r6h9pe6UpQxboQjhhFbg",
        "$69.99": "https://useless-gold-stingray.myfilebase.com/ipfs/QmcvcP7ZJThxnZFDkL8Q6JTfACt5HKimkxk8fEGGGxxeYy",
        "$99.99": "https://useless-gold-stingray.myfilebase.com/ipfs/QmcuquyE8dNj4E21KDQipZrhrD7TFbRnYSChsUxzmSwq5Y",
    }
    bank_info = {
        "$4.99": {"bank": "MB Bank", "member": "090520036666", "name": "BUI TRUNG DUC"},
        "$9.99": {"bank": "MB Bank", "member": "090520036666", "name": "BUI TRUNG DUC"},
        "$19.99": {"bank": "MB Bank", "member": "090520036666", "name": "BUI TRUNG DUC"},
        "$49.99": {"bank": "MB Bank", "member": "090520036666", "name": "BUI TRUNG DUC"},
        "$69.99": {"bank": "MB Bank", "member": "090520036666", "name": "BUI TRUNG DUC"},
        "$99.99": {"bank": "MB Bank", "member": "090520036666", "name": "BUI TRUNG DUC"},
    }

    # Initialize state variables
    if "selected_denom" not in state:
        state["selected_denom"] = None
    if "show_payment" not in state:
        state["show_payment"] = False
    if "show_success_dialog" not in state:
        state["show_success_dialog"] = False
    if "show_success_message" not in state:
        state["show_success_message"] = False
    if "show_balance" not in state:
        state["show_balance"] = False

    def toggle_balance(e):
        state["show_balance"] = not state["show_balance"]
        render()

    def select_denom(denom):
        state["selected_denom"] = denom
        state["show_payment"] = False
        render()

    def on_add_funds(e):
        state["show_payment"] = True
        render()

    def confirm_payment():
        current_username = state.get("username", "admin")
        denom = state["selected_denom"]
        if denom:
            amount_usd = round(float(denom.replace("$", "")), 0)
            result = update_user_balance(current_username, amount_usd)  
            if result["success"]:
                state["show_success_message"] = True
                state["show_success_dialog"] = True
                render()
            else:
                print(f"Payment failed: {result['message']}")

    def close_success_dialog(e=None):
        state["show_success_dialog"] = False
        state["show_success_message"] = False
        state["selected_denom"] = None
        state["show_payment"] = False
        page.dialog = None
        page.update()

    denom_buttons = []
    for d in denominations:
        selected = state["selected_denom"] == d
        denom_buttons.append(
            ft.ElevatedButton(
                d,
                style=ft.ButtonStyle(
                    color="white" if selected else ft.Colors.WHITE,
                    bgcolor="#22c55e" if selected else "transparent",
                    side=ft.BorderSide(2, "#22c55e"),
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(0, 8, 0, 8),
                    text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=18),
                ),
                width=120,
                height=48,
                on_click=lambda e, d=d: select_denom(d)
            )
        )

    # Deposit box
    deposit_box = ft.Container(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ATTACH_MONEY, color=ft.Colors.WHITE, size=28),
                ft.Text("Select deposit amount:", size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Text(
                    f"Balance: ${get_current_user_balance():.2f}" if state["show_balance"] else "Balance: ********", 
                    size=16, 
                    color=ft.Colors.WHITE
                ),
                ft.IconButton(
                    icon=ft.Icons.VISIBILITY_OFF if state["show_balance"] else ft.Icons.VISIBILITY,
                    icon_color=ft.Colors.WHITE,
                    icon_size=20,
                    on_click=toggle_balance
                )
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=16),
            ft.Row(denom_buttons[:3], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
            ft.Row(denom_buttons[3:], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
            ft.Container(height=16),
            ft.ElevatedButton(
                "Add funds",
                bgcolor="#22c55e",
                color="white",
                width=180,
                height=44,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                disabled=state["selected_denom"] is None,
                on_click=on_add_funds
            ),
            ft.Container(height=16),
            ft.Text(
                "Note:\nPlease enter the exact transfer description so the system can verify and activate your top-up automatically.\nYour account will be credited within 1 to 5 minutes.\nIf the funds have not been added after 5 minutes, please contact us via Facebook for support.",
                size=12, color="#b0b0b0"
            )
        ], alignment=ft.MainAxisAlignment.START),
        bgcolor="#232b39",
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=32, vertical=28),
        width=500,
        border=ft.border.all(1, "#333"),
        margin=ft.margin.only(right=32)
    )

    # Right box: selection or payment interface
    if not state["show_payment"]:
        right_box = ft.Container(
            ft.Text(
                "Please select denomination!!!",
                size=20,
                color="#b0b0b0",
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            bgcolor="#232b39",
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=32, vertical=32),
            width=380,
            alignment=ft.alignment.center
        )
    elif state.get("show_success_message"):
        def on_ok(e):
            state["show_success_message"] = False
            state["show_payment"] = False
            state["selected_denom"] = None
            render()
        # Khi thanh toán thành công, không hiển thị right_box
        right_box = ft.Container(width=0, height=0)
    else:
        denom = state["selected_denom"]
        info = bank_info.get(denom, {"bank": "", "member": "", "name": ""})
        right_box = ft.Container(
            ft.Column([
                ft.Text("Payment Information", size=22, weight=ft.FontWeight.BOLD, color="#22c55e", text_align=ft.TextAlign.CENTER),
                ft.Container(height=16),
                ft.Row([
                    ft.Text("Amount:", size=18, color=ft.Colors.WHITE),
                    ft.Text(denom, size=18, color="#22c55e", weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=12),
                ft.Row([
                    ft.Text("Bank:", size=16, color="#b0b0b0"),
                    ft.Container(width=8),
                    ft.Text(info["bank"], size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Row([
                    ft.Text("Member:", size=16, color="#b0b0b0"),
                    ft.Container(width=8),
                    ft.Text(info["member"], size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Row([
                    ft.Text("Name:", size=16, color="#b0b0b0"),
                    ft.Container(width=8),
                    ft.Text(info["name"], size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=16),
                ft.Text("Scan the QR code below to pay:", size=14, color="#b0b0b0", text_align=ft.TextAlign.CENTER),
                ft.Container(height=12),
                ft.Image(src=qr_images.get(denom, "qr_default.png"), width=180, height=180, fit=ft.ImageFit.CONTAIN),
                ft.Container(height=16),
                ft.ElevatedButton(
                    "Confirm",
                    bgcolor="#22c55e",
                    color="white",
                    width=160,
                    height=44,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=lambda e: confirm_payment()
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#232b39",
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=32, vertical=32),
            width=380,
            alignment=ft.alignment.center
        )

    # Success dialog
    if state.get("show_success_dialog"):
        def on_ok(e):
            close_success_dialog()

        success_dialog = ft.AlertDialog(
            open=True,
            modal=True,
            bgcolor="#232b39",
            content=ft.Container(
                ft.Column([
                    ft.Text("Payment successful", size=24, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=2, thickness=2, color="#22c55e"),
                    ft.Container(height=24),
                    ft.Text("✔", size=80, color="#22c55e", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=24),
                    ft.ElevatedButton(
                        "OK",
                        bgcolor="#22c55e",
                        color="white",
                        width=120,
                        height=40,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=on_ok
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=32,
                width=320
            ),
        )
        page.dialog = success_dialog
        page.update()
    else:
        page.dialog = None
        page.update()

    # Nếu thanh toán thành công, hiển thị thông báo thành công ở giữa màn hình
    if state.get("show_success_message"):
        def on_ok(e):
            state["show_success_message"] = False
            state["show_payment"] = False
            state["selected_denom"] = None
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
    else:
        return ft.Container(
            content=ft.Column(
                [
                    title,
                    ft.Row([
                        deposit_box,
                        right_box
                    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START),
                    ft.Container(height=56),  # Thêm khoảng cách trước footer
                    footer
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            ),
            expand=True
        )
