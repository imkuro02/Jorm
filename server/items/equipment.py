
from configuration.config import ItemType, EquipmentSlotType, StatType, SKILLS, Color, DamageType, BonusTypes, EQUIPMENT_REFORGES, ActorStatusType
from items.misc import Item
from utils import Table
import skills.skills 
import random
import affects.affects as affects


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
            StatType.SOUL: 0,
            StatType.INVSLOTS: 0
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
            StatType.LVL: 0,
            StatType.INVSLOTS: 0
            }
        
class EquipmentBonus:
    def __init__(   self, 
                    id = 0,
                    type = 'stat',
                    key = 'marmor',
                    val = 69,
                    premade_bonus = False
    ):
        self.id = id
        self.premade_bonus = premade_bonus
        self.type =   type
        self.key =    key
        self.val =    val
        



class EquipmentBonusManager:
    def __init__(self, item):
        self.item = item
        self.bonuses = {}


    def check_if_valid(self, bonus):
       

        if (bonus.type != BonusTypes.REFORGE 
            and bonus.type != BonusTypes.SKILL_LEVEL 
            and bonus.type != BonusTypes.STAT 
            and bonus.type != BonusTypes.STAT_REQ):
            print('def check_if_valid(self, bonus) not of type')
            return False

        if bonus.type == BonusTypes.SKILL_LEVEL:
            if bonus.key not in SKILLS:
                print('def check_if_valid(self, bonus) not in skills')
                return False
        
        if bonus.type == BonusTypes.REFORGE:
            if bonus.key not in EQUIPMENT_REFORGES:
                print(bonus.key, 'def check_if_valid(self, bonus) not in ')
                return False

        if bonus.type == BonusTypes.STAT:
            if bonus.key not in StatType.name:
                print('def check_if_valid(self, bonus) not in stats')
                return False

        return True
    
    def remove_bonus(self, bonus):
        #print(bonus.__dict__, bonus.type == 'reforge')
        #print(EQUIPMENT_REFORGES[bonus.key])
        match bonus.type:
            case BonusTypes.REFORGE:
                if EQUIPMENT_REFORGES[bonus.key]['affliction_to_create'] == 'StatBonusPerItemLevel':
                    reforge_variables = EQUIPMENT_REFORGES[bonus.key]['vars']
                    stat = reforge_variables['var_a']
                    _bonus = float(reforge_variables['var_b'])
                    _bonus = int(_bonus * self.item.stat_manager.reqs[StatType.LVL])
                    self.item.stat_manager.reqs[stat] -= _bonus
                    self.item.stat_manager.stats[stat] -= _bonus
                    
            case BonusTypes.SKILL_LEVEL:
                #if bonus.key in SKILLS:
                #    self.item.skill_manager.learn(bonus.key, bonus.val)
                #    return
                pass
           
            case BonusTypes.STAT:
                if bonus.key in [
                    StatType.HPMAX, StatType.MPMAX, StatType.GRIT, 
                    StatType.FLOW, StatType.MIND, StatType.SOUL, 
                    StatType.PHYARMOR, StatType.MAGARMOR, StatType.INVSLOTS
                    ]:
                    self.item.stat_manager.stats[bonus.key] -= bonus.val
                    
            case BonusTypes.STAT_REQ:
                if bonus.key in [
                    StatType.HPMAX, StatType.MPMAX, StatType.GRIT, 
                    StatType.FLOW, StatType.MIND, StatType.SOUL, 
                    StatType.PHYARMOR, StatType.MAGARMOR, StatType.INVSLOTS, 
                    StatType.LVL
                    ]:
                    self.item.stat_manager.reqs[bonus.key] -= bonus.val
                    
        print(bonus.__dict__,'removed')
        del self.bonuses[bonus.id]

    def add_bonus(self, bonus, recursive = True, merging = True): 
        

        
            
        if bonus.id == 0:
            id = len(self.bonuses) + 1
        else:
            id = bonus.id

        '''
        for i in self.bonuses:
            if not merging:
                break
            if self.bonuses[i].type == bonus.type and self.bonuses[i].key == bonus.key:
                #updated_bonus = self.bonuses[i]
                #self.remove_bonus(updated_bonus)
                #updated_bonus.val = updated_bonus.val + bonus.val
                self.bonuses[i].val = self.bonuses[i].val + bonus.val

                returned_bonus = self.add_bonus(bonus, merging = False)
                # delete it but dont actually run the remove bonus thing
                del self.bonuses[returned_bonus.id]
        
                return
        '''

        if not self.check_if_valid(bonus):
            print('failed to add bonus ', bonus.__dict__)
            return

        self.bonuses[id] = bonus
        bonus.id = id

            
        #print(bonus.__dict__,'added')
        
        if recursive:
            to_del = []
            for bon in self.bonuses.values():
                if bon.type == BonusTypes.REFORGE:
                    to_del.append(bon)

            for bon in to_del:
                self.remove_bonus(bon)
                #print('temp removing reforge', bon)
                
        match bonus.type:
            case BonusTypes.REFORGE:
                if EQUIPMENT_REFORGES[bonus.key]['affliction_to_create'] == 'StatBonusPerItemLevel':
                    reforge_variables = EQUIPMENT_REFORGES[bonus.key]['vars']
                    stat = reforge_variables['var_a']
                    _bonus = float(reforge_variables['var_b'])
                    _bonus = int(_bonus * self.item.stat_manager.reqs[StatType.LVL])
                    self.item.stat_manager.reqs[stat] += _bonus
                    self.item.stat_manager.stats[stat] += _bonus
                    

            case BonusTypes.SKILL_LEVEL:
                if bonus.key in SKILLS:
                    self.item.skill_manager.learn(bonus.key, bonus.val)
                    
            case BonusTypes.STAT:
                if bonus.key in [
                    StatType.HPMAX, StatType.MPMAX, StatType.GRIT, 
                    StatType.FLOW, StatType.MIND, StatType.SOUL, 
                    StatType.PHYARMOR, StatType.MAGARMOR, StatType.INVSLOTS
                    ]:
                    self.item.stat_manager.stats[bonus.key] += bonus.val
                    
            case BonusTypes.STAT_REQ:
                if bonus.key in [
                    StatType.HPMAX, StatType.MPMAX, StatType.GRIT, 
                    StatType.FLOW, StatType.MIND, StatType.SOUL, 
                    StatType.PHYARMOR, StatType.MAGARMOR, StatType.INVSLOTS, 
                    StatType.LVL
                    ]:
                    self.item.stat_manager.reqs[bonus.key] += bonus.val
                    


        if recursive:
            for bon in to_del:
                #bon.id = bonus.id
                self.add_bonus(bon, recursive = False)
                #print('after temp removing reforge, add it back', bon.__dict__)


        # resort list so there are no empty spaces
        tmp = {}
        x = 0
        for i in self.bonuses:
            x += 1
            tmp[x] = self.bonuses[i]
            tmp[x].id = x
            
        self.bonuses = tmp
        #return bonus

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
        output += f'{Color.TOOLTIP}Equipment slot:{Color.NORMAL} {EquipmentSlotType.name[self.slot]}\n'
        output += f'{Color.TOOLTIP}Requirements to equip:{Color.NORMAL}\n'
        t = Table(2,3)
        ordered_stats = [StatType.LVL, StatType.HPMAX, StatType.MPMAX, StatType.PHYARMORMAX, StatType.MAGARMORMAX, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.INVSLOTS]
        for stat in ordered_stats:
            if self.stat_manager.reqs[stat] == 0:
                continue
            col = f'{Color.GOOD}' if self.stat_manager.reqs[stat] <= identifier.stat_manager.stats[stat] else f'{Color.BAD}'
            t.add_data(StatType.name[stat])
            t.add_data(self.stat_manager.reqs[stat], col = col)
        output += t.get_table()
       
        output += f'\n{Color.TOOLTIP}Total stats with bonuses:{Color.NORMAL}\n'
        t = Table(2,3)
        ordered_stats = [StatType.HPMAX, StatType.MPMAX, StatType.PHYARMORMAX, StatType.MAGARMORMAX, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.INVSLOTS]
        for stat in ordered_stats:
            if self.stat_manager.stats[stat] == 0:
                continue
            t.add_data(StatType.name[stat])
            #t.add_data(self.stat_manager.stats[stat])
            if self.stat_manager.stats[stat] < 0:
                t.add_data(f'{self.stat_manager.stats[stat]}', Color.BAD)
            else:
                t.add_data(f'+{self.stat_manager.stats[stat]}', Color.GOOD)
            #t.add_data(f'({new})')
        output += t.get_table()

        if len(self.manager.bonuses.values()) >= 1:
            output += f'\n{Color.TOOLTIP}Special bonus:{Color.NORMAL}\n'
            for bonus in self.manager.bonuses.values():
                col = f'{Color.GOOD}+' if bonus.val >= 1 else f'{Color.BAD}'
                match bonus.type:
                    case BonusTypes.REFORGE:
                        output += f'Reforged: {col.replace("+","")}{bonus.key}{Color.BACK}\n'
                        output += f'          {EQUIPMENT_REFORGES[bonus.key]["description"]}\n'

                    case BonusTypes.SKILL_LEVEL:
                        output += f'Affect {SKILLS[bonus.key]["name"]} by {col}{bonus.val}{Color.BACK}\n'

                    case BonusTypes.STAT:
                        output += f'Affect {StatType.name[bonus.key]} by {col}{bonus.val}{Color.BACK}\n'

                    case BonusTypes.STAT_REQ:
                        output += f'Requirement {StatType.name[bonus.key]} {col}{bonus.val}{Color.BACK}\n'

        if self.equiped == False:
            output += f'\n{Color.TOOLTIP}On equip changes:{Color.NORMAL}\n'
            eq = None
            if identifier.slots_manager.slots[self.slot] != None and identifier.slots_manager.slots[self.slot] != self.id:
                eq = identifier.inventory_manager.items[identifier.slots_manager.slots[self.slot]]
            
            t = Table(3,3)
            no_changes = True
            for stat in ordered_stats:
                difference = self.stat_manager.stats[stat]
                if eq != None:
                    difference = self.stat_manager.stats[stat] - eq.stat_manager.stats[stat]
            

                new_stat = identifier.stat_manager.stats[stat] + difference
                
                if new_stat == identifier.stat_manager.stats[stat]:
                    continue
                elif new_stat < identifier.stat_manager.stats[stat]:
                    no_changes = False
                    t.add_data(f'{StatType.name[stat]}')
                    t.add_data(difference, col=f'{Color.BAD}')
                    t.add_data(f'({new_stat})')
                elif new_stat > identifier.stat_manager.stats[stat]:
                    no_changes = False
                    t.add_data(f'{StatType.name[stat]}')
                    t.add_data(f'+{difference}', col=f'{Color.GOOD}')
                    t.add_data(f'({new_stat})')
            
            if no_changes:
                t.add_data(f'No changes')
                t.add_data(f'')
                t.add_data(f'')
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
                    t.add_data(f'{val}',    f'{Color.BAD}')
                else:
                    t.add_data(f'+{val}',   f'{Color.GOOD}')
                t.add_data(f'({new})')
                
                
            output += t.get_table()
        return output.strip('\n')
     


    def reforge(self, forced_reforge_id = None):
        item = self
        to_del = []
        for bon in item.manager.bonuses.values():
            if bon.type == BonusTypes.REFORGE:
                to_del.append(bon)

        for bon in to_del:
            item.manager.remove_bonus(bon)

        reforge_choices = []
        for i in EQUIPMENT_REFORGES:
            # i is the reforge_id
            #print(EQUIPMENT_REFORGES[i])
            if EQUIPMENT_REFORGES[i]['slot_'+item.slot]:
                reforge_choices.append(EQUIPMENT_REFORGES[i])

        reforge_chances = {}
        _chance = 0
        for i in reforge_choices:
            #print('choice')
            reforge_chances[i['reforge_id']] = {'start':_chance + i['roll_chance'], 'range': i['roll_chance']}
            _chance = _chance + i['roll_chance']


        rolled_reforge = None
        
        if forced_reforge_id == None:
            roll = random.randint(0,_chance)
            # print(roll,_chance)
            for i in reforge_chances:
                if roll <= reforge_chances[i]['start'] and roll >= reforge_chances[i]['range']:
                    #print(i)
                    rolled_reforge = i
                    break
        else:
            rolled_reforge = forced_reforge_id

        if rolled_reforge != None:
            new_bonus = EquipmentBonus(type = BonusTypes.REFORGE, key = rolled_reforge, val = 1, premade_bonus = False)
            item.manager.add_bonus(new_bonus)



        return item

    # called at start of turn

    def use_skill(self, skill_id, triggered_by_damage_obj = None):
        skill_id = skill_id
        skill = SKILLS[skill_id]
        try:
            skill_obj = getattr(skills.skills, f'Skill{skill["script_to_run"]}')
        except AttributeError:
            self.inventory_manager.simple_broadcast(
                f'@redscript_to_run:{skill["script_to_run"]} is not a valid skill object in skills.py@normal',
                f'@redscript_to_run:{skill["script_to_run"]} is not a valid skill object in skills.py@normal')
            return False
        
        use_perspectives = skill['use_perspectives']
        success = True #random.randint(1,100) < (skill['script_values']['chance'][users_skill_level]*100)
        silent_use = True
        no_cooldown = True


        _skill_obj = skill_obj(
            skill_id = skill_id, 
            script_values = skill['script_values'], 
            user = self.inventory_manager.owner, 
            other = self.inventory_manager.owner, 
            users_skill_level = 0, 
            use_perspectives = use_perspectives, 
            success = success, 
            silent_use = silent_use,
            no_cooldown = no_cooldown,
            combat_event = triggered_by_damage_obj.combat_event
        )

        #print('aaa',triggered_by_damage_obj.combat_event == _skill_obj.combat_event)

        _skill_obj.pre_use()
        del _skill_obj

    def get_reforge_id(self):
        for i in self.manager.bonuses.values():
            if i.type == BonusTypes.REFORGE:
                return i.key
        return None

    def set_turn(self):
        pass

    # called at end of turn
    def finish_turn(self):

        if self.get_reforge_id():
            self.reforge(self.get_reforge_id())

        if not self.equiped:
            #print(self.name,'not equipped')
            return
        
        reforge_id = self.get_reforge_id()
        if reforge_id == None:
            return

        if self.inventory_manager.owner.status == ActorStatusType.DEAD:
            return
            
        reforge_obj = None
        affliction_to_create = f'Reforge{EQUIPMENT_REFORGES[reforge_id]["affliction_to_create"]}'
        try:
            reforge_obj = getattr(affects, affliction_to_create)
        except AttributeError:
            err = f'cant set affliction object of {affliction_to_create} on {self} of id {self.premade_id} of unique id {self.id} finish_turn()'
            self.inventory_manager.owner.simple_broadcast(err,err)
            
        if reforge_obj:
            reforge_name = EQUIPMENT_REFORGES[reforge_id]['name']
            #reforge_name = 'Reforged'
            #reforge_description = EQUIPMENT_REFORGES[reforge_id]['description']
            reforge_description = f'Reforged: {reforge_name}'
            slot_name = EquipmentSlotType.name[self.slot]
            wear_or_wield = 'Wearing' if self.slot != EquipmentSlotType.WEAPON else 'Wielding'
            #affliction_name = f'{wear_or_wield} {reforge_name} {slot_name}'
            affliction_name = f'{wear_or_wield} {slot_name}'
            aff = reforge_obj(
                affect_source_actor = self.inventory_manager.owner,
                affect_target_actor = self.inventory_manager.owner,
                name = affliction_name,
                description = reforge_description,
                turns = 3,
                source_item = self,
                reforge_variables = EQUIPMENT_REFORGES[reforge_id]['vars']
            ) 
            self.inventory_manager.owner.affect_manager.set_affect_object(aff)    
            

    # called whenever hp updates in any way
    def take_damage_before_calc(self, damage_obj):
        return damage_obj

    def take_damage_after_calc(self, damage_obj):
        return damage_obj
    
    def deal_damage(self, damage_obj):
        return damage_obj
    
    def dealt_damage(self, damage_obj):
        #if self.stack >= 10:
        #    self.inventory_manager.owner.simple_broadcast(f'You are carrying so much of {self.name} it deals extra damage!','')
        return damage_obj
    
    # called when exp is gained
    def gain_exp(self, exp):
        return exp

        
        


