from configuration.constants.item_type import ItemType
from items.misc import Item
class Currency(Item):
    @classmethod
    def compare_replace(self, item_object):
        if "currency_" not in item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_type = ItemType.CURRENCY