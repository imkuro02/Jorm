import uuid
from config import ItemType, SKILLS
from items.misc import Item
from skills.manager import use_skill, get_skills


class Consumable(Item):
    def __init__(self):
        super().__init__()
        self.item_type = ItemType.CONSUMABLE
        
        self.skills = []
        self.use_perspectives = {
            'you on you':           'You drink the vile liquid',
            'you on other':         'You splash the vile liquid on #OTHER#',
            'user on user':         '#USER# drinks the vile liquid',
            'user on you':          '#USER# splashes the vile liquid on you',
            'user on other':        '#USER# splashes the vile liquid on #OTHER#',

            'you on you fail':           'You fumble and the vile liquid splashes onto the ground',
            'you on other fail':         'You fumble and the vile liquid splashes onto the ground',
            'user on user fail':         '#USER# fumbles and the vile liquid splashes onto the ground',
            'user on you fail':          '#USER# fumbles and the vile liquid splashes onto the ground',
            'user on other fail':        '#USER# fumbles and the vile liquid splashes onto the ground'
        }
        

    def to_dict(self):
        my_dict = {
            'skills': self.skills
        } | super().to_dict()

        return my_dict

    def identify(self):
        output = super().identify()
        
        id_to_name, name_to_id = get_skills()
        output += f'Contents: {[id_to_name[skill_id] for skill_id in self.skills]}'
        #output += f'Contents: {self.skills}'
        return output

    def use(self, user, target):
        first_skill = True
        for skill in self.skills:
            use_skill(user, target, skill, used_from_consumable = True, forced_perspectives = self.use_perspectives, silent_use = not first_skill)
            first_skill = False
        user.inventory_remove_item(self.id)
