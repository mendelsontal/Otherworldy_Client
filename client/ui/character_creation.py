# client/ui/character_creation.py
import pygame
import re
import time
import os
from .character_preview import CharacterPreview
from client.data import config

class CharacterCreation:
    @staticmethod
    def _get_hair_folders():
        hair_root = os.path.join("client", "assets", "images", "Characters", "Hair")
        if not os.path.exists(hair_root):
            return []
        return sorted([d for d in os.listdir(hair_root) if os.path.isdir(os.path.join(hair_root, d))])

    def __init__(self, screen, client):
        self.screen = screen
        self.client = client
        self.font = pygame.font.SysFont(None, 32)

        # state
        self.state = "name"
        self.name_text = ""
        self.cursor_visible = True
        self.last_blink = time.time()

        self.gender_options = ["Male", "Female"]
        self.gender_index = 0

        self.hair_folders = self._get_hair_folders()
        self.hair_index = 0

        self.preview = CharacterPreview(self.font, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

        self.error_msg = ""
        self.created_character = None

    def draw(self):
        self.screen.fill((0,0,0))

        if self.state == "name":
            title_surf = self.font.render("Enter Character Name:", True, (255,255,255))
            self.screen.blit(title_surf, (50, 100))

            # Input box
            pygame.draw.rect(self.screen, (255,255,255), (50, 150, 400, 40), 2)
            text_surf = self.font.render(self.name_text, True, (255,255,255))
            self.screen.blit(text_surf, (55, 155))

            # Cursor blink
            if self.cursor_visible:
                cursor_x = 55 + text_surf.get_width() + 2
                pygame.draw.line(self.screen, (255,255,255), (cursor_x, 155), (cursor_x, 185), 2)

            # Show error if any
            if self.error_msg:
                err_surf = self.font.render(self.error_msg, True, (255, 80, 80))
                self.screen.blit(err_surf, (50, 200))

        elif self.state == "gender":
                    title_surf = self.font.render("Select Gender:", True, (255,255,255))
                    self.screen.blit(title_surf, (50, 100))

                    for i, g in enumerate(self.gender_options):
                        color = (255,255,0) if i == self.gender_index else (200,200,200)
                        gsurf = self.font.render(g, True, color)
                        self.screen.blit(gsurf, (config.SCREEN_WIDTH//2 - gsurf.get_width()//2, 200 + i*60))

        elif self.state == "hair":
            title_surf = self.font.render("Select Hair Style:", True, (255,255,255))
            self.screen.blit(title_surf, (50, 40))

            current_hair = self.hair_folders[self.hair_index] if self.hair_folders else None
            appearance = {
                "gender": self.gender_options[self.gender_index],
                "hair": current_hair
            }
            self.preview.draw_preview(self.screen, appearance=appearance)

            if current_hair:
                hair_text = self.font.render(current_hair, True, (200,200,200))
                self.screen.blit(hair_text, (50, config.SCREEN_HEIGHT - 80))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        # Hook into server response
        original_callback = self.client.on_message
        def temp_callback(message):
            if message.get("action") == "character_created":
                self.created_character = message["character"]

            elif message.get("action") == "name_valid":
                if message.get("ok"):
                    self.error_msg = ""
                    self.state = "gender"
                else:
                    self.error_msg = message.get("reason", "Invalid name")

            else:
                if original_callback:
                    original_callback(message)

        self.client.on_message = temp_callback

        while running:
            self.draw()

            # Cursor blink
            if time.time() - self.last_blink > 0.5:
                self.cursor_visible = not self.cursor_visible
                self.last_blink = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    # universal cancel
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "name":
                            running = False
                        elif self.state == "gender":
                            self.state = "name"
                        elif self.state == "hair":
                            self.state = "gender"
                        continue

                    # --- name state ---
                    if self.state == "name":
                        if event.key == pygame.K_RETURN:
                            self.client.send_json({
                                "action": "check_name",
                                "data": {"name": self.name_text}
                            })
                        elif event.key == pygame.K_BACKSPACE:
                            self.name_text = self.name_text[:-1]
                        else:
                            char = event.unicode
                            if char.isalnum() and len(self.name_text) < 12:
                                self.name_text += char

                    # --- gender state ---
                    elif self.state == "gender":
                        if event.key == pygame.K_UP:
                            self.gender_index = (self.gender_index - 1) % len(self.gender_options)
                        elif event.key == pygame.K_DOWN:
                            self.gender_index = (self.gender_index + 1) % len(self.gender_options)
                        elif event.key == pygame.K_RETURN:
                            self.state = "hair"

                    # --- hair state ---
                    elif self.state == "hair":
                        if self.hair_folders:
                            if event.key == pygame.K_LEFT:
                                self.hair_index = (self.hair_index - 1) % len(self.hair_folders)
                            elif event.key == pygame.K_RIGHT:
                                self.hair_index = (self.hair_index + 1) % len(self.hair_folders)
                            elif event.key == pygame.K_RETURN:
                                data = {
                                    "name": self.name_text,
                                    "gender": self.gender_options[self.gender_index],
                                    "hair": self.hair_folders[self.hair_index] if self.hair_folders else None
                                }
                                print("Creating character:", data)
                                self.client.send_json({
                                    "action": "create_character",
                                    "data": data
                                })

                        else:
                            if event.key == pygame.K_RETURN:
                                self.client.send_json({
                                    "action": "create_character",
                                    "data": {
                                        "name": self.name_text,
                                        "gender": self.gender_options[self.gender_index],
                                        "hair": None
                                    }
                                })

            # If character created, return it
            if self.created_character:
                self.client.on_message = original_callback  # restore
                return self.created_character

            clock.tick(config.FPS)

        self.client.on_message = original_callback
        return None
