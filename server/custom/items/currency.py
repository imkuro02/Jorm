from configuration.constants.item_type import ItemType
from items.misc import Item
class CustomCurrency(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_type = ItemType.CURRENCY