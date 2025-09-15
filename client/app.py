import pygame
from client import config
from client.ui.menu import Menu

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Game Client")

    menu = Menu(screen)
    menu.run()  # calls the run method defined above

    pygame.quit()

if __name__ == "__main__":
    main()
