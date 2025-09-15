import pygame
from client import config
from client.ui.login import Login
from client.ui.setting_menu import SettingsMenu

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.options = config.MENU_OPTIONS
        self.selected = 0

        # Load background
        self.bg_img_orig = pygame.image.load("client/data/assets/images/menu_bg.png").convert_alpha()
        self.bg_img = pygame.transform.scale(self.bg_img_orig, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Font size proportional to screen height
        self.font = pygame.font.SysFont(config.FONT_NAME, max(20, int(config.SCREEN_HEIGHT * 0.04)))

    def draw(self):
        # Draw background scaled to current screen size
        self.bg_img = pygame.transform.scale(self.bg_img_orig, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.screen.blit(self.bg_img, (0, 0))

        # Draw options
        center_x = config.SCREEN_WIDTH // 2
        center_y = config.SCREEN_HEIGHT // 2
        spacing = max(40, int(config.SCREEN_HEIGHT * 0.06))

        for i, option in enumerate(self.options):
            color = (50, 150, 255) if i == self.selected else (255, 255, 255)
            text_surface = self.font.render(option, True, color)
            rect = text_surface.get_rect(center=(center_x, center_y + i * spacing))
            self.screen.blit(text_surface, rect)

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
                        elif option == "Settings":
                            settings = SettingsMenu(self.screen)
                            settings.run()
                            # Refresh screen, font, and background after changing resolution
                            self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
                            self.font = pygame.font.SysFont(config.FONT_NAME, max(20, int(config.SCREEN_HEIGHT * 0.04)))
                            self.bg_img = pygame.transform.scale(self.bg_img_orig, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
                        elif option == "Exit":
                            running = False

            clock.tick(config.FPS)
