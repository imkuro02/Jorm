from copy import deepcopy
import uuid
from combat.damage_event import Damage
from items.manager import Item
from affects.manager import AffectsManager
from configuration.config import DamageType, ActorStatusType, EquipmentSlotType, StatType, Audio
from skills.manager import use_skill
from inventory import InventoryManager
import utils
from party import PartyManager
from quest import QuestManager
import actors.ai
from dialog import Dialog

class ActorStatManager:
    def __init__(self, actor):
        self.actor = actor
        self.stats = {
            StatType.HPMAX: 30,
            StatType.HP:    30,
            StatType.MPMAX: 0,
            StatType.MP:    0,
            StatType.ARMOR: 0,
            StatType.MARMOR:0,
            StatType.GRIT: 10,
            StatType.FLOW: 10,
            StatType.MIND: 10,
            StatType.SOUL: 10,
            StatType.LVL: 1,
            StatType.EXP: 0,
            StatType.PP: 0,

            StatType.THREAT: 0,
            StatType.INITIATIVE: 0
            }
        
    def hp_mp_clamp_update(self):
        # max
        if self.stats[StatType.HP] >= self.stats[StatType.HPMAX]:
            self.stats[StatType.HP] = self.stats[StatType.HPMAX]

        if self.stats[StatType.MP] >= self.stats[StatType.MPMAX]:
            self.stats[StatType.MP] = self.stats[StatType.MPMAX]

        # min 
        if self.stats[StatType.HP] <= 0:
            self.stats[StatType.HP] = 0

        if self.stats[StatType.MP] <= 0:
            self.stats[StatType.MP] = 0

        # death
        if self.stats[StatType.HP] <= 0:
            self.stats[StatType.HP] = 0
            self.actor.die()

class SkillManager:
    def __init__(self, actor):
        self.actor = actor
        self.skills = {
            'swing': 1
        }

    def delete_skills_at_0(self):
        to_del = []
        for skill in self.skills:
            if self.skills[skill] == 0:
                to_del.append(skill)

        for skill in to_del:
            del self.skills[skill]
                

    def learn(self, skill_id, amount = 1):
        if skill_id not in self.skills:
            self.skills[skill_id] = amount
        else:
            self.skills[skill_id] += amount
        self.delete_skills_at_0()
    
    def unlearn(self, skill_id, amount = 1):
        if skill_id not in self.skills:
            self.skills[skill_id] = -amount
        else:
            self.skills[skill_id] -= amount
        self.delete_skills_at_0()



class CooldownManager:
    def __init__ (self, actor):
        self.actor = actor
        self.cooldowns = {}

    def add_cooldown(self, cooldown, turns):
        self.cooldowns[cooldown] = turns

    def remove_cooldown(self, cooldown):
        if cooldown in self.cooldowns:
            del self.cooldowns[cooldown]

    def unload_all_cooldowns(self, silent = False):
        cool_to_delete = []
        for cool in self.cooldowns:
            cool_to_delete.append(cool)
        for cool in cool_to_delete:
            self.remove_cooldown(cool)

    def finish_turn(self):
        pass

    def set_turn(self):
        cooldowns_to_remove = []
        for i in self.cooldowns:
            self.cooldowns[i] -= 1
            if self.cooldowns[i] <= 0:
                cooldowns_to_remove.append(i)
        for i in cooldowns_to_remove:
            self.remove_cooldown(i)

class SlotsManager:
    def __init__(self, actor):
        self.actor = actor
        self.slots = {
            EquipmentSlotType.HEAD:      None,
            EquipmentSlotType.BODY:      None,
            EquipmentSlotType.WEAPON:    None,
            EquipmentSlotType.TRINKET:   None,
            EquipmentSlotType.RELIC:     None
        }


