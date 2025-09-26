import os
from .utils import load_json

ITEMS = load_json(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "items.json"))

class Inventory:
    def __init__(self, player):
        self.player = player

    def show(self):
        print(f"{self.player.name}'s Inventory:")
        if not self.player.inventory:
            print("  (empty)")
        for item in self.player.inventory:
            print(f" - {ITEMS[item]['name']}: {ITEMS[item]['description']}")