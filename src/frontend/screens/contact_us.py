import flet as ft

def contact_us_screen(page, state, render, footer):
    def set_home(e=None):
        state["screen"] = "home"
        render()
    
    def set_privacy(e=None):
        state["screen"] = "privacy_policy"
        render()
    
    def set_terms(e=None):
        state["screen"] = "terms_of_use"
        render()
    
    def handle_menu(action):
        if action == "home":
            state["screen"] = "home"
        elif action == "cart":
            state["screen"] = "cart"
        elif action == "history":
            state["screen"] = "history"
        elif action == "account":
            state["screen"] = "account"
        elif action == "payment":
            state["screen"] = "payment"
        elif action == "logout":
            state["screen"] = "login"
        elif action == "allgame":
            state["screen"] = "allgame"
        elif action == "ai_chat":
            state["screen"] = "ai_chat"
        render()

    # Top green accent bar
    top_accent = ft.Container(
        width=1200,
        height=4,
        bgcolor="#22c55e",
        margin=ft.margin.only(bottom=40)
    )

    # Main content
    content = ft.Container(
        ft.Column([
            # Title
            ft.Container(
                ft.Text(
                    "Contact us",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                border=ft.border.all(1, "#b0b0b0"),
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=40, vertical=20),
                margin=ft.margin.only(bottom=40)
            ),
            
            # Introduction
            ft.Container(
                ft.Text(
                    "We're here to support you — whether you're looking for help, feedback, or partnership opportunities. Get in touch with the Game Hub team anytime!",
                    size=16,
                    color=ft.Colors.WHITE,
                    width=800,
                    text_align=ft.TextAlign.CENTER
                ),
                margin=ft.margin.only(bottom=40)
            ),
            
            # Office Address section
            ft.Container(
                ft.Column([
                    ft.Row([
                        ft.Container(
                            width=4,
                            height=28,
                            bgcolor="#22c55e",
                            margin=ft.margin.only(right=16)
                        ),
                        ft.Text(
                            "Office Address",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    ft.Container(
                        ft.Column([
                            ft.Text("FPT University", size=16, color=ft.Colors.WHITE),
                            ft.Text("Hoa Lac Hi-Tech Park", size=16, color=ft.Colors.WHITE),
                            ft.Text("Thach That District, Hanoi, Vietnam", size=16, color=ft.Colors.WHITE)
                        ], spacing=8),
                        margin=ft.margin.only(left=20, top=16, bottom=32)
                    )
                ]),
                margin=ft.margin.only(bottom=32)
            ),
            
            # Contact Channels section
            ft.Container(
                ft.Column([
                    ft.Row([
                        ft.Container(
                            width=4,
                            height=28,
                            bgcolor="#22c55e",
                            margin=ft.margin.only(right=16)
                        ),
                        ft.Text(
                            "Contact Channels",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    ft.Container(
                        ft.Column([
                            ft.Text("Phone: +84 919 554 393", size=16, color=ft.Colors.WHITE),
                            ft.Text("Email: gamehubfpt@gmail.com", size=16, color=ft.Colors.WHITE),
                            ft.Container(height=16),
                            ft.Text("Working Hours:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Row([
                                ft.Icon(ft.Icons.CIRCLE, color="#e74c3c", size=12),
                                ft.Text("Monday-Friday: 9:00 AM - 5:00 PM (GMT+7)", size=16, color=ft.Colors.WHITE)
                            ], spacing=8),
                            ft.Row([
                                ft.Icon(ft.Icons.CIRCLE, color="#b0b0b0", size=12),
                                ft.Text("Saturday & Sunday: Closed", size=16, color=ft.Colors.WHITE)
                            ], spacing=8),
                            ft.Container(height=8),
                            ft.Text("Response Time: Within 24 business hours", size=16, color=ft.Colors.WHITE)
                        ], spacing=8),
                        margin=ft.margin.only(left=20, top=16, bottom=32)
                    )
                ]),
                margin=ft.margin.only(bottom=32)
            ),
            
            # What Can We Help You With section
            ft.Container(
                ft.Column([
                    ft.Row([
                        ft.Container(
                            width=4,
                            height=28,
                            bgcolor="#22c55e",
                            margin=ft.margin.only(right=16)
                        ),
                        ft.Text(
                            "What Can We Help You With?",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    ft.Container(
                        ft.Column([
                            ft.Text("• Technical Support", size=16, color=ft.Colors.WHITE),
                            ft.Text("• Billing Inquiries", size=16, color=ft.Colors.WHITE),
                            ft.Text("• Game Recommendations", size=16, color=ft.Colors.WHITE),
                            ft.Text("• Partnerships & Careers", size=16, color=ft.Colors.WHITE)
                        ], spacing=8),
                        margin=ft.margin.only(left=20, top=16, bottom=32)
                    )
                ]),
                margin=ft.margin.only(bottom=32)
            ),
            
            # FAQs section
            ft.Container(
                ft.Column([
                    ft.Row([
                        ft.Container(
                            width=4,
                            height=28,
                            bgcolor="#22c55e",
                            margin=ft.margin.only(right=16)
                        ),
                        ft.Text(
                            "Frequently Asked Questions (FAQs)",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    ft.Container(
                        ft.Column([
                            ft.Text("Q: Can I get a refund for a game I purchased?", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("A: Yes, we offer refunds within 14 days of purchase if you haven't played the game for more than 2 hours.", size=16, color=ft.Colors.WHITE),
                            ft.Container(height=16),
                            ft.Text("Q: How do I get personalized game recommendations?", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("A: Our AI analyzes your purchase history and gaming preferences to suggest games you'll likely enjoy.", size=16, color=ft.Colors.WHITE),
                            ft.Container(height=16),
                            ft.Text("Q: Is Game Hub available on mobile devices?", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("A: Android app is available now. iOS version coming soon!", size=16, color=ft.Colors.WHITE)
                        ], spacing=8),
                        margin=ft.margin.only(left=20, top=16, bottom=32)
                    )
                ]),
                margin=ft.margin.only(bottom=32)
            ),
            
            # Footer text
            ft.Container(
                ft.Column([
                    ft.Text(
                        "Let us power your play.",
                        size=16,
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER,
                        width=800
                    ),
                    ft.Text(
                        "Game Hub – Powered by Passion, Driven by Play.",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER,
                        width=800
                    )
                ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                margin=ft.margin.only(top=20)
            )
            
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#232b39",
        padding=ft.padding.all(40),
        border_radius=12,
        width=1000,
        margin=ft.margin.symmetric(horizontal=40, vertical=24)
    )

    return ft.Container(
        ft.Column([
            top_accent,
            content,
            footer
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll="auto"),
        expand=True
    ) 