import npcs
from player import Player
import time
#from items import Item
import uuid
import random
from combat import Combat


class Room:
    def __init__(self, world, uid, name, description, exits, dungeon = None):
        self.world = world
        self.uid = uid
        self.name = name
        self.description = description
        self.exits = exits
        self.inventory = {}
        

        self.combat = None
        self.dungeon = dungeon

        self.entities = {}
        #self.players = {}
        #self.npcs = {}

    def next(self):
        return

    def tick(self):
        if self.combat == None:
            return
        self.combat.tick()

    #def spawn_enemy(self, name):
    #    _ = Enemy(name, self)

    def inventory_add_item(self, item):
        self.inventory[item.id] = item

    def inventory_remove_item(self, item_id):
        del self.inventory[item_id]

    def new_combat(self):
        if self.combat != None:
            #print('there is combat')
            return 'There is already a fight here!'

        participants = {}
        npcs_here = False
        players_here = False
        for i in self.entities.values():
            #print(i)
            if type(i).__name__ == "Player":
                participants[i.name] = i
                players_here = True
            if type(i).__name__ == "Enemy":
                participants[i.name] = i
                npcs_here = True

        if players_here and npcs_here:
            self.combat = Combat(self, participants)
        
    def move_player(self, player, silent = False):
        #old_room = player.room

        #for p in player.room.entities.values():
        #    if not silent and p != player and isinstance(p, Player):
        #        p.sendLine(f'{player.pretty_name()} went to {self.name}.')

        #new_room.move_player(self)

        if player in player.room.entities.values():
            del player.room.entities[player.name]
        player.room = self
        self.entities[player.name] = player

        #if not silent:
        #    player.sendLine(f'You arrived at {self.name}.')

        #    for p in player.room.entities.values():
        #        if p != player and isinstance(p, Player):
        #            p.sendLine(f'{player.pretty_name()} arrived from {old_room.name}.')

        player.command_look('')
        #if self.combat == None:
        #    self.new_combat()

    def move_enemy(self, enemy):
        #if enemy in enemy.room.npcs.values():
        #    del enemy.room.players[player.name]
        enemy.room = self
        self.entities[enemy.name] = enemy

    def explore(self):
        if self.dungeon != None:
            uid = str(uuid.uuid4())
            dungeon = Dungeon(self.world, uid)
            self.world.dungeons[uid] = dungeon
            players_to_move = []

            for i in self.entities.values():
                if isinstance(i, Player):
                    players_to_move.append(i)

            for i in players_to_move:
                i.sendLine(f'You explore {i.room.name}')
                dungeon.move_player(i, True)
                
            for i in players_to_move:
                i.command_look('')
            
                
            #dungeon.reload_room()
                
class Dungeon(Room):
    def __init__(self, world, uid):
        super().__init__(world, uid, '', '')
        self.floor = 0
        self.ticks_passed = 0
        self.party_is_moving = False
        self.room_types = [
            ['Past the entrance','0'],
            ['Dungeon corridor','1'],
            ['Sinkhole','2'],
            ['A kitchen?','3'],
        ]

        self.traveling_messages = [
            'Are you walking in circles?',
            '*BONK* ouch, You should of brought a torch!',
            'EWWW! #PLAYER# stepped in something gross!',
            'Are we there yet? - #PLAYER#',
            'The air is suffecating you...'
        ]

        self.name = self.room_types[0][0]
        self.description = self.room_types[0][1]
        
    def reload_room(self):
        # reset the room
        for i in self.entities.values():
            if isinstance(i, Player):
                continue

            del self.entities[i.name]
            i.room = None
            
        self.inventory = {}

        # set moving to false to stop the funny messages
        self.party_is_moving = False

        # get random room layout
        index = random.randint(0,len(self.room_types)-1)
        
        # set name and description form layout
        self.name = self.room_types[index][0]
        self.description = self.room_types[index][1]

        # ---
        #   insert enemy add code here
        # ---

        # attempt to start combat
        self.new_combat()

        # view new room
        for i in self.entities.values():
            if isinstance(i, Player):
                i.command_look('')

    def tick(self):
        super().tick()
        self.ticks_passed += 1
        if self.party_is_moving and self.ticks_passed % 30*2 == 0:
            load_room = random.randint(0,10)
            if load_room <= 8:
                travel_message = random.choice(self.traveling_messages)
                broadcaster = random.choice([key for key in self.entities.values()])
                if type(broadcaster).__name__ != "Player":
                    return
                #broadcaster = self.entities[broadcaster]
                broadcaster.simple_broadcast(
                    '@gray'+travel_message.replace('#PLAYER#','you')+'@normal',
                    '@gray'+travel_message.replace('#PLAYER#', broadcaster.name)+'@normal'
                )
            else:
                self.reload_room()

    def next(self):
        self.party_is_moving = True
        

class World:
    def __init__(self, factory):
        self.factory = factory
        '''
        self.rooms = {
            'home': Room(self, 'home','Town', 'The recall point'),
            #'shop': Room(self, 'shop','The Store', 'Buy items, sell loot.'),
            #'market': Room(self, 'market','Black Market', 'Sell your loot for more...'),
            #'dungeon1': Room(self, 'dungeon1','A Dungeon Entrance', 'Holy fuck its an actual dungeon what!', True)
            }

        self.dungeons = {}

        #self.rooms['market'].spawn_enemy()
        '''
        self.rooms = {}
        world = self.factory.config.WORLD
        for r in world['world']:
            room = world['world'][r]
            self.rooms[r] = Room(self, r, room['name'], room['description'], room['exits']) 
            if 'enemies' in room:
                for enemy in room['enemies']:
                    #self.rooms[r].spawn_enemy(enemy)
                    npcs.create_enemy(self.rooms[r], enemy)

    def save_world(self):
        pass

    def tick(self):
        for i in self.rooms.values():
            i.tick()
        #for i in self.dungeons.values():
        #    i.tick()
