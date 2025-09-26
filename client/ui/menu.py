import pygame
from client.data import config
from client.ui.login import Login
from client.ui.setting_menu import SettingsMenu

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Start", "Settings", "Exit"]
        self.selected = 0

        # Load background
        self.bg_img_orig = pygame.image.load("client/assets/images/ui/menu_bg.png").convert_alpha()
        self.bg_img = pygame.transform.scale(self.bg_img_orig, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.last_size = (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

        # Font size proportional to screen height
        self.font = pygame.font.SysFont(config.FONT_NAME, max(20, int(config.SCREEN_HEIGHT * 0.04)))

        # Store rectangles for mouse click and hover detection
        self.last_mouse_pos = pygame.mouse.get_pos() # Track last mouse pos
        self.option_rects = []

    def draw(self):
        # Draw background scaled to current screen size
        current_size = (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        if current_size != self.last_size:
            self.bg_img = pygame.transform.scale(self.bg_img_orig, current_size)
            self.font = pygame.font.SysFont(config.FONT_NAME, max(20, int(config.SCREEN_HEIGHT * 0.04)))
            self.last_size = current_size

            # Draw background scaled to current screen size
        self.screen.blit(self.bg_img, (0, 0))

        # Draw options and store their rectangles
        self.option_rects.clear()  # Clear previous rectangles
        center_x = config.SCREEN_WIDTH // 2
        center_y = config.SCREEN_HEIGHT // 2
        spacing = max(40, int(config.SCREEN_HEIGHT * 0.06))

        for i, option in enumerate(self.options):
            color = (50, 150, 255) if i == self.selected else (255, 255, 255)
            text_surface = self.font.render(option, True, color)
            rect = text_surface.get_rect(center=(center_x, center_y + i * spacing))
            self.screen.blit(text_surface, rect)
            self.option_rects.append((option, rect))  # Store option and its rectangle

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.draw()

            # Check mouse position for hover selection
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos != self.last_mouse_pos:
                for i, (_, rect) in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected = i
                        break
                self.last_mouse_pos = mouse_pos

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        option = self.options[self.selected]
                        if option == "Start":
                            return "start"
                        elif option == "Settings":
                            return "settings"
                        elif option == "Exit":
                            return "exit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = event.pos
                        for i, (option, rect) in enumerate(self.option_rects):
                            if rect.collidepoint(mouse_pos):
                                self.selected = i  # Update selected option
                                if option == "Start":
                                    return "start"
                                elif option == "Settings":
                                    return "settings"
                                elif option == "Exit":
                                    return "exit"

            clock.tick(config.FPS)

        return None