class Actor:
    def __init__(
        self, 
        _id = None,
        ai = None,
        name = None,
        description = None, 
        room = None, 
        
    ):

        if _id == None:
            self.id = str(uuid.uuid4())
        else: 
            self.id = _id
        self.ai = actors.ai.get_ai(ai)(self)
        self.name = name
        self.description = description
        self.room = room
        if self.room != None:
            self.factory = self.room.world.factory

        
        
        self.inventory_manager =    InventoryManager(self)
        self.slots_manager =        SlotsManager(self)

        self.party_manager =        PartyManager(self)
        self.quest_manager =        QuestManager(self)

        self.stat_manager =         ActorStatManager(self)
        self.status =               ActorStatusType.NORMAL
        self.affect_manager =       AffectsManager(self)
        self.skill_manager =        SkillManager(self)
        self.cooldown_manager =     CooldownManager(self)

        
        self.dialog_tree = None
        

        if self.room != None:
            self.room.move_actor(self, silent = True)
   
    def prompt(self):
        hp =    self.stat_manager.stats[StatType.HP]
        mhp =   self.stat_manager.stats[StatType.HPMAX]
        mp =    self.stat_manager.stats[StatType.MP]
        mmp =   self.stat_manager.stats[StatType.MPMAX]
        if hp <= 0:
            output = f'[@red{hp}@normal/@red{mhp}@normal] (@red0@normal%)@normal '
        else:
            output = f'[@red{hp}@normal/@red{mhp}@normal] (@red{int((hp/mhp)*100)}@normal%)@normal '

        if mp <= 0:
            output += f'[@cyan{mp}@normal/@cyan{mmp}@normal] (@cyan0@normal%)@normal '
        else:   
            output += f'[@cyan{mp}@normal/@cyan{mmp}@normal] (@cyan{int((mp/mmp)*100)}@normal%)@normal'
        return output

    def talk_to(self, talker):
        if talker.current_dialog != None:
            talker.sendLine('You are already conversing.')
            return False
        if self.dialog_tree == None:
            talker.sendLine('There is nothing to talk about.')
            return False
        return True # return true if no errors
        
    def pretty_name(self):
        output = ''
        
        
        match type(self).__name__:
            case "Enemy":
                output = output + f'@purple{self.name}@normal'
            case "Player":
                if self.admin:
                    output = output + f'@byellow{self.name}@normal'
                else:
                    output = output + f'@cyan{self.name}@normal'
            case "Npc":
                output = output + f'@yellow{self.name}@normal'
        
        if self.status == ActorStatusType.FIGHTING:
            output = f'{output}'

        return output

    def get_affects(self, target):
        if len(target.affect_manager.affects) == 0:
            if target == self:
                output = 'You are not affected by anything'
            else:
                output = f'{target.pretty_name()} is not affected by anything'
        else:
            if target == self:
                output = 'You are affected with:\n' 
            else:
                output = f'{target.pretty_name()} is affected with:\n'
            t = utils.Table(3,1)
            t.add_data('Aff')
            t.add_data('x')
            t.add_data('Description')
            #output += f'{"Affliction":<15} {"For":<3} {"Info"}\n'
            
            for aff in target.affect_manager.affects.values():
                #output += f'{aff.info()}'
                t.add_data(aff.name)
                t.add_data(aff.turns)
                t.add_data(aff.description)
            output = output + t.get_table()
        return output

    def get_character_equipment(self, hide_empty = True):
        t = utils.Table(2, spaces = 1)
        for i in self.slots_manager.slots:
            if None == self.slots_manager.slots[i]:
                if hide_empty:
                    continue
                else:
                    t.add_data(EquipmentSlotType.name[i] + ':')
                    t.add_data('---')
            else:
                t.add_data(EquipmentSlotType.name[i] + ':')
                t.add_data(self.inventory_manager.items[self.slots_manager.slots[i]].pretty_name(rank_only = True))
        output = t.get_table()
        return output

    def get_character_sheet(self):
        output = f'{self.pretty_name()} ({self.status})\n'
        # if no description then ignore
        if self.description != None: 
            output += f'@cyan{self.description}@normal\n'

        output += self.get_character_equipment()
        t = utils.Table(2,1)
        t.add_data(StatType.name[StatType.HP])
        t.add_data(f'(@red{self.stat_manager.stats[StatType.HP]}@normal/@red{self.stat_manager.stats[StatType.HPMAX]}@normal)')
        t.add_data(StatType.name[StatType.MP])
        t.add_data(f'(@cyan{self.stat_manager.stats[StatType.MP]}@normal/@cyan{self.stat_manager.stats[StatType.MPMAX]}@normal)')
        _piss = [StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.ARMOR, StatType.MARMOR, StatType.LVL]
        for _shit in _piss:
            t.add_data(StatType.name[_shit]+':')
            t.add_data(self.stat_manager.stats[_shit])

        output += t.get_table()
       
        
        return output

    def heal(self, heal_hp = True, heal_mp = True, value = 1, silent = True):
        if heal_hp:
            damage_obj = Damage(
                damage_taker_actor = self,
                damage_source_actor = self,
                damage_source_action = self,
                damage_value = value,
                damage_type = DamageType.HEALING,
                silent = silent
                )
            damage_obj.run()      
        if heal_mp:    
            damage_obj = Damage(
                damage_taker_actor = self,
                damage_source_actor = self,
                damage_source_action = self,
                damage_value = value,
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.MP,
                silent = silent
                )
            damage_obj.run()   
        self.stat_manager.hp_mp_clamp_update()
        
    def tick(self):
        if self.status != ActorStatusType.FIGHTING:
            self.cooldown_manager.unload_all_cooldowns()
            if self.status != ActorStatusType.DEAD and self.factory.ticks_passed % 30 == 0:
                self.heal()
                
                

    '''
    def deal_damage(self, damage_obj: Damage):
        damage_obj = self.affect_manager.deal_damage(damage_obj)
        damage_obj = damage_obj.damage_taker_actor.take_damage(damage_obj)
        damage_obj.calculate()
        self.affect_manager.dealt_damage(damage_obj)
        self.stat_manager.stats[StatType.THREAT] += damage_obj.damage_value
        return damage_obj

    def take_damage(self, damage_obj: Damage):
        damage_obj = self.affect_manager.take_damage(damage_obj)
        return damage_obj
    '''
    
    
        
    def die(self):
        if self.room == None:
            print(self.id, self.name, 'CANT DIE BECAUSE THERE IS NO ROOM IM NOT IN A ROOM HELP!?')
            return
        
        self.status = ActorStatusType.DEAD

        sound = Audio.ENEMY_DEATH
        if type(self).__name__ == "Player":
            sound = Audio.PLAYER_DEATH

        self.simple_broadcast(
                f'@redYou died@normal "help rest"',
                f'{self.pretty_name()} has died',
                sound = sound
                )
        
        if self.room.combat != None:
            if self.room.combat.current_actor == self:
                self.room.combat.next_turn()

        

        # create a temporary corpse item 
        # this items name and description is NOT stored in db
        #item = Item()
        #item.name = f'Corpse of {self.name}'
        #item.premade_id = 'corpse'
        #item.item_type = 'misc'
        #item.description = f'This is the corpse of {self.name}, kinda gross...'
        #self.room.inventory_manager.add_item(item)

        if type(self).__name__ != "Player":
            del self.room.actors[self.id]
            if self.room.combat != None:
                if self.id in self.room.combat.participants:
                    del self.room.combat.participants[self.id]
            self.room = None

        
        

    def simple_broadcast(self, line_self, line_others, worldwide = False, sound = None):
        

        if self.room == None:
            return

        if worldwide:
            players = [proto.actor for proto in self.factory.protocols if proto.actor != None]

        else:
            players = [actor for actor in self.room.actors.values() if type(actor).__name__ == "Player"]
            
        for player in players:
            if player == self:
                if line_self == None:
                    continue
                player.sendLine(f'{line_self}')
                if sound != None:
                    player.sendSound(sound)
            else:
                if line_others == None:
                    continue
                if sound != None:
                    player.sendSound(sound)
                player.sendLine(f'{line_others}')

    def finish_turn(self, force_cooldown = False):
        # force_cooldown forces timers to go down for affects and skills
        # it should only be set to true on activities that are outside of combat
        # like passing a turn out of combat, but NOT set to true if inside of combat
        # as while you are in combat set_turn gets called on turn start, so
        # that would make all timers go down twice
        if force_cooldown == True:
            self.affect_manager.set_turn()
            self.cooldown_manager.set_turn()

        self.affect_manager.finish_turn()
        self.cooldown_manager.finish_turn()
        
        if self.room == None:
            return
        if self.room.combat == None:
            #print('no combat')
            return
        if self != self.room.combat.current_actor:
            #print('not my turn')
            return
        
        self.room.combat.next_turn()

    
    def set_turn(self):
        
        if self.room == None:
            return
        if self.room.combat == None:
            return
        
        
        if type(self).__name__ == "Player":
            output = f'@yellowYour turn.@normal'
            self.sendLine(output)
            t = utils.Table(10,0)
            par = self
            hp =    par.stat_manager.stats[StatType.HP]
            mhp =   par.stat_manager.stats[StatType.HPMAX]
            mp =    par.stat_manager.stats[StatType.MP]
            mmp =   par.stat_manager.stats[StatType.MPMAX]
            t.add_data(f'[')
            t.add_data(f'@red{hp}')
            t.add_data(f'/')
            t.add_data(f'@red{mhp}')
            t.add_data(f'|')
            t.add_data(f'@cyan{mp}')
            t.add_data(f'/')
            t.add_data(f'@cyan{mmp}')
            t.add_data(f']')
            t.add_data(f' {par.pretty_name()}')

            for par in self.room.combat.participants.values():
                if par == self: 
                    continue
                hp =    par.stat_manager.stats[StatType.HP]
                mhp =   par.stat_manager.stats[StatType.HPMAX]
                mp =    par.stat_manager.stats[StatType.MP]
                mmp =   par.stat_manager.stats[StatType.MPMAX]
                t.add_data(f'[')
                t.add_data(f'@red{hp}')
                t.add_data(f'/')
                t.add_data(f'@red{mhp}')
                t.add_data(f'|')
                t.add_data(f'@cyan{mp}')
                t.add_data(f'/')
                t.add_data(f'@cyan{mmp}')
                t.add_data(f']')
                t.add_data(f' {par.pretty_name()}')
            
            output = t.get_table()
            output = output[:-1] if output.endswith("\n") else output
            self.sendLine(output)

        self.affect_manager.set_turn()
        self.cooldown_manager.set_turn()

    def sendLine(self, line):
        print(f'sendLine called in a object class Npc function? line: {line}')

    def sendSound(self, sfx):
        print(f'sendSound called in a object class Npc function? line: {line}')
    

