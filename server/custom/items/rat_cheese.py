
from items.misc import Item
class rat_cheese(Item):
    @classmethod
    def compare_replace(self, item_object):
        if "rat_cheese" != item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def before_get(self, *args, **kwargs):
        print('tertretre')
        print(args, kwargs)
