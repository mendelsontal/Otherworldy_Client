import pygame
import json
import os

class Item:
    items = {}  # master dictionary: key -> Item instance

    @classmethod
    def load_items(cls, folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                item_type = filename.replace(".json", "")  # e.g., "helm", "consumables"
                file_path = os.path.join(folder_path, filename)

                with open(file_path, "r") as f:
                    data = json.load(f)

                for key, info in data.items():
                    cls.items[key] = Item(
                        key=key,
                        name=info.get("name", key),
                        description=info.get("description", ""),
                        stat=info.get("stat", ""),
                        grade=info.get("grade", ""),
                        image_path=info.get("image", None),
                        type=item_type,
                        max_amount=info.get("max_amount", 99)  # e.g. default stack size
                    )

    def __init__(self, key, name, description, stat, grade, image_path, type,
                 max_amount=99, amount=1):
        self.key = key
        self.name = name
        self.description = description
        self.stat = stat
        self.grade = grade
        self.type = type
        self.image_path = image_path
        self.image = None

        # stack handling
        self.amount = amount
        self.max_amount = max_amount

        # Load image if exists
        if image_path and os.path.exists(image_path):
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.image.fill((150, 150, 150, 200))

    def clone(self, amount=1):
        """Make a new instance from this template"""
        return Item(
            key=self.key,
            name=self.name,
            description=self.description,
            stat=self.stat,
            grade=self.grade,
            image_path=self.image_path,
            type=self.type,
            max_amount=self.max_amount,
            amount=amount
        )

    def add_amount(self, value):
        """Increase stack, respecting max"""
        self.amount = min(self.amount + value, self.max_amount)

    def remove_amount(self, value):
        """Decrease stack"""
        self.amount = max(self.amount - value, 0)
