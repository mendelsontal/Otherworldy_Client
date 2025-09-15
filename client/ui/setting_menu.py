# client/ui/settings_menu.py
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
        self.options = ["Resolution", "Sound", "Apply", "Return"]
        self.selected_index = 0

        # Resolution choices
        self.resolutions = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
        self.current_resolution_index = next(
            (i for i, r in enumerate(self.resolutions) if r == (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)), 0
        )

        self.dropdown_open = False
        self.dropdown_selected = self.current_resolution_index
    
    def center_window(width, height):
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
            text_surface = self.font.render(option, True, (255, 255, 255))
            rect = text_surface.get_rect(center=(center_x, center_y + i * spacing))

            # Highlight selected option (if dropdown closed)
            if i == self.selected_index and not self.dropdown_open:
                s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                s.fill((255, 215, 0, 30))  # semi-transparent highlight
                self.screen.blit(s, rect.topleft)

            self.screen.blit(text_surface, rect)
            self.option_rects.append(rect)

            # Draw current resolution next to "Resolution"
            if option == "Resolution":
                res_text = f"{self.resolutions[self.current_resolution_index][0]}x{self.resolutions[self.current_resolution_index][1]}"
                res_surface = self.font.render(res_text, True, (200, 200, 0))
                self.screen.blit(res_surface, (rect.right + 20, rect.y))

        # Draw dropdown if open
        self.dropdown_rects = []
        if self.dropdown_open:
            dropdown_start_y = center_y + spacing  # just below Resolution option
            dropdown_spacing = max(30, int(config.SCREEN_HEIGHT * 0.04))

            for i, res in enumerate(self.resolutions):
                res_surface = self.font.render(f"{res[0]}x{res[1]}", True, (255, 255, 255))
                rect = res_surface.get_rect(center=(center_x, dropdown_start_y + i * dropdown_spacing))

                # Highlight selected dropdown item
                if i == self.dropdown_selected:
                    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                    s.fill((255, 215, 0, 50))
                    self.screen.blit(s, rect.topleft)

                self.screen.blit(res_surface, rect)
                self.dropdown_rects.append(rect)

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
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_UP:
                        if self.dropdown_open:
                            self.dropdown_selected = (self.dropdown_selected - 1) % len(self.resolutions)
                        else:
                            self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        if self.dropdown_open:
                            self.dropdown_selected = (self.dropdown_selected + 1) % len(self.resolutions)
                        else:
                            self.selected_index = (self.selected_index + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.dropdown_open:
                            self.current_resolution_index = self.dropdown_selected
                            self.dropdown_open = False
                        else:
                            selected_option = self.options[self.selected_index]
                            if selected_option == "Resolution":
                                self.dropdown_open = True
                                self.dropdown_selected = self.current_resolution_index
                            elif selected_option == "Return":
                                running = False
                            elif selected_option == "Apply":
                                self.apply_resolution()

                elif event.type == pygame.MOUSEMOTION:
                    if not self.dropdown_open:
                        for i, rect in enumerate(self.option_rects):
                            if rect.collidepoint(mx, my):
                                self.selected_index = i
                    else:
                        for i, rect in enumerate(self.dropdown_rects):
                            if rect.collidepoint(mx, my):
                                self.dropdown_selected = i

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.dropdown_open:
                        for i, rect in enumerate(self.option_rects):
                            if rect.collidepoint(mx, my):
                                self.selected_index = i
                                selected_option = self.options[i]
                                if selected_option == "Resolution":
                                    self.dropdown_open = True
                                    self.dropdown_selected = self.current_resolution_index
                                elif selected_option == "Return":
                                    running = False
                                elif selected_option == "Apply":
                                    self.apply_resolution()
                    else:
                        for i, rect in enumerate(self.dropdown_rects):
                            if rect.collidepoint(mx, my):
                                self.current_resolution_index = i
                                self.dropdown_open = False

