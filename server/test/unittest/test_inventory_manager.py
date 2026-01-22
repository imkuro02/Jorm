from conftest import DummyItem, make_inventory


def test_add_item_stacks_until_max():
    inv = make_inventory()
    first = DummyItem("potion", stack=3, stack_max=5)
    second = DummyItem("potion", stack=4, stack_max=5)

    assert inv.add_item(first) is True
    assert inv.add_item(second) is True

    items = list(inv.items.values())
    assert len(items) == 2
    assert items[0].stack == 5
    assert items[1].stack == 2


def test_add_item_respects_limit():
    inv = make_inventory(limit=1)
    first = DummyItem("apple")
    second = DummyItem("bread")

    assert inv.add_item(first) is True
    assert inv.add_item(second) is False


def test_remove_items_by_id_reduces_stacks():
    inv = make_inventory(limit=5)
    first = DummyItem("gem", stack=2, stack_max=10)
    second = DummyItem("gem", stack=3, stack_max=10)

    inv.add_item(first, stack_items=False)
    inv.add_item(second, stack_items=False)

    assert inv.remove_items_by_id("gem", stack=4) is True
    remaining = [item for item in inv.items.values() if item.premade_id == "gem"]
    assert len(remaining) == 1
    assert remaining[0].stack == 1
