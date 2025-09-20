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
        font_path = "client/data/assets/fonts/cinzel.decorative-black.ttf"
        self.font = pygame.font.Font(font_path, max(20, int(config.SCREEN_HEIGHT * 0.04)))

        # Main options
        self.options = ["Screen Mode", "Resolution", "Music", "Sound", "Return to Title", "Apply Changes"]
        self.selected_index = 0

        # Resolution choices
        self.resolutions = [(800, 600), (1024, 768), (1280, 720), (1920, 1080), (2560, 1440)]
        self.current_resolution_index = next(
            (i for i, r in enumerate(self.resolutions) if r == (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)), 0
        )

        # Screen Mode choices
        self.screen_mode = ["Window", "Full Screen"]
        self.current_screen_mode_index = next(
            (i for i, r in enumerate(self.screen_mode) if r == config.SCREEN_MODE), 0
        )

        # Store rectangles for mouse interaction
        self.last_mouse_pos = pygame.mouse.get_pos() # Track last mouse pos
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
        spacing = max(50, int(config.SCREEN_HEIGHT * 0.07))
        start_y = int(config.SCREEN_HEIGHT * 0.3)
        menu_height = len(self.options) * spacing

        # --- Boxed semi-transparent panel ---
        panel_width = int(config.SCREEN_WIDTH * 0.6)
        panel_height = menu_height + 120                # Add padding top/bottom
        overlay = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
        overlay,
        (0, 0, 0, 100),           # semi-transparent black
        overlay.get_rect(),
        border_radius=20           # <-- roundness (pixels)
    )

        # Center the panel behind the menu block
        menu_center_y = start_y + (menu_height - spacing) // 2
        overlay_rect = overlay.get_rect(center=(center_x, menu_center_y))
        self.screen.blit(overlay, overlay_rect)

        self.option_rects = []

        for i, option in enumerate(self.options):
            # Highlight selected option
            color = (50, 150, 255) if i == self.selected_index else (255, 255, 255)
            text_surface = self.font.render(option, True, color)

            # Compute y position
            extra_spacing = 0
            if option == "Apply Changes":
                extra_spacing = 30

            y_pos = start_y + i * spacing + extra_spacing
            
            margin_x = int(config.SCREEN_WIDTH * 0.25)

            panel_right_x = int(config.SCREEN_WIDTH * 0.78)
            rect = text_surface.get_rect(midleft=(margin_x, y_pos))
            self.screen.blit(text_surface, rect)
            self.option_rects.append((option, rect))

            # Draw current resolution next to "Resolution"
            if option == "Resolution":
                res_text = f"{self.resolutions[self.current_resolution_index][0]}x{self.resolutions[self.current_resolution_index][1]}"
                res_surface = self.font.render(res_text, True, (200, 200, 0))
                res_rect = res_surface.get_rect(midright=(panel_right_x, rect.centery))
                self.screen.blit(res_surface, res_rect)

            # Draw current screen mode next to "screen mode"
            if option == "Screen Mode":
                res_text = f"{self.screen_mode[self.current_screen_mode_index]}"
                res_surface = self.font.render(res_text, True, (200, 200, 0))
                res_rect = res_surface.get_rect(midright=(panel_right_x, rect.centery))
                self.screen.blit(res_surface, res_rect)

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
                elif line.startswith("SCREEN_MODE"):
                    config.SCREEN_MODE = self.screen_mode[self.current_screen_mode_index]
                    lines[i] = f'SCREEN_MODE = "{config.SCREEN_MODE}"\n'

            # Write back
            with open(config_path, "w") as f:
                f.writelines(lines)

            print(f"Configuration saved: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}")
        except Exception as e:
            print("Error saving config:", e)

    def apply_changes(self):
        mode_text = self.screen_mode[self.current_screen_mode_index]
        flags = pygame.FULLSCREEN if mode_text == "Full Screen" else 0

        new_width, new_height = self.resolutions[self.current_resolution_index]
        config.SCREEN_WIDTH = new_width
        config.SCREEN_HEIGHT = new_height
        config.SCREEN_MODE = mode_text

        # Center the window on the desktop
        os.environ['SDL_VIDEO_CENTERED'] = '1'

         # Apply changes
        self.screen = pygame.display.set_mode((new_width, new_height), flags)

        # Rescale background
        self.bg_img = pygame.transform.scale(self.bg_img_orig, (new_width, new_height))

        # Update font size
        font_path = "client/data/assets/fonts/cinzel.decorative-black.ttf"
        self.font = pygame.font.Font(font_path, max(20, int(config.SCREEN_HEIGHT * 0.04)))

        print(f"Applied new resolution: {new_width} x {new_height}")
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
            if mouse_pos != self.last_mouse_pos:
                for i, (_, rect) in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        break
                self.last_mouse_pos = mouse_pos

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
                        if self.options[self.selected_index] == "Screen Mode":
                            self.current_screen_mode_index = (self.current_screen_mode_index - 1) % len(self.screen_mode)
                    elif event.key == pygame.K_RIGHT:
                        if self.options[self.selected_index] == "Resolution":
                            self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
                        if self.options[self.selected_index] == "Screen Mode":
                            self.current_screen_mode_index = (self.current_screen_mode_index + 1) % len(self.screen_mode)
                    elif event.key == pygame.K_RETURN:
                        selected_option = self.options[self.selected_index]
                        if selected_option == "Apply Changes":
                            self.apply_changes()
                        elif selected_option == "Return to Title":
                            running = False
                        elif selected_option == "Quit":
                            pygame.quit()
                            raise SystemExit
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
                            if option == "Screen Mode":
                                if event.button == 1:  # Left click
                                    self.current_screen_mode_index = (self.current_screen_mode_index + 1) % len(self.screen_mode)
                            elif option == "Apply Changes":
                                self.apply_changes()
                            elif option == "Return to Title":
                                running = False
                            elif option == "Quit":
                                return "exit"

            clock.tick(config.FPS)

        return "return"