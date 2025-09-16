# app.py
import pygame
from client import config
from client.ui.menu import Menu
from client.ui.login import Login
from client.ui.setting_menu import SettingsMenu

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Game Client")

    running = True
    while running:
        # Show menu and get the user's choice
        menu = Menu(screen)
        choice = menu.run()  # returns one of: "start", "settings", "exit"

        if choice == "exit" or choice is None:
            running = False
            break

        if choice == "settings":
            settings = SettingsMenu(screen)
            settings.run()
            # after settings applied the config.SCREEN_* may have changed
            screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        elif choice == "start":
            login_screen = Login(screen)
            result = login_screen.run()  # returns selected character dict, or None if cancelled/back
            if result and isinstance(result, dict) and result.get("selected_character"):
                selected = result["selected_character"]
                print("Player picked:", selected)
                # TODO: start the actual game world here (pass client, selected char, etc)
                # For now just exit the loop to demonstrate flow:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()
