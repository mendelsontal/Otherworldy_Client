# src/intro.py
import pygame
import os
from client.data import config

def play_intro(screen, image_folder="assets/images/intro", delay=3000):
    """Plays a slideshow intro once after new character creation.
    
    screen: pygame display surface
    image_folder: folder with intro images
    delay: time per image in ms
    """
    clock = pygame.time.Clock()
    images = []

    # Load all images
    for file in sorted(os.listdir(image_folder)):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            img = pygame.image.load(os.path.join(image_folder, file)).convert()
            img = pygame.transform.scale(img, screen.get_size())  # fit screen
            images.append(img)

    if not images:
        print("No intro images found!")
        return

    for img in images:
        screen.blit(img, (0, 0))
        pygame.display.flip()
        pygame.time.delay(delay)  # hold on this image
        # let player skip with ESC
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        clock.tick(config.FPS)
