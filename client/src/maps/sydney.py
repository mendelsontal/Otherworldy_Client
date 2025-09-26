# src/maps/sydney.py
import pygame
import os

# Path to the big map image (project-root/assets/...)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
MAP_PATH = os.path.join("assets", "images", "Maps", "Sydney_a.png")
COLLISION_PATH = os.path.join("assets", "images", "Maps", "Sydney_collision.png")

# Map variables
_map_image = None
_collision_image = None
MAP_WIDTH = 2880
MAP_HEIGHT = 2560

def _ensure_loaded():
    global _map_image, _collision_image, MAP_WIDTH, MAP_HEIGHT
    if _map_image is not None:
        return

    if not os.path.exists(MAP_PATH):
        raise FileNotFoundError(f"Map image not found: {MAP_PATH}")
    
    if not os.path.exists(COLLISION_PATH):
        raise FileNotFoundError(f"Collision map not found: {COLLISION_PATH}")
    _collision_image = pygame.image.load(COLLISION_PATH).convert()  # convert for pixel access

    img = pygame.image.load(MAP_PATH)
    if pygame.display.get_surface() is not None:
        try:
            img = img.convert()
        except Exception:
            pass

    _map_image = img
    MAP_WIDTH, MAP_HEIGHT = _map_image.get_size()


def draw_map(screen, player):
    _ensure_loaded()
    screen_width, screen_height = screen.get_size()
    camera_x = int(player.x - screen_width // 2)
    camera_y = int(player.y - screen_height // 2)
    camera_x = max(0, min(camera_x, MAP_WIDTH - screen_width))
    camera_y = max(0, min(camera_y, MAP_HEIGHT - screen_height))
    view_rect = pygame.Rect(camera_x, camera_y, screen_width, screen_height)
    screen.blit(_map_image, (0, 0), view_rect)

    # Draw player with offsets
    try:
        player.draw(screen, offset_x=-camera_x, offset_y=-camera_y)
        return
    except Exception:
        pass
    if hasattr(player, "image"):
        draw_x = player.x - camera_x
        draw_y = player.y - camera_y
        screen.blit(player.image, (draw_x, draw_y))


def get_tile_type(x, y):
    """
    Returns the type of tile at world coordinates (x, y):
    - "walkable" = white (255,255,255)
    - "shadow" = gray (128,128,128)
    - "blocked" = any other color
    """
    _ensure_loaded()
    x = max(0, min(int(x), MAP_WIDTH - 1))
    y = max(0, min(int(y), MAP_HEIGHT - 1))
    color = _collision_image.get_at((x, y))[:3]

    if color == (255, 255, 255):
        return "walkable"
    elif color == (128, 128, 128):
        return "shadow"
    else:
        return "blocked"


def is_walkable(x, y):
    """
    Returns True if white or gray (walkable), False if black (blocked).
    """
    tile = get_tile_type(x, y)
    return tile in ("walkable", "shadow")
