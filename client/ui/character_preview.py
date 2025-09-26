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

    def draw_preview(self, screen, gender=None, hair=None):
        """
        Draw assembled character layers centered on the screen.
        We try to draw (in order): body, feet, legs, torso, head, hair.
        Each sheet is assumed 3x4; we take the first frame of the 3rd row (row index 2, col 0).
        """
        cx = self.screen_width // 2
        cy = self.screen_height // 2

        # helper to blit if exists
        def try_blit(path):
            if not path:
                return
            frame = self._load_frame(path)
            if frame:
                x = cx - frame.get_width() // 2
                y = cy - frame.get_height() // 2
                screen.blit(frame, (x, y))

        # Body
        body_path = _find_case_variants(os.path.join("assets", "images", "Characters", "Body", (gender or "Male"), "Idle.png"))
        try_blit(body_path)

        # Clothing: Feet, Legs, Torso (best-effort paths)
        feet_path = _find_case_variants(os.path.join("assets", "images", "Characters", "Clothing", (gender or "Male"), "Feet", "Shoes 01 - Shoes", "Idle.png"))
        try_blit(feet_path)

        legs_path = _find_case_variants(os.path.join("assets", "images", "Characters", "Clothing", (gender or "Male"), "Legs", "Pants 01 - Hose", "Idle.png"))
        try_blit(legs_path)

        torso_path = _find_case_variants(os.path.join("assets", "images", "Characters", "Clothing", (gender or "Male"), "Torso", "Shirt 01 - Longsleeve Shirt", "Idle.png"))
        try_blit(torso_path)

        # Head
        head_path = _find_case_variants(os.path.join("assets", "images", "Characters", "Head", (gender or "Male"), "idle.png"))
        try_blit(head_path)

        # Hair (folder)
        if hair:
            hair_path = _find_case_variants(os.path.join("assets", "images", "Characters", "Hair", hair, "Idle.png"))
            try_blit(hair_path)

    def _load_frame(self, path, cols=3, rows=4, row_idx=2, col_idx=0):
        """
        Load (and cache) the specified sheet and return scaled frame:
        - Take frame at (col_idx, row_idx) from a sheet with cols x rows
        - Scale it up by self.scale
        """
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
            # if subsurface fails (frame out of bounds), fallback to whole image
            frame = sheet.copy()

        scaled = pygame.transform.smoothscale(frame, (fw*self.scale, fh*self.scale))
        self._cache[key] = scaled
        return scaled

def _find_case_variants(path):
    """
    Windows is case-insensitive; on other systems filenames could be different.
    Try common variants for 'Idle.png' vs 'idle.png'. Return first existing path or None.
    """
    if os.path.exists(path):
        return path
    # try lowercase filename
    dirname, fname = os.path.split(path)
    candidates = [fname, fname.lower(), fname.capitalize()]
    for c in candidates:
        p = os.path.join(dirname, c)
        if os.path.exists(p):
            return p
    return None
