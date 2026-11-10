from items.consumable import Consumable
import ast
import systems.utils
from configuration.constants.stat_type import StatType
from configuration.constants.audio import Audio

""" 
        -------------------------------------------------------------------------
        This item is very weird

        Its name and description are set in code
        the name in code:
                
        self.name = 'Mixed Brew'         

        needs to be set in the config file aswell...
        otherwise you cannot lore for it
        -------------------------------------------------------------------------
"""


class CustomCraftedPotion(Consumable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_properties['skills'] = '{}'
        self.item_properties['herbs_mixed'] = '0'
        self.trigger_manager.trigger_add('mix', self.trigger_mix)
        #self.trigger_manager.trigger_add('test', self.trigger_test)
    
    def after_init(self):
        self.sync_skills()
        
    def sync_skills(self):
        self.skills = ast.literal_eval(self.item_properties['skills'])
        
        self.name = 'Mixed Brew'
        self.description = 'A mixture of herbs and whatnot'

        ha = int(self.item_properties['herbs_mixed'])
        self.description += f'\nIt consists of {ha} herb{"" if ha < 1 else "s"}'
        
        if self.skills == {}:
            self.name = 'Empty Brew'
            self.description = 'This brew needs more herbs'

        self.description += '\n\nYou can "@tipmix <brew> with <herb>@back"'
        self.description += '\nYou can mix 1 herb for every 15 SOUL and MIND'

    def trigger_mix(self, player, line):

        mind = player.stat_manager.stats[StatType.MIND]
        soul = player.stat_manager.stats[StatType.SOUL]
        lvl = int((mind+soul)/15) + 1
        if lvl <= int(self.item_properties['herbs_mixed']):
            player.send_line('This brew is too powerful for you to mix further')
            return True

        line = line.replace('mix','')
        _dict = player.inventory_manager.items

        obj_1, obj_2 = systems.utils.get_two_objects_from_line(line, dict_1 = _dict, dict_2 = _dict)


        if obj_1 != self and obj_2 != self:
            return False
        
        if obj_1 != self and obj_2 == self:
            _obj_a = obj_1
            _obj_b = obj_2
            obj_1 = _obj_b
            obj_2 = _obj_a
        
        if type(obj_2).__name__ != 'Consumable':
            return False
        if ' custom_potion_ingredient_' not in f' {obj_2.premade_id.lower()}':
            return False

        list_pretty_name_objects = [player, obj_1, obj_2]
        br1 = f'{player.id} mix {obj_2.id} into {obj_1.id}'
        br2 = f'{player.id} mixes {obj_2.id} into {obj_1.id}'
        player.pretty_broadcast(br1,br2,list_pretty_name_objects=list_pretty_name_objects,sound=Audio.DRINK)

        player.inventory_manager.remove_item(obj_2, 1)

        for skill in obj_2.skills.values():
            skill_id = skill['skill_id']
            skill_lv = skill['skill_lv']
            new = {'skill_id': str(skill_id), 'skill_lv': 0}
            self.skills[skill_id] = self.skills.get(skill_id, new) 
            self.skills[skill_id]['skill_lv'] += skill['skill_lv']#+ 10
            self.item_properties['skills'] = str(self.skills)

        self.sync_skills()
        self.item_properties['herbs_mixed'] = str(int(self.item_properties['herbs_mixed']) + 1)
        return True



    def trigger_test(self, player, line):
        return
        item_name_or_id = line.replace('mix ','')
        item_found = player.get_item(item_name_or_id)
        if item_found != [self]:
            return False

        skill_id = 'flat_heal_hp'
        skill_lvl = 0

        new = {'skill_id': str(skill_id), 'skill_lv': int(skill_lvl)}
        self.skills[skill_id] = self.skills.get(skill_id, new)
        self.skills[skill_id]['skill_lv'] = self.skills[skill_id].get('skill_lv',0) + 10

        self.item_properties['skills'] = str(self.skills)
        self.sync_skills()
        return True

    def identify(self, *args, **kwargs):
        self.sync_skills()
        return super().identify(*args, **kwargs)
        
    def use(self, *args, **kwargs):
        #if self.skills == {}:
        #    print(args, kwargs)
        self.sync_skills()
        return super().use(*args, **kwargs)
