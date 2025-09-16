import pygame

class CharacterSelection:
    def __init__(self, screen, characters):
        self.screen = screen
        self.characters = characters  # list of dicts
        self.selected_index = 0
        self.font = pygame.font.SysFont(None, 32)

    def draw(self):
        self.screen.fill((0,0,0))
        y = 100
        for i, char in enumerate(self.characters):
            text = f"{char['name']} (Level {char['stats'].get('Level',0)})"
            color = (255, 255, 0) if i == self.selected_index else (255,255,255)
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, (100, y))
            y += 40
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.characters)
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.characters)
                    elif event.key == pygame.K_RETURN:
                        return self.characters[self.selected_index]  # return selected character
            clock.tick(60)
        return None
