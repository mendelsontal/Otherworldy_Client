import pygame
from client import config
from client.ui.login import Login

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE)
        self.options = config.MENU_OPTIONS
        self.selected = 0

    def draw(self):
        self.screen.fill((30, 30, 30))
        for i, option in enumerate(self.options):
            color = (50, 150, 255) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(config.SCREEN_WIDTH//2, config.SCREEN_HEIGHT//2 + i*60))
            self.screen.blit(text, rect)
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        option = self.options[self.selected]
                        if option == "Start":
                            login_screen = Login(self.screen)
                            login_screen.run()
                        elif option == "Register":
                            print("Register selected")
                        elif option == "Settings":
                            print("Settings selected")
                        elif option == "Exit":
                            running = False
            clock.tick(config.FPS)
