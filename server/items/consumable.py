import uuid
from configuration.config import ItemType, SKILLS
from items.misc import Item
from skills.manager import use_skill_from_consumable, get_skills

class Consumable(Item):
    def __init__(self):
        super().__init__()
        self.item_type = ItemType.CONSUMABLE
        
        self.skills = []
        self.use_perspectives = {
            'you on you':           'no use perspective, check Consumable Class',
            'you on other':         'no use perspective, check Consumable Class',
            'user on user':         'no use perspective, check Consumable Class',
            'user on you':          'no use perspective, check Consumable Class',
            'user on other':        'no use perspective, check Consumable Class',

            'you on you fail':           'no use perspective, check Consumable Class',
            'you on other fail':         'no use perspective, check Consumable Class',
            'user on user fail':         'no use perspective, check Consumable Class',
            'user on you fail':          'no use perspective, check Consumable Class',
            'user on other fail':        'no use perspective, check Consumable Class'
        }
        

    def to_dict(self):
        my_dict = {
            'skills': self.skills
        } | super().to_dict()

        return my_dict

    def identify(self, identifier = None):
        output = super().identify()
        
        id_to_name, name_to_id = get_skills()
        output += f'Contents: {[id_to_name[skill_id] for skill_id in self.skills]}'
        #output += f'Contents: {self.skills}'
        return output

    def use(self, user, target):
        # do these checks if the user is attempting to use the item on something else
        if user is not target:
            if user.room.combat == None:
                user.sendLine('You can\'t use items on others out of combat')
                return

            if user not in user.room.combat.participants.values():
                user.sendLine(f'You can\'t use items on others while you are not in combat')
                return

            if target not in user.room.combat.participants.values():
                user.sendLine(f'You can\'t use items on others while they are not fighting')
                return

        first_skill = True
        for skill in self.skills:
            use_skill_from_consumable(user = user, target = target, skill_id = skill, consumable_item = self)
        user.inventory_manager.remove_item(self)
        return True
