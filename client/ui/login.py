import pygame
from client import config
import time

class Login:
    def __init__(self, screen):
        self.screen = screen

        # Load window & mask
        self.base_img = pygame.image.load("client/data/assets/images/login_window.png").convert_alpha()
        self.mask_img = pygame.image.load("client/data/assets/images/login_window_mask.png").convert()

        self.base_w, self.base_h = self.base_img.get_size()
        scale_ratio = config.SCREEN_HEIGHT * 0.7 / self.base_h
        self.scaled_w = int(self.base_w * scale_ratio)
        self.scaled_h = int(self.base_h * scale_ratio)
        self.window_img = pygame.transform.scale(self.base_img, (self.scaled_w, self.scaled_h))
        self.mask_img = pygame.transform.scale(self.mask_img, (self.scaled_w, self.scaled_h))
        self.window_rect = self.window_img.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))

        # Map colors to fields/buttons
        self.color_map = {
            (0, 0, 255): "username",
            (0, 255, 255): "password",
            (0, 255, 0): "signup_btn",
            (255, 0, 0): "login_btn",
        }

        # Extract bounding boxes for all fields/buttons in screen space
        self.fields_rects = {}
        for color, name in self.color_map.items():
            rect = self._find_color_bounds(color)
            if rect:
                self.fields_rects[name] = rect.move(self.window_rect.topleft)

        # Focus order
        self.focus_order = ["username", "password", "login_btn", "signup_btn"]
        self.focus_index = 0
        self.active_field = self.focus_order[self.focus_index]

        # State
        self.username_text = ""
        self.password_text = ""
        self.font = pygame.font.SysFont(config.FONT_NAME, 24)

        # Cursor blink
        self.cursor_visible = True
        self.last_blink = time.time()

    def _find_color_bounds(self, color):
        pixels = pygame.PixelArray(self.mask_img)
        coords = [(x, y) for x in range(self.mask_img.get_width())
                          for y in range(self.mask_img.get_height())
                          if self.mask_img.get_at((x, y))[:3] == color]
        pixels.close()
        if not coords:
            return None
        xs, ys = zip(*coords)
        return pygame.Rect(min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys))

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.screen.blit(self.window_img, self.window_rect)

        # Draw highlight overlay for active field
        if self.active_field in self.fields_rects:
            rect = self.fields_rects[self.active_field]
            s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            s.fill((255, 215, 0, 50))  # semi-transparent highlight
            self.screen.blit(s, (rect.x, rect.y))

        # Cursor blink toggle
        if time.time() - self.last_blink > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_blink = time.time()

        # Draw username/password text + cursor
        for field in ["username", "password"]:
            if field in self.fields_rects:
                rect = self.fields_rects[field]
                text = self.username_text if field == "username" else "*" * len(self.password_text)
                text_surface = self.font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, (rect.x + 5, rect.y + (rect.h - text_surface.get_height()) // 2))

                # Draw cursor if active
                if self.active_field == field and self.cursor_visible:
                    cursor_h = int(text_surface.get_height() * 0.6)
                    cursor_x = rect.x + 5 + text_surface.get_width() + 2
                    cursor_y = rect.y + (rect.h - cursor_h) // 2
                    pygame.draw.line(self.screen, (255, 255, 255), (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 1)

        pygame.display.flip()

    def attempt_login(self):
        if not self.username_text.strip():
            print("Username cannot be empty")
        elif len(self.username_text.strip()) < 6:
            print("Username must be at least 6 characters")
        elif not self.password_text.strip():
            print("Password cannot be empty")
        elif len(self.password_text.strip()) < 6:
            print("Password must be at least 6 characters")
        else:
            print("Login clicked:", self.username_text, self.password_text)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_TAB:
                        # Only switch between username/password
                        if self.active_field in ["username", "password"]:
                            self.focus_index = (self.focus_index + 1) % 2
                            self.active_field = self.focus_order[self.focus_index]

                    elif event.key == pygame.K_DOWN:
                        self.focus_index = (self.focus_index + 1) % len(self.focus_order)
                        self.active_field = self.focus_order[self.focus_index]

                    elif event.key == pygame.K_UP:
                        self.focus_index = (self.focus_index - 1) % len(self.focus_order)
                        self.active_field = self.focus_order[self.focus_index]

                    elif event.key == pygame.K_BACKSPACE:
                        if self.active_field == "username":
                            self.username_text = self.username_text[:-1]
                        elif self.active_field == "password":
                            self.password_text = self.password_text[:-1]

                    elif event.key == pygame.K_RETURN:
                        if self.active_field in ["username", "password", "login_btn"]:
                            self.attempt_login()
                        elif self.active_field == "signup_btn":
                            print("Sign Up clicked")

                    else:
                        char = event.unicode
                        if char.isprintable():
                            if self.active_field == "username" and len(self.username_text) < 10:
                                self.username_text += char
                            elif self.active_field == "password" and len(self.password_text) < 22:
                                self.password_text += char

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if self.window_rect.collidepoint(mx, my):
                        local_x = mx - self.window_rect.x
                        local_y = my - self.window_rect.y
                        color = self.mask_img.get_at((local_x, local_y))[:3]
                        action = self.color_map.get(color)
                        if action:
                            self.active_field = action
                            self.focus_index = self.focus_order.index(action)
                            if action == "login_btn":
                                self.attempt_login()
                            elif action == "signup_btn":
                                print("Sign Up clicked")

            clock.tick(config.FPS)
