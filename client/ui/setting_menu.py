import os
import pygame
from client import config

class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen

        # Load background (keep original for scaling)
        self.bg_img_orig = pygame.image.load("client/data/assets/images/settings_bg.png").convert()
        self.bg_img = pygame.transform.scale(self.bg_img_orig, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Font proportional to screen height
        self.font = pygame.font.SysFont(config.FONT_NAME, max(20, int(config.SCREEN_HEIGHT * 0.04)))

        # Main options
        self.options = ["Screen Mode", "Resolution", "Music", "Sound", "Apply Changes", "Restore Defaults", "Return to Title", "Quit"]
        self.selected_index = 0

        # Resolution choices
        self.resolutions = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
        self.current_resolution_index = next(
            (i for i, r in enumerate(self.resolutions) if r == (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)), 0
        )

        # Store rectangles for mouse interaction
        self.option_rects = []

    def center_window(self, width, height):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.display.set_mode((width, height))

    def draw(self):
        # Scale background dynamically
        self.bg_img = pygame.transform.scale(self.bg_img_orig, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.screen.blit(self.bg_img, (0, 0))

        # Compute vertical spacing dynamically
        center_x = config.SCREEN_WIDTH // 2
        center_y = config.SCREEN_HEIGHT // 2
        spacing = max(50, int(config.SCREEN_HEIGHT * 0.07))

        self.option_rects = []

        for i, option in enumerate(self.options):
            # Highlight selected option
            color = (50, 150, 255) if i == self.selected_index else (255, 255, 255)
            text_surface = self.font.render(option, True, color)
            rect = text_surface.get_rect(center=(center_x, center_y + i * spacing))
            self.screen.blit(text_surface, rect)
            self.option_rects.append((option, rect))

            # Draw current resolution next to "Resolution"
            if option == "Resolution":
                res_text = f"{self.resolutions[self.current_resolution_index][0]}x{self.resolutions[self.current_resolution_index][1]}"
                res_surface = self.font.render(res_text, True, (200, 200, 0))
                self.screen.blit(res_surface, (rect.right + 20, rect.y))

        pygame.display.flip()

    def save_config(self):
        """Save current resolution to config.py."""
        try:
            config_path = "client/config.py"
            with open(config_path, "r") as f:
                lines = f.readlines()

            # Replace SCREEN_WIDTH and SCREEN_HEIGHT lines
            for i, line in enumerate(lines):
                if line.startswith("SCREEN_WIDTH"):
                    lines[i] = f"SCREEN_WIDTH = {config.SCREEN_WIDTH}\n"
                elif line.startswith("SCREEN_HEIGHT"):
                    lines[i] = f"SCREEN_HEIGHT = {config.SCREEN_HEIGHT}\n"

            # Write back
            with open(config_path, "w") as f:
                f.writelines(lines)

            print(f"Configuration saved: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}")
        except Exception as e:
            print("Error saving config:", e)

    def apply_resolution(self):
        new_width, new_height = self.resolutions[self.current_resolution_index]
        config.SCREEN_WIDTH = new_width
        config.SCREEN_HEIGHT = new_height

        # Center the window on the desktop
        os.environ['SDL_VIDEO_CENTERED'] = '1'

        # Reset the main screen
        self.screen = pygame.display.set_mode((new_width, new_height))

        # Rescale background
        self.bg_img = pygame.transform.scale(self.bg_img_orig, (new_width, new_height))

        # Update font size
        self.font = pygame.font.SysFont(config.FONT_NAME, max(20, int(config.SCREEN_HEIGHT * 0.04)))

        print(f"Applied new resolution: {new_width}x{new_height}")
        if hasattr(self, "window_rect"):
            self.window_rect.center = (new_width // 2, new_height // 2)

        # Save to config file
        self.save_config()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.draw()

            # Check mouse position for hover selection
            mouse_pos = pygame.mouse.get_pos()
            for i, (_, rect) in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                    elif event.key == pygame.K_LEFT:
                        if self.options[self.selected_index] == "Resolution":
                            self.current_resolution_index = (self.current_resolution_index - 1) % len(self.resolutions)
                    elif event.key == pygame.K_RIGHT:
                        if self.options[self.selected_index] == "Resolution":
                            self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
                    elif event.key == pygame.K_RETURN:
                        selected_option = self.options[self.selected_index]
                        if selected_option == "Apply Changes":
                            self.apply_resolution()
                        elif selected_option == "Return to Title":
                            running = False
                        elif selected_option == "Quit":
                            return "exit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for i, (option, rect) in enumerate(self.option_rects):
                        if rect.collidepoint(mouse_pos):
                            self.selected_index = i
                            if option == "Resolution":
                                if event.button == 1:  # Left click
                                    self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
                                elif event.button == 3:  # Right click
                                    self.current_resolution_index = (self.current_resolution_index - 1) % len(self.resolutions)
                            elif option == "Apply Changes":
                                self.apply_resolution()
                            elif option == "Return to Title":
                                running = False
                            elif option == "Quit":
                                return "exit"

            clock.tick(config.FPS)

        return "return"