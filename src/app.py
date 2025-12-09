import flet as ft

from .frontend.screens.screens_login import login_screen
from .frontend.screens.home import HomeScreen, build_menu_row, build_footer
from .frontend.screens.screens_register import register_screen
from .frontend.screens.screens_forgot import forgot_screen
from .frontend.screens.account import account_screen
from .frontend.screens.purchase_history import purchase_history_screen
from .frontend.screens.privacy_policy import privacy_policy_screen
from .frontend.screens.terms_of_use import terms_of_use_screen
from .frontend.screens.about_us import about_us_screen
from .frontend.screens.contact_us import contact_us_screen
from .frontend.screens.ai_chat import ai_chat_screen




def main(page: ft.Page):
    page.title = "GameHub"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0f1419"
    page.padding = 0
    page.spacing = 0

    def render():
        page.controls.clear()
        if state["screen"] == "login":
            login_screen(page, state, render)
            page.update()
            return
        elif state["screen"] == "register":
            register_screen(page, state, render)
            page.update()
            return
        elif state["screen"] == "forgot":
            forgot_screen(page, state, render)
            page.update()
            return
        elif state["screen"] == "home":
            HomeScreen(page, state, render)
            page.update()
            return
        elif state["screen"] == "account":
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
            page.add(
                build_menu_row(state, render, set_home, handle_menu, None, None),
                account_screen(page, state, render, build_footer(set_terms, set_privacy, set_home))
            )
            page.update()
            return
        elif state["screen"] == "payment":
            from .frontend.screens.payment import payment_screen
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
            page.add(
                build_menu_row(state, render, set_home, handle_menu, None, None),
                payment_screen(page, state, render, build_footer(set_terms, set_privacy, set_home))
            )
            page.update()
            return
        elif state["screen"] == "cart":
            from .frontend.screens.cart import cart_screen
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
            page.add(
                build_menu_row(state, render, set_home, handle_menu, None, None),
                cart_screen(page, state, render, build_footer(set_terms, set_privacy, set_home))
            )
            page.update()
            return
        elif state["screen"] == "history":
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
            page.add(
                build_menu_row(state, render, set_home, handle_menu, None, None, set_about_us, set_contact_us),
                purchase_history_screen(page, state, render, build_footer(set_terms, set_privacy, set_home))
            )
            page.update()
            return
        elif state["screen"] == "about_us":
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
            page.add(
                build_menu_row(state, render, set_home, handle_menu, None, None, set_about_us, set_contact_us),
                about_us_screen(page, state, render, build_footer(set_terms, set_privacy, set_home, set_about_us, set_contact_us))
            )
            page.update()
            return
        elif state["screen"] == "contact_us":
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
            page.add(
                build_menu_row(state, render, set_home, handle_menu, None, None, set_about_us, set_contact_us),
                contact_us_screen(page, state, render, build_footer(set_terms, set_privacy, set_home, set_about_us, set_contact_us))
            )
            page.update()
            return
        elif state["screen"] == "privacy_policy":
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
            footer = build_footer(set_terms, set_privacy, set_home, set_about_us, set_contact_us)
            page.add(
                build_menu_row(state, render, set_home, handle_menu, None, None, set_about_us, set_contact_us),
                privacy_policy_screen(page, state, render, footer)
            )
            page.update()
            return
        elif state["screen"] == "terms_of_use":
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
            footer = build_footer(set_terms, set_privacy, set_home, set_about_us, set_contact_us)
            page.add(
                build_menu_row(state, render, set_home, handle_menu, None, None, set_about_us, set_contact_us),
                terms_of_use_screen(page, state, render, footer)
            )
            page.update()
            return
        elif state["screen"] == "game_detail":
            from .frontend.screens.game_detail import game_detail_screen
            game_detail_screen(page, state, render)
            return
        elif state["screen"] == "admin":
            from .frontend.screens.admin_interface import admin_interface_screen
            admin_interface_screen(page, state, render)
            page.update()
            return
        elif state["screen"] == "add_game":
            from .frontend.screens.add_game import add_game_screen
            add_game_screen(page, state, render)
            page.update()
            return
        elif state["screen"] == "edit_game":
            from .frontend.screens.edit_game import edit_game_screen
            edit_game_screen(page, state, render)
            page.update()
            return
        elif state["screen"] == "confirm_delete":
            from .frontend.screens.confirm_delete import confirm_delete_screen
            confirm_delete_screen(page, state, render)
            page.update()
            return
        elif state["screen"] == "allgame":
            from .frontend.screens.allgame import allgame_screen
            allgame_screen(page, state, render)
            page.update()
            return
        elif state["screen"] == "ai_chat":
            page.add(ai_chat_screen(page, state, render))
            page.update()
            return

    state = {
        "screen": "login",
        "login_error": "",
        "login_email": "",
        "login_password": "",
        "username": "",
        "cart_selected": {}
    }

    render()

if __name__ == "__main__":
    ft.app(target=main) 