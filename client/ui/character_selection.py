import pygame
from client import config

class CharacterSelection:
    def __init__(self, screen, characters):
        self.screen = screen
        self.characters = characters  # list of dicts (max 6)
        self.selected_slot = None  # index of chosen slot

        # Load images
        self.bg_img = pygame.image.load("client/data/assets/images/character_selection.png").convert_alpha()
        self.mask_img = pygame.image.load("client/data/assets/images/character_selection_mask.png").convert()

        # Scale images to screen size
        self.bg_img = pygame.transform.scale(self.bg_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.mask_img = pygame.transform.scale(self.mask_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Font proportional to screen height
        self.font = pygame.font.SysFont(config.FONT_NAME, max(20, int(config.SCREEN_HEIGHT * 0.04)))

        # Map overlay colors -> field names
        self.color_map = {
            (0, 128, 0): "start_btn",
            (176, 224, 230): "slot",
            (255, 0, 0): "return_btn",
        }

        # Build masks for clickable/highlightable regions
        self.masks = self._build_masks()

        # Focus order
        self.focus_order = [f"slot{i}" for i in range(len(self.masks['slots']))] + ["start_btn", "return_btn"]
        self.active_field = self.focus_order[0]

    def _build_masks(self):
        """Scan mask image and create pygame.Mask for each field."""
        masks = {}
        slot_masks = []
        width, height = self.mask_img.get_size()

        # Initialize masks for buttons
        for color, name in self.color_map.items():
            if name != "slot":
                masks[name] = pygame.Mask((width, height))

        visited = pygame.Mask((width, height))

        for x in range(width):
            for y in range(height):
                color = self.mask_img.get_at((x, y))[:3]
                if color not in self.color_map:
                    continue
                field_name = self.color_map[color]

                if field_name == "slot" and not visited.get_at((x, y)):
                    # Flood-fill a new slot mask
                    slot_mask = pygame.Mask((width, height))
                    to_check = [(x, y)]
                    while to_check:
                        cx, cy = to_check.pop()
                        if 0 <= cx < width and 0 <= cy < height:
                            if not visited.get_at((cx, cy)) and self.mask_img.get_at((cx, cy))[:3] == color:
                                visited.set_at((cx, cy), 1)
                                slot_mask.set_at((cx, cy), 1)
                                to_check.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
                    slot_masks.append(slot_mask)

                elif field_name != "slot":
                    masks[field_name].set_at((x, y), 1)

        # Sort slots roughly top→bottom
        slot_masks.sort(key=lambda m: m.get_bounding_rects()[0].y if m.get_bounding_rects() else 9999)
        masks["slots"] = slot_masks[:6]
        return masks

    def draw_highlight(self, field):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        if field.startswith("slot"):
            index = int(field.replace("slot", ""))
            if index < len(self.masks["slots"]):
                self.masks["slots"][index].to_surface(overlay, setcolor=(255, 215, 0, 100), unsetcolor=(0, 0, 0, 0))
        else:
            mask = self.masks.get(field)
            if mask:
                mask.to_surface(overlay, setcolor=(255, 215, 0, 100), unsetcolor=(0, 0, 0, 0))
        self.screen.blit(overlay, (0, 0))

    def draw_selected_slot(self):
        if self.selected_slot is not None and self.selected_slot < len(self.masks["slots"]):
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            self.masks["slots"][self.selected_slot].to_surface(
                overlay, setcolor=(0, 200, 255, 120), unsetcolor=(0, 0, 0, 0)
            )
            self.screen.blit(overlay, (0, 0))

    def draw(self):
        self.screen.blit(self.bg_img, (0, 0))
        self.draw_selected_slot()
        self.draw_highlight(self.active_field)

        # Draw characters inside slots
        for i, mask in enumerate(self.masks["slots"]):
            if not mask:
                continue
            rects = mask.get_bounding_rects()
            if not rects:
                continue
            rect = rects[0]
            if i < len(self.characters):
                char = self.characters[i]
                text = f"{char['name']} (Lv {char['stats'].get('Level', 0)})"
            else:
                text = "Empty Slot"
            surf = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))

        pygame.display.flip()

    def _get_field_at_pos(self, pos):
        x, y = pos
        for i, mask in enumerate(self.masks["slots"]):
            if mask.get_at((x, y)):
                return f"slot{i}"
        for name in ("start_btn", "return_btn"):
            mask = self.masks.get(name)
            if mask.get_at((x, y)):
                return name
        return None

    def _activate_field(self, field):
        if field.startswith("slot"):
            index = int(field.replace("slot", ""))
            self.selected_slot = index
            return None
        elif field == "start_btn":
            if self.selected_slot is not None and self.selected_slot < len(self.characters):
                return self.characters[self.selected_slot]
            print("No character selected!")
            return None
        elif field == "return_btn":
            return "menu"

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_DOWN, pygame.K_TAB):
                        idx = self.focus_order.index(self.active_field)
                        self.active_field = self.focus_order[(idx + 1) % len(self.focus_order)]
                    elif event.key == pygame.K_UP:
                        idx = self.focus_order.index(self.active_field)
                        self.active_field = self.focus_order[(idx - 1) % len(self.focus_order)]
                    elif event.key == pygame.K_RETURN:
                        if self.active_field.startswith("slot"):
                            self.selected_slot = int(self.active_field.replace("slot", ""))
                        elif self.active_field == "start_btn":
                            if self.selected_slot is not None:
                                return self.characters[self.selected_slot]
                        elif self.active_field == "return_btn":
                            return "menu"

                elif event.type == pygame.MOUSEMOTION:
                    field = self._get_field_at_pos(event.pos)
                    if field:
                        self.active_field = field

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    field = self._get_field_at_pos(event.pos)
                    if field:
                        result = self._activate_field(field)
                        if result is not None:
                            return result

            clock.tick(60)
