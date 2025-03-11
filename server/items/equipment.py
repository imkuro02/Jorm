
from configuration.config import ItemType, EquipmentSlotType, StatType, SKILLS
from items.misc import Item
from utils import Table

class EquipSkillManager:
    def __init__(self, owner):
        self.owner = owner
        self.skills = {}

    # code copy pasted from actor skill manager
    def learn(self, skill_id, amount = 1):
        if skill_id not in self.skills:
            self.skills[skill_id] = amount
        else:
            self.skills[skill_id] += amount
    
    def unlearn(self, skill_id, amount = 1):
        if skill_id not in self.skills:
            print(f'{self.owner.name} cant unlearn {skill_id} because it is not learned')
            return
        
        if amount == self.skills[skill_id]:
            del self.skills[skill_id]
            return

        self.skills[skill_id] -= amount

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
        
class EquipmentBonus:
    def __init__(   self, 
                    bonus_type = 'stat',
                    bonus_key = 'hp_max',
                    bonus_val = 100
    ):
        self.bonus_type =   bonus_type
        self.bonus_key =    bonus_key
        self.bonus_val =    bonus_val
        

class BonusTypes:
    SKILL_LEVEL = 'skill_level'
    STAT  = 'stat'


class EquipmentBonusManager:
    def __init__(self, item):
        self.item = item
        self.bonuses = {}

    def check_if_bonus_valid(self, bonus):
        if bonus.bonus_type != BonusTypes.SKILL_LEVEL or bonus.bonus_type != BonusTypes.STAT:
            return False

        if bonus.bonus_type == BonusTypes.SKILL_LEVEL:
            if bonus.bonus_key not in SKILLS:
                return False

        if bonus.bonus_type == BonusTypes.STAT:
            if bonus.bonus_key not in StatType.name:
                return False

    def add_bonus(self, bonus): 
        bonus_id = f'{bonus.bonus_type}.{bonus.bonus_key}'
        
        if bonus_id in self.bonuses:
            self.bonuses[bonus_id].bonus_val += bonus.bonus_val
        else:
            self.bonuses[bonus_id] = bonus


        match bonus.bonus_type:
            case 'skill_level':
                self.item.skill_manager.learn(bonus.bonus_key, bonus.bonus_val)
                return
            case 'skill_values':
                pass
                return
            case 'stat':
                self.item.stat_manager.stats[bonus.bonus_key] += bonus.bonus_val
                return
                

        print(f'cant add enchant for some reason {bonus.__dict__}')

    def remove_bonus(self, bonus):
        return

    def read_bonuses(self):
        t = Table(3,1)
        t.add_data('Enchants')
        t.add_data('')
        t.add_data('')


        for en in self.bonuses.values():
            match en.bonus_type:
                case 'skill_level':
                    t.add_data('')
                    t.add_data(SKILLS[en.bonus_key]['name'])
                    t.add_data(f'+{en.bonus_val}','@green')

                case 'skill_values':
                    pass

                case 'stat':
                    pass
                    t.add_data('')
                    t.add_data(StatType.name[en.bonus_key])
                    t.add_data(f'+{en.bonus_val}','@green')

        return t.get_table()


            

class Equipment(Item):
    def __init__(self):
        super().__init__()
        self.item_type = ItemType.EQUIPMENT

        self.slot = EquipmentSlotType.TRINKET
        self.equiped = False

        self.rank = 0 
        
        self.stat_manager = EquipmentStatManager(self)
        self.bonus_manager = EquipmentBonusManager(self)
        self.skill_manager = EquipSkillManager(self)

        '''       
        boon = EquipmentBonus(bonus_type = 'skill_level', bonus_key = 'swing', bonus_val = 1)
        self.bonus_manager.add_bonus(boon)
        boon = EquipmentBonus(bonus_type = 'stat', bonus_key = 'grit', bonus_val = 1)
        self.bonus_manager.add_bonus(boon)
        boon = EquipmentBonus(bonus_type = 'stat', bonus_key = 'armor', bonus_val = 1)
        self.bonus_manager.add_bonus(boon)
        '''

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
        t = Table(columns = 4, spaces = 3)
        t.add_data('Bonuses ')
        t.add_data('')
        t.add_data('')
        t.add_data('')
        #t.add_data('')

        #t.add_data('Stat')
        #t.add_data('Bonus')
        #t.add_data('Req')
        for stat in [StatType.HPMAX, StatType.MPMAX, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.ARMOR, StatType.MARMOR]:
            s = self.stat_manager.stats[stat]
            r = self.stat_manager.reqs[stat]
            #if r == 0 and s == 0:
            #    continue
            t.add_data('')
            t.add_data(StatType.name[stat])

            if identifier.slots_manager.slots[self.slot] != None and identifier.slots_manager.slots[self.slot] != self.id:
                eq_id = identifier.slots_manager.slots[self.slot]
                eq_item = identifier.inventory_manager.items[eq_id]
                
                eq_stats = eq_item.stat_manager.stats
                col = "@normal"

                if eq_stats[stat] < s:
                    col = '@green'
                    t.add_data(f'{s} (+{s-eq_stats[stat]})', col)
                elif eq_stats[stat] > s:
                    col = '@red'
                    t.add_data(f'{s} ({s-eq_stats[stat]})', col)
                elif  eq_stats[stat] == s:
                    t.add_data(f'{s}', col)
                
               
            else:
                t.add_data(s, '@normal')

            t.add_data(r, '@normal' if identifier.stat_manager.stats[stat] >= r else '@red')

       

        if len(self.bonus_manager.bonuses) >= 1:
            t.add_data('Enchants')
            t.add_data('')
            t.add_data('')
            t.add_data('')
            for en in self.bonus_manager.bonuses.values():
                match en.bonus_type:
                    case 'skill_level':
                        t.add_data('')
                        t.add_data(SKILLS[en.bonus_key]['name'])
                        if en.bonus_val >= 0:
                            t.add_data(f'+{en.bonus_val}','@green')
                        else:
                            t.add_data(f'{en.bonus_val}','@red')
                        t.add_data('')

                    case 'skill_values':
                        pass

                    case 'stat':
                        pass
                        t.add_data('')
                        t.add_data(StatType.name[en.bonus_key])
                        if en.bonus_val >= 0:
                            t.add_data(f'+{en.bonus_val}','@green')
                        else:
                            t.add_data(f'{en.bonus_val}','@red')
                        t.add_data('')

        output = output + t.get_table() #+ self.bonus_manager.read_bonuses()
        
        return output





        
        


