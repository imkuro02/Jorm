
import uuid
from config import ItemType, EquipmentSlotType, StatType
from items.misc import Item

class Equipment(Item):
    def __init__(self):
        super().__init__()
        self.item_type = ItemType.EQUIPMENT

        self.slot = EquipmentSlotType.TRINKET
        self.equiped = False
        
        self.stats = {
            StatType.HPMAX: 0,
            StatType.MPMAX: 0,
            StatType.ARMOR: 0,
            StatType.MARMOR:0,
            StatType.BODY: 0,
            StatType.MIND: 0,
            StatType.SOUL: 0

            }

        self.requirements = {
            StatType.HPMAX: 0,
            StatType.MPMAX: 0,
            StatType.ARMOR: 0,
            StatType.MARMOR:0,
            StatType.BODY: 0,
            StatType.MIND: 0,
            StatType.SOUL: 0,
            StatType.LVL: 0
            }

    def to_dict(self):
        my_dict = {
            'slot': self.slot,
            'equiped': self.equiped,
            'stats': self.stats,
            'requirements': self.requirements
        } | super().to_dict()
        
        return my_dict

    def set_stat(stat, value):
        self.stats[stat] = value

    def identify(self):

        output = super().identify()
        s = self.stats
        r = self.requirements
        if self.slot == None:
            return output
        output += f'Slot: {EquipmentSlotType.name[self.slot]} '
        if self.equiped:
            output += f'{"@green(Equiped)@normal"}'
        output += '\n'
        output += f'{StatType.LVL}: {r[StatType.LVL]}\n'
        space = 12
        output += f'@normal{"Stat":<{space}} {"Bonus":<{space}} {"Req":<{space}}\n'
        for stat in self.stats.keys():
            s = self.stats[stat]
            r = self.requirements[stat]
            if r == 0 and s == 0:
                continue
            output += f'@normal{StatType.name[stat]:<{space}} {s:<{space}} {r:<{space}}\n'
    
        return output





        
        


