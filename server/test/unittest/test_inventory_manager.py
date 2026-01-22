def test_add_item_stacks_until_max(inventory_factory, item_factory):
    # Given
    inv = inventory_factory()
    first = item_factory("potion", stack=3, stack_max=5)
    second = item_factory("potion", stack=4, stack_max=5)

    # When
    first_added = inv.add_item(first)
    second_added = inv.add_item(second)

    # Then
    assert first_added is True
    assert second_added is True
    items = list(inv.items.values())
    assert len(items) == 2
    assert items[0].stack == 5
    assert items[1].stack == 2


def test_add_item_respects_limit(inventory_factory, item_factory):
    # Given
    inv = inventory_factory(limit=1)
    first = item_factory("apple")
    second = item_factory("bread")

    # When
    first_added = inv.add_item(first)
    second_added = inv.add_item(second)

    # Then
    assert first_added is True
    assert second_added is False
    assert len(inv.items) == 1


def test_remove_items_by_id_reduces_stacks(inventory_factory, item_factory):
    # Given
    inv = inventory_factory(limit=5)
    first = item_factory("gem", stack=2, stack_max=10)
    second = item_factory("gem", stack=3, stack_max=10)

    inv.add_item(first, stack_items=False)
    inv.add_item(second, stack_items=False)

    # When
    removed = inv.remove_items_by_id("gem", stack=4)

    # Then
    assert removed is True
    remaining = [item for item in inv.items.values() if item.premade_id == "gem"]
    assert len(remaining) == 1
    assert remaining[0].stack == 1
