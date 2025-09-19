# app.py
import pygame
from client import config
from client.ui.menu import Menu
from client.ui.login import Login
from client.ui.setting_menu import SettingsMenu
from client.ui.character_selection import CharacterSelection

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Game Client")

    # Create Login instance once to keep login state
    login_screen = Login(screen)

    running = True
    while running:
        # Show main menu
        menu = Menu(screen)
        choice = menu.run()  # returns "start", "settings", "exit"

        if choice in ("exit", None):
            running = False
            break

        elif choice == "settings":
            settings = SettingsMenu(screen)
            settings.run()
            # Reapply screen size if changed
            screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            login_screen = Login(screen)

        elif choice == "start":
            # If already logged in with characters, go straight to character selection
            if login_screen.logged_in and login_screen.characters:
                selected = CharacterSelection(screen, login_screen.characters).run()
                if selected in ("cancel", "menu", None):
                    continue  # back to main menu

                if isinstance(selected, dict):
                    print("Player picked:", selected)
                    running = False
                    break
                else:
                    # Cancelled character selection -> back to menu
                    continue

            # Otherwise, show login screen
            result = login_screen.run()  # returns {"selected_character": ...} or None

            if login_screen.logged_in:
                print("User is logged in.")
            elif result is None:
                print("User cancelled or closed the login screen.")
                continue  # back to main menu

            # Check if character was selected
            if result and isinstance(result, dict) and result.get("selected_character"):
                selected = result["selected_character"]
                print("Player picked:", selected)
                # TODO: launch actual game world
                running = False
                break

    pygame.quit()


if __name__ == "__main__":
    main()
