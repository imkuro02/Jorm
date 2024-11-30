import uuid
from config import ItemType

class Item:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.item_type = ItemType.MISC
        self.name = 'Name of item'
        self.description = 'Description here'
        self.history = {}
        self.tags = []
        self.keep = False

    def to_dict(self):
        my_dict = {
            'id': self.id,
            'item_type': self.item_type,
            'name': self.name,
            'description': self.description,
            'history': self.history,
            'tags': self.tags,
            'keep': self.keep
        }
        return my_dict

    def identify(self):
        output = f'{self.name}\n'
        output += f'@cyan{self.description}@normal\n'
        return output
