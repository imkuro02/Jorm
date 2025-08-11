
from configuration.config import ItemType, EquipmentSlotType, StatType, SKILLS
from items.misc import Item
from utils import Table

class EquipSkillManager:
    def __init__(self, item):
        self.item = item
        self.skills = {}

    # code copy pasted from actor skill manager
    def learn(self, skill_id, amount = 1):
        if skill_id not in self.skills:
            self.skills[skill_id] = amount
        else:
            self.skills[skill_id] += amount
    
    def unlearn(self, skill_id, amount = 1):
        if skill_id not in self.skills:
            print(f'{self.item.name} cant unlearn {skill_id} because it is not learned')
            return
        
        if amount == self.skills[skill_id]:
            del self.skills[skill_id]
            return

        self.skills[skill_id] -= amount

class EquipmentStatManager:
    def __init__(self, item):
        self.item = item
        
        self.stats = {
            StatType.HPMAX: 0,
            StatType.MPMAX: 0,
            StatType.PHYARMORMAX: 0,
            StatType.MAGARMORMAX:0,
            StatType.GRIT: 0,
            StatType.FLOW: 0,
            StatType.MIND: 0,
            StatType.SOUL: 0
            }
        
        self.reqs = {
            StatType.HPMAX: 0,
            StatType.MPMAX: 0,
            StatType.PHYARMORMAX: 0,
            StatType.MAGARMORMAX:0,
            StatType.GRIT: 0,
            StatType.FLOW: 0,
            StatType.MIND: 0,
            StatType.SOUL: 0,
            StatType.LVL: 0
            }
        
class EquipmentBonus:
    def __init__(   self, 
                    type = 'stat',
                    key = 'marmor',
                    val = 69,
                    premade_bonus = False
    ):
        self.premade_bonus = premade_bonus
        self.type =   type
        self.key =    key
        self.val =    val
        

class BonusTypes:
    SKILL_LEVEL = 'skill_level'
    STAT  = 'stat'


class EquipmentBonusManager:
    def __init__(self, item):
        self.item = item
        self.bonuses = {}

    def check_if_valid(self, bonus):
        if bonus.type != BonusTypes.SKILL_LEVEL or bonus.type != BonusTypes.STAT:
            return False

        if bonus.type == BonusTypes.SKILL_LEVEL:
            if bonus.key not in SKILLS:
                return False

        if bonus.type == BonusTypes.STAT:
            if bonus.key not in StatType.name:
                return False

    def add_bonus(self, bonus): 
        id = len(self.bonuses)
        
        if bonus.val == 0:
            return

        if id in self.bonuses:
            self.bonuses[id].val += bonus.val
        else:
            self.bonuses[id] = bonus

        match bonus.type:
            case 'skill_level':
                if bonus.key in SKILLS:
                    self.item.skill_manager.learn(bonus.key, bonus.val)
                    return
            case 'skill_values':
                pass
                return
            case 'stat':
                if bonus.key in [
                    StatType.HPMAX, StatType.MPMAX, StatType.GRIT, 
                    StatType.FLOW, StatType.MIND, StatType.SOUL, 
                    StatType.PHYARMOR, StatType.MAGARMOR
                    ]:
                    self.item.stat_manager.stats[bonus.key] += bonus.val
                    return
                
        del self.bonuses[id]
        print(f'cant add enchant for some reason {bonus.__dict__}')

    def remove_bonus(self, bonus):
        
        return

            

