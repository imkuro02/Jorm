from configuration.config import ItemType

class InventoryManager:
    def __init__(self, owner, limit = 20):
        self.owner = owner
        self.limit = limit
        self.items = {}

    def item_count(self):
        return len(self.items)

    def is_empty(self):
        if len(self.items) == 0: 
            return True
        return False

    def add_item(self, item, stack_items = True):
        if stack_items:
            for _i in self.items.values():
                if item.premade_id != _i.premade_id:
                    continue
                if item.item_type != ItemType.MISC:
                    continue
                if _i.item_type != ItemType.MISC:
                    continue
                _i.stack += item.stack
                return True
            
        if len(self.items) >= self.limit:
            return False
        self.items[item.id] = item
        item.new = True
        return True

    def remove_item(self, item):
        del self.items[item.id]

    def give_item(self, item, receiver):
        receiver.add_item(item)
        self.remove_item(item)

    def all_items_set_new(self, new = False):
        for i in self.items.values():
            i.new = new




    