import pytest

import inventory
from items.misc import Item


class DummyOwner:
    def __init__(self):
        self.name = "DummyOwner"


@pytest.fixture()
def item_factory():
    def _make_item(premade_id: str, stack: int = 1, stack_max: int = 99):
        item = Item()
        item.premade_id = premade_id
        item.stack = stack
        item.stack_max = stack_max
        return item

    return _make_item


@pytest.fixture()
def inventory_factory():
    def _make_inventory(limit: int = 20):
        return inventory.InventoryManager(DummyOwner(), limit=limit)

    return _make_inventory
