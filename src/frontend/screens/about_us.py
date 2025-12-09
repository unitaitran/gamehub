import flet as ft

def about_us_screen(page, state, render, footer):
    def set_home(e=None):
        state["screen"] = "home"
        render()
    
    def set_privacy(e=None):
        state["screen"] = "privacy"
        render()
    
    def set_terms(e=None):
        state["screen"] = "terms"
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
                    "About us",
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
            
            # Section 1: About Us - Game Hub
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
                            "1. About Us – Game Hub",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    ft.Container(
                        ft.Text(
                            "Welcome to Game Hub – your ultimate destination for discovering, purchasing, and enjoying your favorite games.",
                            size=16,
                            color=ft.Colors.WHITE,
                            width=800
                        ),
                        margin=ft.margin.only(left=20, top=16, bottom=32)
                    )
                ]),
                margin=ft.margin.only(bottom=32)
            ),
            
            # Section 2: Who We Are
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
                            "2. Who We Are",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    ft.Container(
                        ft.Text(
                            "Game Hub was created by a passionate team of student interns from CampusLink, an internship program hosted by FPT Software. Born out of curiosity and a love for gaming, our mission is to reshape how gamers explore and buy games through an intelligent, user-centric platform.",
                            size=16,
                            color=ft.Colors.WHITE,
                            width=800
                        ),
                        margin=ft.margin.only(left=20, top=16, bottom=32)
                    )
                ]),
                margin=ft.margin.only(bottom=32)
            ),
            
            # Section 3: Our Vision
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
                            "3. Our Vision",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    ft.Container(
                        ft.Text(
                            "We aim to become the go-to digital storefront for gamers in Vietnam and beyond – combining smart technology, community-driven insights, and seamless experiences into one powerful app.",
                            size=16,
                            color=ft.Colors.WHITE,
                            width=800
                        ),
                        margin=ft.margin.only(left=20, top=16, bottom=32)
                    )
                ]),
                margin=ft.margin.only(bottom=32)
            ),
            
            # Section 4: What Makes Us Different?
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
                            "What Makes Us Different?",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    ft.Container(
                        ft.Column([
                            ft.Text(
                                "Game Hub isn't just a store – it's a smart recommendation engine:",
                                size=16,
                                color=ft.Colors.WHITE,
                                width=800
                            ),
                            ft.Container(height=16),
                            ft.Text(
                                "• **Personalized Suggestions:** Based on your purchase history, we recommend games you'll likely enjoy.",
                                size=16,
                                color=ft.Colors.WHITE,
                                width=800
                            ),
                            ft.Text(
                                "• **Trending Market Picks:** Discover hot titles inspired by current gaming trends.",
                                size=16,
                                color=ft.Colors.WHITE,
                                width=800
                            ),
                            ft.Text(
                                "• **Community Insights:** See what other gamers with similar interests are playing and loving.",
                                size=16,
                                color=ft.Colors.WHITE,
                                width=800
                            )
                        ]),
                        margin=ft.margin.only(left=20, top=16, bottom=32)
                    )
                ]),
                margin=ft.margin.only(bottom=32)
            ),
            
            # Section 5: Built by Interns, Backed by Innovation
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
                            "Built by Interns, Backed by Innovation",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    ft.Container(
                        ft.Text(
                            "This app is a real-world project powered by innovation and hands-on learning. As part of FPT Software's commitment to fostering young talent, Game Hub is a shining example of what students can achieve when given the tools and trust to build something meaningful.",
                            size=16,
                            color=ft.Colors.WHITE,
                            width=800
                        ),
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