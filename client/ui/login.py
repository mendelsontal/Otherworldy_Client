import pygame

class Login:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Segoe UI", 30)
        self.username = ""
        self.password = ""
        self.active_field = "username"

    def draw(self):
        self.screen.fill((20, 20, 20))
        # Draw labels
        username_label = self.font.render(f"Username: {self.username}", True, (255,255,255))
        password_label = self.font.render(f"Password: {'*' * len(self.password)}", True, (255,255,255))
        self.screen.blit(username_label, (200, 250))
        self.screen.blit(password_label, (200, 300))
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
                    if event.key == pygame.K_TAB:
                        self.active_field = "password" if self.active_field == "username" else "username"
                    elif event.key == pygame.K_RETURN:
                        print(f"Login attempt: {self.username} / {self.password}")
                        running = False  # replace with actual server call later
                    elif event.key == pygame.K_BACKSPACE:
                        if self.active_field == "username":
                            self.username = self.username[:-1]
                        else:
                            self.password = self.password[:-1]
                    else:
                        char = event.unicode
                        if self.active_field == "username":
                            self.username += char
                        else:
                            self.password += char
            clock.tick(60)
