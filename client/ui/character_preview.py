# src/character_preview.py
import pygame
import os

class CharacterPreview:
    def __init__(self, font, screen_width, screen_height, scale=3):
        self.font = font
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale = scale
        self._cache = {}  # cache loaded frame surfaces by path

    def draw_preview(self, screen, appearance=None, gear=None, pos=None):
        """
        Draw assembled character using the character's appearance and gear.
        - appearance: dict with 'gender' and 'hair'
        - gear: dict with 'helm', 'armor', 'pants', 'weapon', 'accessory'
        """
        if not appearance:
            appearance = {}
        if not gear:
            gear = {}

        gender = appearance.get("gender", "Male")
        hair = appearance.get("hair")

        cx, cy = (self.screen_width // 2, self.screen_height // 2) if pos is None else pos

        def try_blit(path):
            if not path:
                return
            frame = self._load_frame(path)
            if frame:
                x = cx - frame.get_width() // 2
                y = cy - frame.get_height() // 2
                screen.blit(frame, (x, y))

        # Draw layers in proper order

        # 1. Body
        body_path = _find_case_variants(os.path.join("client", "assets", "images", "Characters", "Body", gender, "Idle.png"))
        try_blit(body_path)

        # 2. Clothing layers: feet, legs, torso
        clothing_layers = {
            "Feet": gear.get("feet", "Shoes 01 - Shoes"),
            "Legs": gear.get("pants", "Pants 01 - Hose"),
            "Torso": gear.get("armor", "Shirt 01 - Longsleeve Shirt")
        }
        for layer, name in clothing_layers.items():
            path = _find_case_variants(os.path.join("client", "assets", "images", "Characters", "Clothing", gender, layer, name, "Idle.png"))
            try_blit(path)

        # 3. Head
        head_path = _find_case_variants(os.path.join("client", "assets", "images", "Characters", "Head", gender, "Idle.png"))
        try_blit(head_path)

        # 4. Helm/Accessory if any
        for layer, key in [("Helm", "helm"), ("Accessory", "accessory")]:
            item = gear.get(key)
            if item:
                path = _find_case_variants(os.path.join("client", "assets", "images", "Characters", "Equipment", layer, item, "Idle.png"))
                try_blit(path)

        # 5. Hair
        if hair:
            hair_path = _find_case_variants(os.path.join("client", "assets", "images", "Characters", "Hair", hair, "Idle.png"))
            try_blit(hair_path)

        # 6. Weapon
        weapon = gear.get("weapon")
        if weapon:
            path = _find_case_variants(os.path.join("client", "assets", "images", "Characters", "Equipment", "Weapon", weapon, "Idle.png"))
            try_blit(path)

    def _load_frame(self, path, cols=3, rows=4, row_idx=2, col_idx=0):
        if not path or not os.path.exists(path):
            return None
        key = (path, cols, rows, row_idx, col_idx, self.scale)
        if key in self._cache:
            return self._cache[key]

        sheet = pygame.image.load(path).convert_alpha()
        fw = sheet.get_width() // cols
        fh = sheet.get_height() // rows
        rect = pygame.Rect(col_idx*fw, row_idx*fh, fw, fh)
        try:
            frame = sheet.subsurface(rect).copy()
        except Exception:
            frame = sheet.copy()

        scaled = pygame.transform.smoothscale(frame, (fw*self.scale, fh*self.scale))
        self._cache[key] = scaled
        return scaled

def _find_case_variants(path):
    if os.path.exists(path):
        return path
    dirname, fname = os.path.split(path)
    candidates = [fname, fname.lower(), fname.capitalize()]
    for c in candidates:
        p = os.path.join(dirname, c)
        if os.path.exists(p):
            return p
    return None
