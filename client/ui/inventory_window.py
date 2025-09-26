# src/inventory_window.py
import pygame

class InventoryWindow:
    def __init__(self, font):
        self.original_bg = pygame.image.load("assets/images/UI/inventory.png").convert_alpha()
        self.background = self.original_bg
        self.font = font

        self.rows = 6
        self.cols = 10
        self.slots = []

        # Drag & drop
        self.dragging_item = None
        self.dragging_index = None
        self.drag_offset = (0, 0)

    def resize(self, screen):
        screen_rect = screen.get_rect()
        max_width = int(screen_rect.width * 0.8)
        max_height = int(screen_rect.height * 0.8)

        # Scale while keeping aspect ratio
        bg_rect = self.original_bg.get_rect()
        scale = min(max_width / bg_rect.width, max_height / bg_rect.height, 0.8)
        new_size = (int(bg_rect.width * scale), int(bg_rect.height * scale))
        self.background = pygame.transform.smoothscale(self.original_bg, new_size)

        # Slot rects
        slot_w, slot_h = 143, 140
        start_x, start_y = 56, 81
        spacing_x = 5
        spacing_y = 10

        scale_x = new_size[0] / self.original_bg.get_width()
        scale_y = new_size[1] / self.original_bg.get_height()

        self.slots = []
        for r in range(self.rows):
            for c in range(self.cols):
                x = int((start_x + c * (slot_w + spacing_x)) * scale_x)
                y = int((start_y + r * (slot_h + spacing_y)) * scale_y)
                w = int(slot_w * scale_x)
                h = int(slot_h * scale_y)
                self.slots.append(pygame.Rect(x, y, w, h))

    def handle_event(self, event, player):
        if not hasattr(self, "bg_rect"):
            return
        bg_rect = self.bg_rect

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Pick up item if the slot has one
            for i, slot in enumerate(self.slots):
                world_rect = slot.move(bg_rect.topleft)
                if world_rect.collidepoint(event.pos) and i < len(player.inventory):
                    if player.inventory[i] is not None:
                        scale_factor = 0.8
                        self.dragging_item = pygame.transform.smoothscale(
                            player.inventory[i].image,
                            (int(world_rect.width * scale_factor), int(world_rect.height * scale_factor))
                        )
                        self.dragging_index = i
                        self.drag_offset = (world_rect.x - event.pos[0], world_rect.y - event.pos[1])
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging_item:
            dropped_in_slot = False
            for i, slot in enumerate(self.slots):
                world_rect = slot.move(bg_rect.topleft)
                if world_rect.collidepoint(event.pos) and i < len(player.inventory):
                    # Swap items
                    player.inventory[i], player.inventory[self.dragging_index] = (
                        player.inventory[self.dragging_index],
                        player.inventory[i],
                    )
                    dropped_in_slot = True
                    break

            if not dropped_in_slot and self.dragging_index is not None:
                # Dropped outside → discard
                player.inventory[self.dragging_index] = None

            self.dragging_item = None
            self.dragging_index = None


    def draw(self, screen, player):
        self.resize(screen)
        screen_rect = screen.get_rect()

        # Center the window
        bg_rect = self.background.get_rect(center=screen_rect.center)
        self.bg_rect = bg_rect

        # Draw the background
        screen.blit(self.background, bg_rect)

        # Draw stats
        small_font = pygame.font.Font(None, 35)
        medium_font = pygame.font.Font(None, 28)
        x = bg_rect.x + 585
        y = bg_rect.y + 220
        line_height = 30
        for key in ("Title","Gold"):
            if key in player.stats:
                value = player.stats[key]
                text = f"{key}: {value}"
                font_to_use = medium_font if key == "Gold" else small_font
                color = (212,175,55) if key in ("Title","Gold") else (255,255,255)
                shadow = font_to_use.render(text, True, (0,0,0))
                screen.blit(shadow, (x+2, y+2))
                surf = font_to_use.render(text, True, color)
                screen.blit(surf, (x, y))
                y += line_height

        # Draw items
        self.draw_items(screen, bg_rect, player)

        # **Draw hover info last so it appears on top**
        self.draw_hover_info(screen, player)

    def draw_items(self, screen, bg_rect, player):
        for idx, rect in enumerate(self.slots):
            world_rect = rect.move(bg_rect.topleft)
            if idx < len(player.inventory):
                # Skip drawing the item that is currently being dragged
                if self.dragging_index is not None and idx == self.dragging_index:
                    continue

                item = player.inventory[idx]
                if item is None:
                    continue
                if item.image:
                    scale_factor = 0.8
                    icon_w = int(rect.width * scale_factor)
                    icon_h = int(rect.height * scale_factor)
                    icon = pygame.transform.smoothscale(item.image, (icon_w, icon_h))
                    screen.blit(icon, icon.get_rect(center=world_rect.center))


        # Draw dragged item on top of mouse
        if self.dragging_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(self.dragging_item, (mouse_x + self.drag_offset[0], mouse_y + self.drag_offset[1]))

    def draw_hover_info(self, screen, player):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for idx, rect in enumerate(self.slots):
            world_rect = rect.move(self.bg_rect.topleft)
            if world_rect.collidepoint((mouse_x, mouse_y)):
                if idx >= len(player.inventory):
                    return
                item = player.inventory[idx]
                if item is None:
                    return

                # --- Tooltip settings ---
                padding = 8
                spacing = 5
                font = pygame.font.Font(None, 24)
                lines = [item.name, getattr(item, "description", ""), f"Stat: {getattr(item, 'stat', '')}", f"Grade: {getattr(item, 'grade', '')}"]
                lines = [line for line in lines if line]  # remove empty lines

                # Calculate size
                text_widths = [font.size(line)[0] for line in lines]
                text_height = font.size(lines[0])[1] if lines else 0
                icon_size = 32 if getattr(item, "image", None) else 0
                width = max(text_widths) + icon_size + padding*3
                height = text_height * len(lines) + padding*2

                tooltip_rect = pygame.Rect(mouse_x + 20, mouse_y + 20, width, height)

                # Keep tooltip inside screen
                screen_rect = screen.get_rect()
                if tooltip_rect.right > screen_rect.right:
                    tooltip_rect.right = mouse_x - 20
                if tooltip_rect.bottom > screen_rect.bottom:
                    tooltip_rect.bottom = mouse_y - 20

                # --- Draw rounded background ---
                surf = pygame.Surface((tooltip_rect.width, tooltip_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(surf, (30, 30, 30, 230), (0, 0, tooltip_rect.width, tooltip_rect.height), border_radius=8)
                pygame.draw.rect(surf, (200, 200, 200), (0, 0, tooltip_rect.width, tooltip_rect.height), 2, border_radius=8)
                screen.blit(surf, tooltip_rect.topleft)

                # --- Draw icon ---
                x_offset = tooltip_rect.x + padding
                y_offset = tooltip_rect.y + padding
                if getattr(item, "image", None):
                    icon = pygame.transform.smoothscale(item.image, (icon_size, icon_size))
                    screen.blit(icon, (x_offset, y_offset))
                x_offset += icon_size + spacing

                # --- Draw text ---
                for line in lines:
                    text_surf = font.render(line, True, (255, 255, 255))
                    screen.blit(text_surf, (x_offset, y_offset))
                    y_offset += text_height
                break
            
