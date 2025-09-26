# src/game.py
import pygame
from .maps import sydney

class GameLoop:
    def __init__(self, player):
        self.player = player
        self.clock = pygame.time.Clock()

    def loop(self, screen):
        running = True
        while running:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update player position / animation
            self.player.handle_input(keys)

            # Draw the scrolling map + player
            sydney.draw_map(screen, self.player)

            # Refresh display
            pygame.display.flip()
            self.clock.tick(60)

        return "quit"
