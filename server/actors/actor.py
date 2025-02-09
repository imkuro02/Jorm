from copy import deepcopy
import uuid
from combat.manager import Damage
from items.manager import Item
from affects.manager import AffectsManager
from configuration.config import DamageType, ActorStatusType, EquipmentSlotType, StatType
from skills.manager import use_skill
from inventory import InventoryManager
import utils
from party import PartyManager

class CooldownManager:
    def __init__ (self, owner):
        self.owner = owner
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
    def __init__(self, owner):
        self.owner = owner
        self.slots = {
            EquipmentSlotType.HEAD:      None,
            EquipmentSlotType.BODY:      None,
            EquipmentSlotType.WEAPON:    None,
            EquipmentSlotType.TRINKET:   None,
            EquipmentSlotType.RELIC:     None
        }

class Actor:
    def __init__(self, name = None, room = None, _id = None):
        self.name = name
        self.description = ''
        if _id == None:
            self.id = str(uuid.uuid4())
        else: 
            self.id = _id

        #self.protocol = protocol
        self.room = room
        if self.room != None:
            self.factory = self.room.world.factory

        self.affect_manager = AffectsManager(self)
        self.inventory_manager = InventoryManager(self)
        self.slots_manager = SlotsManager(self)
        self.party_manager = PartyManager(self)
        self.status = ActorStatusType.NORMAL
        
        self.stats = {
            StatType.HPMAX: 30,
            StatType.HP:    30,
            StatType.MPMAX: 30,
            StatType.MP:    30,
            StatType.ARMOR: 0,
            StatType.MARMOR:0,
            StatType.GRIT: 10,
            StatType.FLOW: 10,
            StatType.MIND: 10,
            StatType.SOUL: 10,
            StatType.LVL: 1,
            StatType.EXP: 0,
            StatType.PP: 0,

            StatType.THREAT: 0
            }

        self.skills = {
            'swing': 75
            }

        self.cooldown_manager = CooldownManager(self)

        self.recently_send_message_count = 0
   
    def pretty_name(self):
        output = ''
        
        match type(self).__name__:
            case "Enemy":
                output = output + f'@red{self.name}@normal'
            case "Player":
                if self.admin:
                    output = output + f'@byellow{self.name}@normal'
                else:
                    output = output + f'@cyan{self.name}@normal'

        if self.status == ActorStatusType.FIGHTING:
            output = f'{output}'

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
                t.add_data(self.inventory_manager.items[self.slots_manager.slots[i]].name+'')
                #t.add_data(self.inventory_manager.items[self.slots_manager.slots[i]].description)
        output = t.get_table()
        return output

    def get_character_sheet(self):
        output = f'{self.pretty_name()} ({self.status})\n'
        # if no description then ignore
        if self.description != '': 
            output += f'@cyan{self.description}@normal\n'

        output += self.get_character_equipment()

        output += f'{StatType.name[StatType.HP]+":":<15} {self.stats[StatType.HP]}/{self.stats[StatType.HPMAX]}\n'
        output += f'{StatType.name[StatType.MP]+":":<15} {self.stats[StatType.MP]}/{self.stats[StatType.MPMAX]}\n'
        _piss = [StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL, StatType.ARMOR, StatType.MARMOR]
        for _shit in _piss:
            output += f'{StatType.name[_shit]+":":<15} {self.stats[_shit]}\n'
        output += f'{StatType.name[StatType.LVL]}: {self.stats[StatType.LVL]}\n'
        
        return output

    def tick(self):
        if self.recently_send_message_count > 0:
            self.recently_send_message_count -= 1
        if self.status != ActorStatusType.FIGHTING:
            self.cooldown_manager.unload_all_cooldowns()
        
        
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
            self.status = ActorStatusType.DEAD

            self.simple_broadcast(
                f'@redYou died@normal "help rest"',
                f'{self.pretty_name()} has died'
                )

            self.die()

    def take_damage(self, damage_obj: Damage):
        damage_obj = self.affect_manager.take_damage(damage_obj)
        damage_taken = damage_obj.take_damage()
        del damage_obj
        return damage_taken
    
    def deal_damage(self, damage_obj: Damage):
        damage_obj = self.affect_manager.deal_damage(damage_obj)
        damage_dealt = damage_obj.damage_taker_actor.take_damage(damage_obj)
        self.stats[StatType.THREAT] += damage_dealt
        


    def die(self):
        if self.room == None:
            return
        if self.room.combat == None:
            return
        
        if self.room.combat.current_actor == self:
            self.room.combat.next_turn()

        # create a temporary corpse item 
        # this items name and description is NOT stored in db
        item = Item()
        item.name = f'Corpse of {self.name}'
        item.premade_id = 'corpse'
        item.item_type = 'misc'
        item.description = f'This is the corpse of {self.name}, kinda gross...'
        self.room.inventory_manager.add_item(item)

        if type(self).__name__ != "Player":
            del self.room.entities[self.id]
            self.room = None

    def simple_broadcast(self, line_self, line_others, worldwide = False):
        

        if self.room == None:
            return

        if worldwide:
            players = [proto.actor for proto in self.factory.protocols if proto.actor != None]

        else:
            players = [entity for entity in self.room.entities.values() if type(entity).__name__ == "Player"]
            
        for player in players:
            if player == self:
                if line_self == None:
                    continue
                player.sendLine(f'{line_self}')
            else:
                if line_others == None:
                    continue
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
        
        if type(self).__name__ == "Player":
            output = f'@yellowYour turn.@normal {self.prompt()} @normal'
            self.sendLine(output)

        self.affect_manager.set_turn()
        self.cooldown_manager.set_turn()

    

