import uuid
from config import ItemType, SKILLS
from items.misc import Item
import skills

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
            'user on other':        '#USER# splashes the vile liquid on #OTHER#'
        }
        

    def to_dict(self):
        my_dict = {
            'id': self.id,
            'item_type': self.item_type,
            'name': self.name,
            'description': self.description,
            'history': self.history,
            'tags': self.tags,
            'keep': self.keep,

            'skills': self.skills
            
        }
        return my_dict

    def identify(self):
        output = super().identify()
        
        id_to_name, name_to_id = FACTORY.use_manager.get_skills()
        output += f'Contents: {[id_to_name[skill_id] for skill_id in self.skills]}'
        #output += f'Contents: {self.skills}'
        return output

    def use(self, user, target):
        for skill in self.skills:
            script = SKILLS[skill]['script_to_run']['name_of_script']
            arguments = SKILLS[skill]['script_to_run']['arguments']
            script = getattr(skills, script)
            skills.use_broadcast(user, target, self.use_perspectives)
            script(user, target, arguments)
        user.inventory_remove_item(self.id)