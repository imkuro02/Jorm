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
            StatType.HPMAX:     30,
            StatType.HP:        30,
            StatType.MPMAX:     0,
            StatType.MP:        0,
            StatType.PHYARMOR:     0,
            StatType.PHYARMORMAX:  0,
            StatType.MAGARMOR:    0,
            StatType.MAGARMORMAX: 0,
            StatType.GRIT: 10,
            StatType.FLOW: 10,
            StatType.MIND: 10,
            StatType.SOUL: 10,
            StatType.INVSLOTS: 0,
            StatType.LVL: 1,
            StatType.EXP: 0,
            StatType.PP: 0,

            StatType.THREAT: 0,
            StatType.INITIATIVE: 0
            }
        
    def hp_mp_clamp_update(self):
        # max
        if self.stats[StatType.PHYARMOR] >= self.stats[StatType.PHYARMORMAX]:
            self.stats[StatType.PHYARMOR] = self.stats[StatType.PHYARMORMAX]

        if self.stats[StatType.MAGARMOR] >= self.stats[StatType.MAGARMORMAX]:
            self.stats[StatType.MAGARMOR] = self.stats[StatType.MAGARMORMAX]

        # min 
        if self.stats[StatType.PHYARMOR] <= 0:
            self.stats[StatType.PHYARMOR] = 0

        if self.stats[StatType.MAGARMOR] <= 0:
            self.stats[StatType.MAGARMOR] = 0

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
            if self.actor.status != ActorStatusType.DEAD:
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
            EquipmentSlotType.RELIC:     None,
            EquipmentSlotType.BAG:       None
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
        
        
        self.name = name
        self.description = description
        self.room = room
        if self.room != None:
            self.factory = self.room.world.factory
        self.ai = actors.ai.get_ai(ai)(self)

        
        
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

        self.set_base_threat()
   
    def add_prompt_syntax(self, prompt_syntax):
        justing = 3
        translations = {
            '#HP#':             str(self.stat_manager.stats[StatType.HP]).rjust(justing),
            '#HPMAX#':          str(self.stat_manager.stats[StatType.HPMAX]).rjust(justing),

            '#MP#':             str(self.stat_manager.stats[StatType.MP]).rjust(justing),
            '#MPMAX#':          str(self.stat_manager.stats[StatType.MPMAX]).rjust(justing),

            '#PHYARM#':         str(self.stat_manager.stats[StatType.PHYARMOR]).rjust(justing),
            '#PHYARMMAX#':      str(self.stat_manager.stats[StatType.PHYARMORMAX]).rjust(justing),

            '#MAGARM#':         str(self.stat_manager.stats[StatType.MAGARMOR]).rjust(justing),
            '#MAGARMMAX#':      str(self.stat_manager.stats[StatType.MAGARMORMAX]).rjust(justing),

            '#THREAT#':         str(self.stat_manager.stats[StatType.THREAT]).rjust(justing),

            # int((cur_value / max_value) * 100)
            '#HP%#':             str('0' if self.stat_manager.stats[StatType.HPMAX] <= 0 else int((self.stat_manager.stats[StatType.HP] / self.stat_manager.stats[StatType.HPMAX]) * 100)).rjust(justing),
            '#MP%#':             str('0' if self.stat_manager.stats[StatType.MPMAX] <= 0 else int((self.stat_manager.stats[StatType.MP] / self.stat_manager.stats[StatType.MPMAX]) * 100)).rjust(justing),
            '#PHYARM%#':         str('0' if self.stat_manager.stats[StatType.PHYARMORMAX] <= 0 else int((self.stat_manager.stats[StatType.PHYARMOR] / self.stat_manager.stats[StatType.PHYARMORMAX]) * 100)).rjust(justing),
            '#MAGARM%#':         str('0' if self.stat_manager.stats[StatType.MAGARMORMAX] <= 0 else int((self.stat_manager.stats[StatType.MAGARMOR] / self.stat_manager.stats[StatType.MAGARMORMAX]) * 100)).rjust(justing),
   
            '#LHP#':             str(self.stat_manager.stats[StatType.HP]).ljust(justing),
            '#LHPMAX#':          str(self.stat_manager.stats[StatType.HPMAX]).ljust(justing),

            '#LMP#':             str(self.stat_manager.stats[StatType.MP]).ljust(justing),
            '#LMPMAX#':          str(self.stat_manager.stats[StatType.MPMAX]).ljust(justing),

            '#LPHYARM#':         str(self.stat_manager.stats[StatType.PHYARMOR]).ljust(justing),
            '#LPHYARMMAX#':      str(self.stat_manager.stats[StatType.PHYARMORMAX]).ljust(justing),

            '#LMAGARM#':         str(self.stat_manager.stats[StatType.MAGARMOR]).ljust(justing),
            '#LMAGARMMAX#':      str(self.stat_manager.stats[StatType.MAGARMORMAX]).ljust(justing),

            # int((cur_value / max_value) * 100)
            '#LHP%#':             str('0' if self.stat_manager.stats[StatType.HPMAX] <= 0 else int((self.stat_manager.stats[StatType.HP] / self.stat_manager.stats[StatType.HPMAX]) * 100)).ljust(justing),
            '#LMP%#':             str('0' if self.stat_manager.stats[StatType.MPMAX] <= 0 else int((self.stat_manager.stats[StatType.MP] / self.stat_manager.stats[StatType.MPMAX]) * 100)).ljust(justing),
            '#LPHYARM%#':         str('0' if self.stat_manager.stats[StatType.PHYARMORMAX] <= 0 else int((self.stat_manager.stats[StatType.PHYARMOR] / self.stat_manager.stats[StatType.PHYARMORMAX]) * 100)).ljust(justing),
            '#LMAGARM%#':         str('0' if self.stat_manager.stats[StatType.MAGARMORMAX] <= 0 else int((self.stat_manager.stats[StatType.MAGARMOR] / self.stat_manager.stats[StatType.MAGARMORMAX]) * 100)).ljust(justing),
        }

        for trans in translations:
            prompt_syntax = prompt_syntax.replace(trans, str(translations[trans]))

        return prompt_syntax

    def prompt(self, actor_that_asked = None):
        if actor_that_asked == None:
            return 'who asked? (def prompt error)'

        hp =    self.stat_manager.stats[StatType.HP]
        mhp =   self.stat_manager.stats[StatType.HPMAX]
        mp =    self.stat_manager.stats[StatType.MP]
        mmp =   self.stat_manager.stats[StatType.MPMAX]
        #xp =    self.stat_manager.stats[StatType.EXP]
        #mxp =   self.stat_manager.stats[StatType.MPMAX]
        #return(f'{utils.progress_bar(12,hp,mhp,"@red")}{utils.progress_bar(12,mp,mmp,"@blue")}')
        #return(f'{utils.progress_bar(12,hp,mhp,"@red")}')
        return self.add_prompt_syntax(actor_that_asked.settings_manager.prompt)
        
    # only npc class has this
    def get_important_dialog(self, actor_to_compare, return_dict = False):
        return False

    def talk_to(self, talker):
        if talker.current_dialog != None:
            talker.sendLine('You are already conversing')
            return False
        if self.dialog_tree == None:
            talker.sendLine('There is nothing to talk about')
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
        
        #if self.status == ActorStatusType.FIGHTING:
        #    output = f'{output}'
        #output = output + f'{self.party_manager.get_party_id()}'
        return output

    def is_not_in_party_or_is_party_leader(self):
        if self.party_manager.party != None:
            if self.party_manager.party.actor != self:
                return False
        return True

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
        
        
        
        t = utils.Table(4,1)
        '''
        hp =    self.stat_manager.stats[StatType.HP]
        mhp =   self.stat_manager.stats[StatType.HPMAX]
        mp =    self.stat_manager.stats[StatType.MP]
        mmp =   self.stat_manager.stats[StatType.MPMAX]

        ahp =    self.stat_manager.stats[StatType.PHYARMOR]
        amhp =   self.stat_manager.stats[StatType.PHYARMORMAX]
        amp =    self.stat_manager.stats[StatType.MAGARMOR]
        ammp =   self.stat_manager.stats[StatType.MAGARMORMAX]

        t.add_data('Health:')
        x = utils.progress_bar(20,hp,mhp,"@red",style=1)
        t.add_data(x)
        t.add_data('PhyArmor:')
        x = utils.progress_bar(20,ahp,amhp,"@red",style=1)
        t.add_data(x)


        t.add_data('Magicka:')
        x = utils.progress_bar(20,mp,mmp,"@blue",style=1)
        t.add_data(x)
        t.add_data('MagArmor:')
        x = utils.progress_bar(20,amp,ammp,"@blue",style=1)
        t.add_data(x)
        '''
        
        
        # t.add_data(StatType.name[StatType.HP])
        # t.add_data(f'(@red{self.stat_manager.stats[StatType.HP]}@normal/@red{self.stat_manager.stats[StatType.HPMAX]}@normal)')
        # t.add_data(StatType.name[StatType.MP])
        # t.add_data(f'(@cyan{self.stat_manager.stats[StatType.MP]}@normal/@cyan{self.stat_manager.stats[StatType.MPMAX]}@normal)')
        _piss = [StatType.HP, StatType.MP, StatType.PHYARMOR, StatType.MAGARMOR, StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.LVL]
        for _shit in _piss:
            t.add_data(StatType.name[_shit]+':')
            if _shit+'_max' in StatType.name:
                t.add_data(f'{self.stat_manager.stats[_shit]}')
                t.add_data(f'/')
                t.add_data(f'{self.stat_manager.stats[_shit+"_max"]}')
            else:
                t.add_data(self.stat_manager.stats[_shit])
                t.add_data('')
                t.add_data('')

        output += t.get_table()
        if type(self).__name__ == 'Player':
            t = utils.Table(4,1)
            '''
            t.add_data(StatType.name[StatType.EXP][:3]+':')
            xp = self.stat_manager.stats[StatType.EXP]
            mxp = self.get_exp_needed_to_level()
            t.add_data(utils.progress_bar(20,xp,mxp,'@purple',1))
            t.add_data(StatType.name[StatType.PP][:4]+':')
            t.add_data(self.stat_manager.stats[StatType.PP])
            '''

            

            t.add_data('Experience:')
            t.add_data(self.stat_manager.stats[StatType.EXP])
            t.add_data('/')
            t.add_data(self.get_exp_needed_to_level())
            
                
            #    t.add_data(str(self.stat_manager.stats[StatType.EXP]-self.get_exp_needed_to_level()))
            t.add_data('Can level?:')
            t.add_data('@goodYES@normal' if self.stat_manager.stats[StatType.EXP] >= self.get_exp_needed_to_level() else '@badNO@normal')
            t.add_data('')
            t.add_data('')

            t.add_data('Practices:')
            t.add_data(self.stat_manager.stats[StatType.PP])
            t.add_data('')
            t.add_data('')

            t.add_data(StatType.name[StatType.INVSLOTS]+':')
            t.add_data(f'+{self.stat_manager.stats[StatType.INVSLOTS]}')
            t.add_data('')
            t.add_data('')

            

            output += t.get_table()
       
        
        return output

   

    def get_base_threat(self):
        s = self.stat_manager.stats
        return int(s[StatType.LVL] + s[StatType.GRIT] + s[StatType.FLOW] + s[StatType.MIND] + s[StatType.SOUL] / 5)

    def set_base_threat(self):
        #self.stat_manager.stats[StatType.THREAT] = self.get_base_threat()
        self.stat_manager.stats[StatType.THREAT] = 0

    def heal(self, heal_hp = True, heal_mp = True, value = 1, silent = True):
         
        if heal_hp:
            damage_obj = Damage(
                damage_taker_actor = self,
                damage_source_actor = self,
                damage_source_action = self,
                damage_value = value,
                damage_type = DamageType.HEALING,
                add_threat = False,
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
                add_threat = False,
                silent = silent
                )
            damage_obj.run()   

        if heal_hp:
            damage_obj = Damage(
                damage_taker_actor = self,
                damage_source_actor = self,
                damage_source_action = self,
                damage_value = value,
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.PHYARMOR,
                add_threat = False,
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
                damage_to_stat = StatType.MAGARMOR,
                add_threat = False,
                silent = silent
                )
            damage_obj.run()   
        self.stat_manager.hp_mp_clamp_update()
        self.set_base_threat()

        
        
    def tick(self):
        if self.status == ActorStatusType.NORMAL:
            self.cooldown_manager.unload_all_cooldowns()
            if self.factory.ticks_passed % 30 == 0:
                if not self.room.is_an_instance():
                    self.heal(value = self.stat_manager.stats[StatType.LVL])
                
                

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
    
    def gain_exp(self, exp):
        pass

    def gain_practice_points(self, pp):
        pass
        
    def die(self):
        if self.room == None:
            print(self.id, self.name, 'CANT DIE BECAUSE THERE IS NO ROOM IM NOT IN A ROOM HELP!?')
            return

        self.ai.die()
        
        self.status = ActorStatusType.DEAD

        sound = Audio.ENEMY_DEATH

        if type(self).__name__ == "Player":
            sound = Audio.PLAYER_DEATH
        else:
            sound = Audio.ENEMY_DEATH
            

        self.simple_broadcast(
                f'@redYou died@normal "help rest"',
                f'{self.pretty_name()} has died',
                sound = sound
                )
        
        if type(self).__name__ == 'Player':
            lost_exp = int(self.stat_manager.stats[StatType.EXP]*0.1)
            self.collect_lost_exp_rooms[self.room.id] = lost_exp
            self.gain_exp(-lost_exp)
        
        if self.room.combat != None:
            if self.room.combat.current_actor == self:
                self.room.combat.next_turn()

        if type(self).__name__ != "Player":
            del self.room.actors[self.id]
            if self.room.combat != None:
                if self.id in self.room.combat.participants:
                    del self.room.combat.participants[self.id]
            self.room = None

        
        

    def simple_broadcast(self, line_self, line_others, send_to = 'room', sound = None, msg_type = None):
        if self.room == None:
            return

        if send_to == 'world':
            players = [proto.actor for proto in self.factory.protocols if proto.actor != None]

        if send_to == 'room':
            players = [actor for actor in self.room.actors.values() if type(actor).__name__ == 'Player']

        if send_to == 'room_not_party':
            players = [actor for actor in self.room.actors.values() if type(actor).__name__ == 'Player' and actor.party_manager.get_party_id() != self.party_manager.get_party_id()]

        if send_to == 'room_party':
            players = [actor for actor in self.room.actors.values() if type(actor).__name__ == 'Player' and  actor.party_manager.get_party_id() == self.party_manager.get_party_id()]
            
        #print(players)
        for player in players:
            if player == self:
                if line_self == None:
                    continue
                player.sendLine(f'{line_self}', msg_type = msg_type)
                if sound != None:
                    player.sendSound(sound)
            else:
                if line_others == None:
                    continue
                if sound != None:
                    player.sendSound(sound)
                player.sendLine(f'{line_others}', msg_type = msg_type)

    def finish_turn(self, force_cooldown = False):
        # force_cooldown forces timers to go down for affects and skills
        # it should only be set to true on activities that are outside of combat
        # like passing a turn out of combat, but NOT set to true if inside of combat
        # as while you are in combat set_turn gets called on turn start, so
        # that would make all timers go down twice
        if force_cooldown:
            self.affect_manager.set_turn()
            self.cooldown_manager.set_turn()
            self.inventory_manager.set_turn()

        self.affect_manager.finish_turn()
        self.cooldown_manager.finish_turn()
        self.inventory_manager.finish_turn()
        
        if self.room == None:
            return
        if self.room.combat == None:
            #print('no combat')
            return
        if self != self.room.combat.current_actor:
            #print('not my turn')
            return
        
        self.room.combat.next_turn()

    def show_prompts(self, order = None):
        # return if received a empty list of orders
        if order == None:
            return

        if type(self).__name__ == "Player":
            output = ''
            #output = f'@yellowYour turn.@normal'
            #self.sendLine(output)
            par = self
            
            #output = par.prompt(self)+' '+par.pretty_name()+' '+par.ai.get_prediction_string(who_checks=self) + '\n'
            if order == None:
                _list = self.room.combat.participants.values()
            else:
                _list = order

            for par in _list:
                if par.status == ActorStatusType.DEAD:
                    continue
                if par == self: 
                    output += par.prompt(self)+' '+'You'+' '+par.ai.get_prediction_string(who_checks=self) + '\n'
                else:
                    output += par.prompt(self)+' '+par.pretty_name()+' '+par.ai.get_prediction_string(who_checks=self) + '\n'
            
            output = output[:-1] if output.endswith("\n") else output
            self.sendLine(output)

    def set_turn(self):
        if type(self).__name__ == "Player":
            output = f'@yellowYour turn.@normal'
            self.sendLine(output)
            '''
            order = self.room.combat.order
            if order == []:
                output = f'@yellowYour turn.@normal'
                self.sendLine(output)
            else:
                output = f'@yellowYour turn.@normal Turns after yours:'
                self.sendLine(output)
                self.show_prompts(self.room.combat.order)
            '''
            
        if self.room == None:
            return
        if self.room.combat == None:
            return
        
        
        
           
            

        self.affect_manager.set_turn()
        self.cooldown_manager.set_turn()
        self.inventory_manager.set_turn()
        #self.stat_manager.stats[StatType.THREAT] = int(self.stat_manager.stats[StatType.THREAT]*.90)

    def sendLine(self, line, msg_type = None):
        print(f'sendLine called in a object class Npc function? line: {line}')

    def sendSound(self, sfx):
        print(f'sendSound called in a object class Npc function? line: {sfx}')
    

