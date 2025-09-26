import pygame
from client.data import config

class GameMenu:
    def __init__(self, font, screen_width=config["screen_width"], screen_height=config["screen_height"]):
        self.font = font
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.options = ["Options", "Main Menu", "Return"]
        self.selected = 0

    def loop(self, screen, player):
        clock = pygame.time.Clock()
        running = True
        while running:
            screen.fill((0, 0, 0))
            # Draw options
            for i, option in enumerate(self.options):
                color = (255, 255, 0) if i == self.selected else (255, 255, 255)
                text = self.font.render(option, True, color)
                screen.blit(text, (self.screen_width // 2 - text.get_width() // 2,
                                   200 + i*50))
            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit", player
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        choice = self.options[self.selected]
                        if choice == "Options":
                            print("No intro images found!")
                            return
                        elif choice == "Main Menu":
                            return "menu", player
                    elif event.key == pygame.K_ESCAPE:
                        return "resume", player

            clock.tick(config.FPS)
