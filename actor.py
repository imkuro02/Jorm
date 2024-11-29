from copy import deepcopy
from items import Item
import affects
from config import DamageType, ActorStatusType, EquipmentSlotType, StatType

class Actor:
    def __init__(self, name, room):
        self.name = name
        #self.protocol = protocol
        self.room = room
        if self.room != None:
            self.factory = self.room.world.factory
            self.use_manager = self.factory.use_manager

        self.affect_manager = affects.AffectsManager(self)

        self.status = ActorStatusType.NORMAL

        self.slots = {
            EquipmentSlotType.HEAD:      None,
            EquipmentSlotType.NECK:      None,
            EquipmentSlotType.CHEST:     None,
            EquipmentSlotType.HANDS:     None,
            EquipmentSlotType.BELT:      None,
            EquipmentSlotType.LEGS:      None,
            EquipmentSlotType.FEET:      None,
            EquipmentSlotType.TRINKET:   None,
            EquipmentSlotType.PRIMARY:   None,
            EquipmentSlotType.SECONDARY: None
        }

        self.stats = {
            StatType.HPMAX: 10,
            StatType.HP:    10,
            StatType.MPMAX: 10,
            StatType.MP:    10,
            StatType.ARMOR: 0,
            StatType.MARMOR:0,
            StatType.BODY: 0,
            StatType.MIND: 0,
            StatType.SOUL: 0,
            StatType.LVL: 1,
            StatType.EXP: 0,
            StatType.PP: 0,
            }

        self.skills = {
            'swing':3
            }
   
    def pretty_name(self):
        output = ''
        
        match type(self).__name__:
            case "Enemy":
                output = output + f'@red{self.name}@normal'
            case "Player":
                output = output + f'@cyan{self.name}@normal'

        if self.status == ActorStatusType.FIGHTING:
            output = f'{output}'

        

        return output

    def get_character_sheet(self):
        output = f'{self.pretty_name()}\n'
        output += f'{StatType.HP+":":<15} {self.stats[StatType.HP]}/{self.stats[StatType.HPMAX]}\n'
        output += f'{StatType.MP+":":<15} {self.stats[StatType.MP]}/{self.stats[StatType.MPMAX]}\n'
        _piss = [StatType.BODY, StatType.MIND, StatType.SOUL, StatType.ARMOR, StatType.MARMOR]
        for _shit in _piss:
            output += f'{_shit+":":<15} {self.stats[_shit]}\n'
            
        '''
        output += f'Health: @red{self.stats["hp"]}@normal/@red{self.stats["hp_max"]}@normal\n'
        output += f'Mana:   @cyan{self.stats["mp"]}@normal/@cyan{self.stats["mp_max"]}@normal\n'
        #output += f'Damage: {self.stats["damage"]}\n'
        output += f'Armor:  {self.stats["armor"]}\n'
        output += f'Marmor: {self.stats["marmor"]}\n'
        output += f'STR:    {self.stats["str"]}\n'
        output += f'DEX:    {self.stats["dex"]}\n'
        output += f'INT:    {self.stats["int"]}\n'
        output += f'LUK:    {self.stats["luk"]}\n'
        '''
        return output

    def tick(self):
        pass

    def take_damage(self, source, damage, damage_type):
        source, damage, damage_type = self.affect_manager.take_damage(source, damage, damage_type)
 
        match damage_type:
            # the string 'none' can be returned from affect_manager.take_damage() 
            # meaning the damage was completely cancelled by something
            # the affect should sendLine what exactly happened
            # example: physical damage while ethereal should send "You are ethereal"
            case DamageType.CANCELLED: 
                return 
            case DamageType.PHYSICAL:
                damage -= self.stats[StatType.ARMOR]
            case DamageType.MAGICAL:
                damage -= self.stats[StatType.MARMOR]
            case DamageType.PURE:
                pass
            case DamageType.HEALING:
                #print('HEALED')
                self.stats[StatType.HP] += damage
                self.simple_broadcast(
                    f'You heal for {damage}',
                    f'{self.pretty_name()} heals for {damage}'
                    )
                return

        if damage <= 0:
            self.simple_broadcast(
            f'You block',
            f'{self.pretty_name()} blocks'
            )
            return

        self.stats[StatType.HP] -= damage
        self.simple_broadcast(
            f'You take {damage} damage',
            f'{self.pretty_name()} takes {damage} damage'
            )

        if self.stats[StatType.HP] >= self.stats[StatType.HPMAX]:
            self.stats[StatType.HP] = self.stats[StatType.HPMAX]

        if self.stats[StatType.HP] <= 0:
            self.stats[StatType.HP] = 0
            self.status = ActorStatusType.DEAD

            self.simple_broadcast(
                f'@redYou died@normal',
                f'{self.pretty_name()} has died'
                )

            self.die()

    def die(self):
        if self.room.combat != None:
            if self.room.combat.current_actor == self:
                self.room.combat.next_turn()

        item = Item()
        item.name = f'Corpse of {self.name}'
        item.description = f'This is the corpse of {self.name}, kinda gross...'
        self.room.inventory_add_item(item)

        if type(self).__name__ != "Player":
            del self.room.entities[self.name]
            self.room = None

    def simple_broadcast(self, line_self, line_others):
        #print(self.name,[line_self,line_others])
        if self.room == None:
            return
            
        for player in self.room.entities.values():
            if type(player).__name__ != "Player":
                continue
            if player == self:
                if line_self == None:
                    continue
                player.sendLine(f'{line_self}')
            else:
                if line_others == None:
                    continue
                player.sendLine(f'{line_others}')

    def finish_turn(self):
        self.affect_manager.finish_turn()
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
        self.affect_manager.set_turn()
        if type(self).__name__ == "Player":
            output = f'@yellowYour turn.@normal {self.prompt()} @normal'
            self.sendLine(output)
    

