
from configuration.config import ItemType, EquipmentSlotType, StatType
from items.misc import Item
from utils import Table

class EquipmentStatManager:
    def __init__(self, owner):
        self.owner = owner
        
        self.stats = {
            StatType.HPMAX: 0,
            StatType.MPMAX: 0,
            StatType.ARMOR: 0,
            StatType.MARMOR:0,
            StatType.GRIT: 0,
            StatType.FLOW: 0,
            StatType.MIND: 0,
            StatType.SOUL: 0
            }
        
        self.reqs = {
            StatType.HPMAX: 0,
            StatType.MPMAX: 0,
            StatType.ARMOR: 0,
            StatType.MARMOR:0,
            StatType.GRIT: 0,
            StatType.FLOW: 0,
            StatType.MIND: 0,
            StatType.SOUL: 0,
            StatType.LVL: 0
            }
        
class Equipment(Item):
    def __init__(self):
        super().__init__()
        self.item_type = ItemType.EQUIPMENT

        self.slot = EquipmentSlotType.TRINKET
        self.equiped = False

        self.rank = 0 
        
        self.stat_manager = EquipmentStatManager(self)
       
    def to_dict(self):
        my_dict = {
            'slot': self.slot,
            'equiped': self.equiped,
            'stats': self.stat_manager.stats,
            'requirements': self.stat_manager.reqs
        } | super().to_dict()
        
        return my_dict

    def set_stat(self, stat, value):
        self.stat_manager.stats[stat] = value

    def identify(self, identifier = None):
        
        output = super().identify()
        s = self.stat_manager.stats
        r = self.stat_manager.reqs
        if self.slot == None:
            return output
        output += f'Slot: {EquipmentSlotType.name[self.slot]} '
        output += '\n'
        #output += f'{StatType.name[StatType.LVL]}: {r[StatType.LVL]}\n'
        
        if identifier == None:
            return output
        
        t = Table(columns = 2, spaces = 1)
        t.add_data(StatType.name[StatType.LVL]+':')
        t.add_data(
            r[StatType.LVL], 
            '@green' if identifier.stat_manager.stats[StatType.LVL] >= r[StatType.LVL] else '@red') 

        output += t.get_table()
        t = Table(columns = 3, spaces = 3)
        t.add_data('Stat')
        t.add_data('Bonus')
        t.add_data('Req')
        for stat in [StatType.HPMAX, StatType.MPMAX, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.ARMOR, StatType.MARMOR]:
            s = self.stat_manager.stats[stat]
            r = self.stat_manager.reqs[stat]
            #if r == 0 and s == 0:
            #    continue

            t.add_data(StatType.name[stat])

            if identifier.slots_manager.slots[self.slot] != None and identifier.slots_manager.slots[self.slot] != self.id:
                eq_id = identifier.slots_manager.slots[self.slot]
                eq_item = identifier.inventory_manager.items[eq_id]
                
                eq_stats = eq_item.stat_manager.stats
                col = "@normal"

                if eq_stats[stat] < s:
                    col = '@green'
                if eq_stats[stat] > s:
                    col = '@red'
                
                t.add_data(f'{s} ({s-eq_stats[stat]})', col)
            else:
                t.add_data(s, '@normal')

            t.add_data(r, '@normal' if identifier.stat_manager.stats[stat] >= r else '@red')
        output = output + t.get_table()
        '''
        space = 12
        output += f'@normal{"Stat":<{space}} {"Bonus":<{space}} {"Req":<{space}}\n'
        for stat in self.stat_manager.stats.keys():
            s = self.stat_manager.stats[stat]
            r = self.stat_manager.reqs[stat]
            if r == 0 and s == 0:
                continue
            output += f'@normal{StatType.name[stat]:<{space}} {s:<{space}} {r:<{space}}\n'
        '''
        return output





        
        


