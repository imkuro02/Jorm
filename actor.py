from copy import deepcopy
from items import Item



class Actor:
    def __init__(self, name, room):
        self.name = name
        #self.protocol = protocol
        self.room = room

        self.status = 'normal'

        self.slots = {
            'head':         None,
            'neck':         None,
            'chest':        None,
            'legs':         None,
            'boots':        None,
            'trinket':      None,
            'primary':      None,
            'secondary':    None
        }

        self.stats = {
            'hp': 10,
            'hp_max': 10,
            'mp': 10,
            'mp_max': 10,

            'str': 0,
            'dex': 0,
            'int': 0,
            'luk': 0,

            'armor': 0,
            'marmor': 0,

            'damage': 1,

            'level': 1,
            'points': 0,
            'exp': 0
            }

        self.skills = {
            'swing':95
            }
    '''
    def create_new_skills(self):
        return {'swing':50+15}
        
    def create_new_stats(self):
        return {
            'hp': 10,
            'hp_max': 10,
            'mp': 10,
            'mp_max': 10,

            'str': 0,
            'dex': 0,
            'int': 0,
            'luk': 0,

            'armor': 0,
            'marmor': 0,

            'damage': 1,

            'level': 0,
            'points': 0,
            'exp': 0
            }
    '''
    def pretty_name(self):
        output = ''
        
        match type(self).__name__:
            case "Enemy":
                output = output + f'@red{self.name}@normal'
            case "Player":
                output = output + f'@cyan{self.name}@normal'

        if self.status == 'fighting':
            output = f'{output}'

        

        return output

    def get_character_sheet(self):
        output = f'{self.pretty_name()}\n'
        output += f'Health: @red{self.stats["hp"]}@normal/@red{self.stats["hp_max"]}@normal\n'
        output += f'Mana:   @cyan{self.stats["mp"]}@normal/@cyan{self.stats["mp_max"]}@normal\n'
        output += f'Damage: {self.stats["damage"]}\n'
        output += f'Armor:  {self.stats["armor"]}\n'
        output += f'Marmor: {self.stats["armor"]}\n'
        output += f'STR:    {self.stats["str"]}\n'
        output += f'DEX:    {self.stats["dex"]}\n'
        output += f'INT:    {self.stats["int"]}\n'
        output += f'LUK:    {self.stats["luk"]}\n'
        return output

    def tick(self):
        pass

    def take_damage(self, damage, damage_type):
        #print(damage, damage_type)
        match damage_type:
            case 'physical':
                damage -= self.stats['armor']
            case 'magical':
                damage -= self.stats['marmor']
            case 'pure':
                pass
            case 'heal':
                #print('HEALED')
                self.stats['hp'] += damage
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

        self.stats['hp'] -= damage
        self.simple_broadcast(
            f'You take {damage} damage',
            f'{self.pretty_name()} takes {damage} damage'
            )

        if self.stats['hp'] <= 0:
            self.stats['hp'] = 0
            self.status = 'dead'

            self.simple_broadcast(
                f'@redYou died@normal',
                f'{self.pretty_name()} has died'
                )

            self.die()

    def die(self):
        if type(self).__name__ == "Player":
            item = Item()
            item.name = f'Corpse of {self.name}'
            item.description = f'This is the corpse of {self.name}, kinda gross...'
            self.room.inventory_add_item(item)
            return

        item = Item()
        item.name = f'Corpse of {self.name}'
        item.description = f'This is the corpse of {self.name}, kinda gross...'
        self.room.inventory_add_item(item)
        #i.room = None
        del self.room.entities[self.name]
        self.room = None

    def finish_turn(self):
        if self.room.combat == None:
            print('no combat')
            return
        if self != self.room.combat.current_actor:
            print('not my turn')
            return
        self.room.combat.next_turn()

    def simple_broadcast(self, line_self, line_others):
        #print(self.name,[line_self,line_others])
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

