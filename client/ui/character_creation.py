import pygame
import re
import time
from .character_preview import CharacterPreview
from client.data import config

class CharacterCreation:
    NAME_REGEX = re.compile(r'^[A-Za-z0-9]{1,12}$')  # letters & numbers only, max 12

    def __init__(self, screen, client):
        self.screen = screen
        self.client = client
        self.font = pygame.font.SysFont(None, 32)
        self.name_text = ""
        self.cursor_visible = True
        self.last_blink = time.time()
        self.created_character = None

    def draw(self):
        self.screen.fill((0,0,0))
        # Title
        title_surf = self.font.render("Enter Character Name:", True, (255,255,255))
        self.screen.blit(title_surf, (50, 100))

        # Input box
        pygame.draw.rect(self.screen, (255,255,255), (50, 150, 400, 40), 2)
        text_surf = self.font.render(self.name_text, True, (255,255,255))
        self.screen.blit(text_surf, (55, 155))

        # Cursor blink
        if self.cursor_visible:
            cursor_x = 55 + text_surf.get_width() + 2
            pygame.draw.line(self.screen, (255,255,255), (cursor_x, 155), (cursor_x, 155 + 30), 2)

        pygame.display.flip()

    def validate_name(self, name):
        return self.NAME_REGEX.match(name) is not None

    def run(self):
        clock = pygame.time.Clock()
        running = True

        # Register callback for server messages
        original_callback = self.client.on_message
        def temp_callback(message):
            if message.get("action") == "character_created":
                self.created_character = message["character"]
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
                    if event.key == pygame.K_RETURN:
                        if self.validate_name(self.name_text):
                            # Send create_character request to server
                            self.client.send_json({
                                "action": "create_character",
                                "data": {"name": self.name_text}
                            })
                        else:
                            print("Invalid name! Only letters and numbers, max 12 characters.")
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_text = self.name_text[:-1]
                    else:
                        char = event.unicode
                        if char.isalnum() and len(self.name_text) < 12:
                            self.name_text += char

            # If character created, return it
            if self.created_character:
                self.client.on_message = original_callback  # restore original callback
                return self.created_character

            clock.tick(config.FPS)

        self.client.on_message = original_callback
        return None
