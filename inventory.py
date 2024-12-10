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

    def add_item(self, item):
        if len(self.items) >= self.limit:
            return False
        self.items[item.id] = item
        return True

    def remove_item(self, item):
        del self.items[item.id]

    def give_item(self, item, receiver):
        receiver.add_item(item)
        self.remove_item(item)



    