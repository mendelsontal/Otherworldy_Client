# client/ui/login.py
import pygame
from client import config
import time
import threading
import os
from network.client import GameClient
from client.ui.character_selection import CharacterSelection
from client.ui.character_creation import CharacterCreation

class Login:
    def __init__(self, screen):
        self.screen = screen
        # Load server ip & port
        self.server_ip = config.SERVER_IP
        self.server_port = config.SERVER_PORT

        # Load window & mask
        self.base_img = pygame.image.load("client/data/assets/images/login_window.png").convert_alpha()
        self.mask_img = pygame.image.load("client/data/assets/images/login_window_mask.png").convert()

        # Load background and scale to screen size
        self.bg_img = pygame.image.load("client/data/assets/images/menu_bg.png").convert_alpha()
        self.bg_img = pygame.transform.scale(self.bg_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

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
        self.logged_in = False
        self.characters = []
        self.username_text = self._load_username_from_file()
        self.password_text = ""
        self.font = pygame.font.SysFont(config.FONT_NAME, 24)

        # Cursor blink
        self.cursor_visible = True
        self.last_blink = time.time()

        # Networking client and synchronization primitives
        self.client = GameClient(self.server_ip, int(self.server_port))
        self.server_event = threading.Event()
        self.server_action = None
        self.server_payload = None

        # assign callback
        self.client.on_message = self._on_server_message
        self.client.connect()

    # ---------------- Persistence Methods ----------------
    def _save_username_to_file(self, username):
        try:
            os.makedirs("client/data", exist_ok=True)
            with open("client/data/saved_username.txt", "w", encoding="utf-8") as f:
                f.write(username)
        except Exception as e:
            print("Failed to save username:", e)

    def _load_username_from_file(self):
        try:
            with open("client/data/saved_username.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    # ---------------- Network & UI Methods ----------------
    def _on_server_message(self, message: dict):
        """This runs on the client's network thread. Keep it minimal: set an event + payload."""
        self.server_action = message.get("action")
        self.server_payload = message
        self.server_event.set()

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
        self.screen.blit(self.bg_img, (0, 0))
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
            self.client.login(self.username_text.strip(), self.password_text.strip())

    def rescale_ui(self):
        # Rescale background
        self.bg_img = pygame.image.load("client/data/assets/images/menu_bg.png").convert_alpha()
        self.bg_img = pygame.transform.scale(self.bg_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Recalculate scaling for window and mask
        scale_ratio = config.SCREEN_HEIGHT * 0.7 / self.base_h
        self.scaled_w = int(self.base_w * scale_ratio)
        self.scaled_h = int(self.base_h * scale_ratio)
        self.window_img = pygame.transform.scale(self.base_img, (self.scaled_w, self.scaled_h))
        self.mask_img = pygame.transform.scale(self.mask_img, (self.scaled_w, self.scaled_h))
        self.window_rect = self.window_img.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))

        # Recalculate field rects
        self.fields_rects.clear()
        for color, name in self.color_map.items():
            rect = self._find_color_bounds(color)
            if rect:
                self.fields_rects[name] = rect.move(self.window_rect.topleft)

        # Update font
        self.font = pygame.font.SysFont(config.FONT_NAME, 24)


    # ---------------- Main Loop ----------------
    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.draw()

            # Handle server responses
            if self.server_event.is_set():
                action = self.server_action
                payload = self.server_payload or {}
                self.server_event.clear()
                self.server_action = None
                self.server_payload = None

                if action == "login_failed":
                    reason = payload.get("reason", "Unknown")
                    print("Login failed:", reason)
                elif action == "character_list":
                    self.characters = payload.get("characters", [])  # <--- assign here
                    self.logged_in = True

                    # Save username to disk for future sessions
                    self._save_username_to_file(self.username_text.strip())

                    # If no characters, open creation screen
                    if not self.characters:
                        created = CharacterCreation(self.screen, self.client).run()
                        if created:
                            self.characters = [created]
                        else:
                            continue

                    # Open character selection
                    selected = CharacterSelection(self.screen, self.characters, self.client).run()
                    if selected == "menu":
                        return "menu"
                    elif selected:
                        return {"selected_character": selected}
                    else:
                        continue

            # Handle input events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_TAB:
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

            clock.tick(config.FPS)

        return None