class Equipment(Item):
    def __init__(self):
        super().__init__()
        self.item_type = ItemType.EQUIPMENT
        self.stack_max = 1

        self.slot = EquipmentSlotType.TRINKET
        self.equiped = False

        self.rank = 0 
        
        self.stat_manager = EquipmentStatManager(self)
        self.manager = EquipmentBonusManager(self)
        self.skill_manager = EquipSkillManager(self)

        '''       
        boon = EquipmentBonus(type = 'skill_level', key = 'swing', val = 1)
        self.manager.add_bonus(boon)
        boon = EquipmentBonus(type = 'stat', key = 'grit', val = 1)
        self.manager.add_bonus(boon)
        boon = EquipmentBonus(type = 'stat', key = 'armor', val = 1)
        self.manager.add_bonus(boon)
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
        output += f'@tipEquipment slot:@normal {EquipmentSlotType.name[self.slot]}\n'
        output += '@tipRequirements to equip:@normal\n'
        t = Table(2,3)
        ordered_stats = [StatType.LVL, StatType.HPMAX, StatType.MPMAX, StatType.PHYARMORMAX, StatType.MAGARMORMAX, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL]
        for stat in ordered_stats:
            if self.stat_manager.reqs[stat] == 0:
                continue
            col = '@good' if self.stat_manager.reqs[stat] <= identifier.stat_manager.stats[stat] else '@bad'
            t.add_data(StatType.name[stat])
            t.add_data(self.stat_manager.reqs[stat], col = col)
        output += t.get_table()
       
        output += '\n@tipTotal stats with bonuses:@normal\n'
        t = Table(2,3)
        ordered_stats = [StatType.HPMAX, StatType.MPMAX, StatType.PHYARMORMAX, StatType.MAGARMORMAX, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL]
        for stat in ordered_stats:
            if self.stat_manager.stats[stat] == 0:
                continue
            t.add_data(StatType.name[stat])
            t.add_data(self.stat_manager.stats[stat])
        output += t.get_table()

        output += '\n@tipSpecial bonus:@normal\n'
        for bonus in self.manager.bonuses.values():
            col = '@good+' if bonus.val >= 1 else '@bad'
            match bonus.type:
                case 'skill_level':
                    
                    output += f'Affect {SKILLS[bonus.key]["name"]} by {col}{bonus.val}@back\n'
                case 'stat':
                    output += f'Affect {StatType.name[bonus.key]} by {col}{bonus.val}@back\n'

        if self.equiped == False:
            output += '\n@tipOn equip changes:@normal\n'
            eq = None
            if identifier.slots_manager.slots[self.slot] != None and identifier.slots_manager.slots[self.slot] != self.id:
                eq = identifier.inventory_manager.items[identifier.slots_manager.slots[self.slot]]
            
            t = Table(3,3)
            for stat in ordered_stats:
                difference = self.stat_manager.stats[stat]
                if eq != None:
                    difference = self.stat_manager.stats[stat] - eq.stat_manager.stats[stat]
            

                new_stat = identifier.stat_manager.stats[stat] + difference
                if new_stat == identifier.stat_manager.stats[stat]:
                    continue
                elif new_stat < identifier.stat_manager.stats[stat]:
                    t.add_data(f'{StatType.name[stat]}')
                    t.add_data(difference, col='@bad')
                    t.add_data(f'({new_stat})')
                elif new_stat > identifier.stat_manager.stats[stat]:
                    t.add_data(f'{StatType.name[stat]}')
                    t.add_data(f'+{difference}', col='@good')
                    t.add_data(f'({new_stat})')
            #output += t.get_table()
            

            def construct_id(bonus):
                return f'{bonus.type}/{bonus.key}'
            
            def construct_dict(bonuses, bonus, positive):
                if bonus.type != 'skill_level':
                    return bonuses
                
                if construct_id(bonus) in bonuses:
                    bonuses[construct_id(bonus)]['val'] += bonus.val * (1 if positive else -1)
                else:
                    bonuses[construct_id(bonus)] = {
                        'type': bonus.type,
                        'key': bonus.key,
                        'val': bonus.val * (1 if positive else -1)
                    }
                return bonuses
            
            bonuses = {}
            for bonus in self.manager.bonuses.values():
                bonuses = construct_dict(bonuses, bonus, positive = True)

            if eq != None:
               for bonus in eq.manager.bonuses.values():
                    bonuses = construct_dict(bonuses, bonus, positive = False)

            '''
            for bonus in bonuses.values():
                #output += f"{'@goodLearn ' if bonus['val'] >= 1 else '@badForgor'}@normal {SKILLS[bonus['key']]['name']} \n"
                if bonus['key'] in identifier.skill_manager.skills:
                    val = bonus['val']
                    curr = identifier.skill_manager.skills[bonus['key']] 
                    new = curr + val
                    #print(new,curr,val)
                    if new > curr:
                        output += f"@goodUpgrade@back {SKILLS[bonus['key']]['name']} by {new-curr}({new})\n"
                        pass
                    elif new < curr and new >= 1:
                        output += f"@badDowngrade@back {SKILLS[bonus['key']]['name']} by {new-curr}({new})\n"
                        pass
                    elif new <= 0:
                        output += f"@badForget@back {SKILLS[bonus['key']]['name']} ({new})\n"
                    else: 
                        continue
                else:
                    output += f"{'@goodLearn@back' if bonus['val'] >= 1 else '@badForget@back'}@normal {SKILLS[bonus['key']]['name']} \n"
            '''
            #t = Table(3,3)
            for bonus in bonuses.values():
                val = bonus['val']
                curr = 0
                new = bonus['val']
                if bonus['key'] in identifier.skill_manager.skills:
                    val = bonus['val']
                    curr = identifier.skill_manager.skills[bonus['key']] 
                    new = curr + val
                
                if new == curr:
                    continue

                t.add_data(f"{SKILLS[bonus['key']]['name']}")
                if new < curr:
                    t.add_data(f'{val}','@bad')
                else:
                    t.add_data(f'+{val}','@good')
                t.add_data(f'({new})')
                
                
            output += t.get_table()
            #print(bonuses)

            

          

        return output
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
            '@good' if identifier.stat_manager.stats[StatType.LVL] >= r[StatType.LVL] else '@bad') 

        output += t.get_table()
        t = Table(columns = 3, spaces = 3)
        t.add_data('@tipStats@back ')
        t.add_data('@tipBonus@back')
        t.add_data('@tipReq@back')
        #t.add_data('')

        #t.add_data('Stat')
        #t.add_data('Bonus')
        #t.add_data('Req')
        for stat in [StatType.HPMAX, StatType.MPMAX, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.PHYARMOR, StatType.MAGARMOR]:
            s = self.stat_manager.stats[stat]
            r = self.stat_manager.reqs[stat]
            
            #if r == 0 and s == 0:
            #    continue
            

            if identifier.slots_manager.slots[self.slot] != None and identifier.slots_manager.slots[self.slot] != self.id:
                
                eq_id = identifier.slots_manager.slots[self.slot]
                eq_item = identifier.inventory_manager.items[eq_id]


                
                eq_stats = eq_item.stat_manager.stats
                col = "@normal"

                if r == 0 and s == 0 and s-eq_stats[stat] == 0:
                    continue

                t.add_data(StatType.name[stat])

                if eq_stats[stat] < s:
                    col = '@good'
                    t.add_data(f'{s} (+{s-eq_stats[stat]})', col)
                elif eq_stats[stat] > s:
                    col = '@bad'
                    t.add_data(f'{s} ({s-eq_stats[stat]})', col)
                elif  eq_stats[stat] == s:
                    t.add_data(f'{s}', col)

                t.add_data(r, '@normal' if identifier.stat_manager.stats[stat] >= r else '@bad')
                
               
            else:
                if r == 0 and s == 0:
                    continue
                t.add_data(StatType.name[stat])
                t.add_data(s, '@normal')
                t.add_data(r, '@normal' if identifier.stat_manager.stats[stat] >= r else '@bad')

       

        

        output = output + t.get_table() + self.manager.read_bonuses()
        
        return output





        
        


