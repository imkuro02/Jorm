import uuid

import inventory


class DummyOwner:
    def __init__(self):
        self.name = "DummyOwner"


class DummyItem:
    def __init__(self, premade_id: str, stack: int = 1, stack_max: int = 99):
        self.id = str(uuid.uuid4())
        self.premade_id = premade_id
        self.stack = stack
        self.stack_max = stack_max
        self.can_pick_up = True
        self.time_on_ground = 0
        self.new = True
        self.inventory_manager = None

    def can_tinker_with(self):
        return True


def make_inventory(limit: int = 20):
    return inventory.InventoryManager(DummyOwner(), limit=limit)
