import uuid

from configuration.config import SKILLS, ItemType
from items.misc import Item
from skills.manager import get_skills, use_skill_from_consumable
from systems.utils import get_object_parent
from items.manager import load_item

class Consumable(Item):
    def __init__(self):
        super().__init__()
        if hasattr(self, 'skills'):
            return

        #self.skill_id = None
        #self.skill_level = 0
        self.skills = {}
            
        self.item_type = ItemType.CONSUMABLE
        self.stack_max = 3

        # if true, delete one stack when consumed
        self.item_del_on_use = True
        # if not none, add one of premade_id item to inv
        self.item_add_on_use = None

    def identify(self, identifier=None):
        output = super().identify()

        id_to_name, name_to_id = get_skills()
        output += f"Contents: {self.skills}"
        if self.trigger_manager.triggers != {}:
            output2 = ''
            for i in self.trigger_manager.triggers:
                if self.trigger_manager.triggers[i]['trigger_action'].__name__ == 'trigger_consume':
                    output2 += f'{i} '

            if output2 != '':
                output +='\nCan be consumed with: '+output2
        return output


    def to_dict(self):
        my_dict = {"skills": self.skill_manager.skills} | super().to_dict()

        return my_dict


    def trigger_consume(self, player, line):
        if len(line.split())<=1:
            return False

        old_line = line
        items = player.get_item(line = line.replace('eat','').replace('drink','').replace('read','').strip(), search_mode='self')
        
        if items == None:
            return False
            

        if items[0] == self:
            attempting_var = 'can_'+old_line.split()[0]
            attempting = old_line.split()[0]

            self.new = False
            player.simple_broadcast(f'You {attempting} the {self.name}', f'{player.pretty_name()} {attempting}s the {self.name}')

            self.use(player, player)
            player.finish_turn()
            return True

    def use(self, user, target):
        if get_object_parent(target) != "Actor":
            super().use(user, target)
            return

        # do these checks if the user is attempting to use the item on something else
        if user is not target:
            return
        
        combat_event = CombatEvent()
        for skill in self.skills.values():
            use_skill_from_consumable(
                user = user, target = user, skill_id = skill['skill_id'], skill_level = skill['skill_lv'], consumable_item = self, combat_event = combat_event
            )
        combat_event.run()

        #user.inventory_manager.remove_item(self, stack=1)


        if self.item_del_on_use != 0:
            user.inventory_manager.remove_item(self, 1)

        if self.item_add_on_use != None:
            item_add_on_use = load_item(self.item_add_on_use)
            user.inventory_manager.add_item(item_add_on_use)

        return True

from combat.combat_event import CombatEvent