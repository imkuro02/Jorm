import uuid
from configuration.config import ItemType

class Item:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.premade_id = None
        self.item_type = ItemType.MISC
        self.name = 'Name of item'
        self.description = 'Description here'

        self.keep = False
        self.owner = None # the inventory manager of this item
    
    def pretty_name(self):
        return self.name

    def to_dict(self):
        my_dict = {
            'id': self.id,
            'premade_id': self.premade_id,
            'item_type': self.item_type,
            'name': self.name,
            'description': self.description,
            'keep': self.keep
        }
        return my_dict

    # function used to save to db
    def save(self):
        my_dict = {
            'premade_id': self.premade_id,
            'id': self.id,
            'item_type': self.item_type,
            'name': self.name,
            'description': self.description,
            'keep': self.keep,
        }
        return my_dict

    def identify(self, identifier = None):
        output = f'{self.name} {"@red(K)@normal" if self.keep else ""}\n'
        output += f'@cyan{self.description}@normal\n'
        return output

    def use(self, user, target):
        if user != target:
            user.simple_broadcast(
                f'You rub {self.pretty_name()} on {target.pretty_name()}... Nothing happens.',
                f'{user.pretty_name()} rubs {self.pretty_name()} on {target.pretty_name()}... Nothing happens.'
            )
        else:
            user.simple_broadcast(
                f'You rub {self.pretty_name()} on yourself... Nothing happens.',
                f'{user.pretty_name()} rubs {self.pretty_name()} on themselves... Nothing happens.'
            )
        return False
