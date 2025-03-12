
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
                    bonus_key = 'marmor',
                    bonus_val = 69,
                    bonus_dont_save_in_db = False
    ):
        self.bonus_dont_save_in_db = bonus_dont_save_in_db
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
        bonus_id = len(self.bonuses)
        
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
        output = '@cyan'
        for en in self.bonuses.values():
            output += 'Enchanted with: '
            match en.bonus_type:
                case 'skill_level':
                    if en.bonus_val >= 0:
                        output += f'@good{SKILLS[en.bonus_key]["name"]}@back raised by @good+{en.bonus_val}@back.'
                    else:
                        output += f'@bad{SKILLS[en.bonus_key]["name"]}@back lowered by @bad{en.bonus_val}@back.'
                    output += '\n'
                case 'skill_values':
                    pass
                case 'stat':
                    stat = StatType.name[en.bonus_key]
                    if en.bonus_val >= 0:
                        output += f'@good{stat}@back raised by @good+{en.bonus_val}@back.'
                    else:
                        output += f'@bad{stat}@back lowered by @bad{en.bonus_val}@back.'
                    output += '\n'
        return output+'@normal'
        if len(self.bonuses) >= 1:
            t = Table(columns = 2, spaces = 3)
            t.add_data('@tipBoost@back')
            t.add_data('@tipBonus@back')
            for en in self.bonuses.values():
                match en.bonus_type:
                    case 'skill_level':
                        t.add_data(SKILLS[en.bonus_key]['name'])
                        if en.bonus_val >= 0:
                            t.add_data(f'+{en.bonus_val}','@good')
                        else:
                            t.add_data(f'{en.bonus_val}','@bad')

                    case 'skill_values':
                        pass

                    case 'stat':
                        pass
                        t.add_data(StatType.name[en.bonus_key])
                        if en.bonus_val >= 0:
                            t.add_data(f'+{en.bonus_val}','@good')
                        else:
                            t.add_data(f'{en.bonus_val}','@bad')
                    
            return t.get_table()
        else:
            return ''


            

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

        output += '@tipRequirements to equip:@normal\n'
        t = Table(2,3)
        ordered_stats = [StatType.LVL, StatType.HPMAX, StatType.MPMAX, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.ARMOR, StatType.MARMOR]
        for stat in ordered_stats:
            if self.stat_manager.reqs[stat] == 0:
                continue
            col = '@good' if self.stat_manager.reqs[stat] <= identifier.stat_manager.stats[stat] else '@bad'
            t.add_data(StatType.name[stat])
            t.add_data(self.stat_manager.reqs[stat], col = col)
        output += t.get_table()
       
        output += '\n@tipTotal stats with bonuses:@normal\n'
        t = Table(2,3)
        ordered_stats = [StatType.HPMAX, StatType.MPMAX, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.ARMOR, StatType.MARMOR]
        for stat in ordered_stats:
            if self.stat_manager.stats[stat] == 0:
                continue
            t.add_data(StatType.name[stat])
            t.add_data(self.stat_manager.stats[stat])
        output += t.get_table()

        output += '\n@tipSpecial bonus:@normal\n'
        for bonus in self.bonus_manager.bonuses.values():
            col = '@good+' if bonus.bonus_val >= 1 else '@bad'
            match bonus.bonus_type:
                case 'skill_level':
                    
                    output += f'Affect {SKILLS[bonus.bonus_key]["name"]} by {col}{bonus.bonus_val}@back\n'
                case 'stat':
                    output += f'Affect {StatType.name[bonus.bonus_key]} by {col}{bonus.bonus_val}@back\n'

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
                    t.add_data(StatType.name[stat])
                    t.add_data(new_stat)
                    t.add_data(difference, col='@bad')
                elif new_stat > identifier.stat_manager.stats[stat]:
                    t.add_data(StatType.name[stat])
                    t.add_data(new_stat)
                    t.add_data(f'+{difference}', col='@good')
            output += t.get_table()

            def construct_bonus_id(bonus):
                return f'{bonus.bonus_type}/{bonus.bonus_key}'
            
            def construct_bonus_dict(bonuses, bonus, positive):
                if bonus.bonus_type != 'skill_level':
                    return bonuses
                
                if construct_bonus_id(bonus) in bonuses:
                    bonuses[construct_bonus_id(bonus)]['bonus_val'] += bonus.bonus_val
                else:
                    bonuses[construct_bonus_id(bonus)] = {
                        'bonus_type': bonus.bonus_type,
                        'bonus_key': bonus.bonus_key,
                        'bonus_val': bonus.bonus_val * positive
                    }
                return bonuses
            
            bonuses = {}
            for bonus in self.bonus_manager.bonuses.values():
                bonuses = construct_bonus_dict(bonuses, bonus, positive = True)

            if eq != None:
               for bonus in eq.bonus_manager.bonuses.values():
                    bonuses = construct_bonus_dict(bonuses, bonus, positive = False)

            for bonus in bonuses.values():
                #output += f"{'@goodLearn ' if bonus['bonus_val'] >= 1 else '@badForgor'}@normal {SKILLS[bonus['bonus_key']]['name']} \n"
                if bonus['bonus_key'] in identifier.skill_manager.skills:
                    if bonus['bonus_val'] > identifier.skill_manager.skills[bonus['bonus_key']]:
                        output += f"@goodUpgrade@back {SKILLS[bonus['bonus_key']]['name']}\n"
                    elif identifier.skill_manager.skills[bonus['bonus_key']] + bonus['bonus_val'] <= 0:
                        output += f"@badDowngrade@back {SKILLS[bonus['bonus_key']]['name']}\n"
                    elif bonus['bonus_val'] < identifier.skill_manager.skills[bonus['bonus_key']]:
                        output += f"@badForget@back {SKILLS[bonus['bonus_key']]['name']}\n"
                    else: 
                        continue
                else:
                    output += f"{'@goodLearn@back ' if bonus['bonus_val'] >= 1 else '@badForget@back'}@normal {SKILLS[bonus['bonus_key']]['name']} \n"

            print(bonuses)

            

          

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
        for stat in [StatType.HPMAX, StatType.MPMAX, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.ARMOR, StatType.MARMOR]:
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

       

        

        output = output + t.get_table() + self.bonus_manager.read_bonuses()
        
        return output





        
        


