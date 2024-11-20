from npcs import Enemy
from player import Player
import time
#from items import Item
import uuid
import random
from combat import Combat

class _Combat:
    def __init__(self, room, team1, team2):
        self.room = room
        self.team1 = team1
        self.team2 = team2
        self.order = []
        self.current_actor = None
        self.time_since_turn_finished = 0
        self.round = 1
        
    def tick(self):
        self.time_since_turn_finished += 1
        print(self.time_since_turn_finished, len(self.team1), len(self.team2))
        if self.time_since_turn_finished == 30*20:
            if isinstance(self.current_actor, Player):
                self.current_actor.simple_broadcast(
                    'Your turn is over in 10 seconds.',
                    f'{self.current_actor.name}\'s turn is over in 10 seconds.'
                )

        if self.time_since_turn_finished >= 30*30:
            if isinstance(self.current_actor, Player):
                self.current_actor.simple_broadcast(
                    'You missed your turn.',
                    f'{self.current_actor.name} missed their turn.'
                )

            self.time_since_turn_finished = 0
            self.next_turn()
        
        team1_died = True
        for i in self.team1.values():
            if i.status != 'dead':
                team1_died = False
            i.tick()
            
        if team1_died:
            self.combat_over(winner = self.team2, loser = self.team1)
            return

        team2_died = True
        for i in self.team2.values():
            if i.status != 'dead':
                team2_died = False
            i.tick()

        if team2_died:
            self.combat_over(winner = self.team1, loser = self.team2)
            return

        #print(f'THIS GUY LEFT AYO? {self.current_actor.name in self.room.players}')
        #print(len(self.team1), len(self.team2))
        #if self.current_actor not in self.room.players.values() and self.current_actor not in self.room.npcs.values():
        #    print(f'This guy left -> ',self.current_actor)
        #    self.next_turn()

        if self.current_actor.room != self.room:
            print('current actor is not here')
            if self.current_actor.name in self.team1: del self.team1[self.current_actor.name]
            if self.current_actor.name in self.team2: del self.team2[self.current_actor.name]
            self.next_turn()
            return

        if self.current_actor.status == 'dead':
            self.next_turn()
            return
            

    def combat_over(self, winner, loser):
        print('combat over', winner)
        players_to_move = []
        enemies_to_remove = []

        for i in winner.values():
            if isinstance(i, Player):
                i.protocol.sendLine('@yellowYou won this fight!@normal')
        for i in loser.values():
            if isinstance(i, Player):
                players_to_move.append(i)
                i.protocol.sendLine('@redYou lost this fight!@normal')

        for i in loser.values():
            if isinstance(i, Enemy):
                enemies_to_remove.append(i)

        for i in players_to_move:
            i.protocol.factory.world.rooms['home'].move_player(i)
            i.status = 'normal'

        for i in self.team1.values():
            i.status = 'normal'
        for i in self.team2.values():
            i.status = 'normal'

        self.team1 = {}
        self.team2 = {}
        self.room.combat = None

    def next_turn(self):
        self.time_since_turn_finished = 0
        if len(self.order) == 0:
            self.initiative()
            return
        
        self.current_actor = self.order[0]
        self.order.pop(0)
        self.current_actor.set_turn()

    def initiative(self):
        print('initiative', len(self.team1), len(self.team2))
        
        for i in self.team1.values():
            if i.status != 'dead':
                self.order.append(i)
        for i in self.team2.values():
            if i.status != 'dead':
                self.order.append(i)

        for i in self.order:
            if isinstance(i, Player):
                combat_stats = f'\n@yellowCombat overview (Round {self.round})@normal:\n'
                for participant in self.order:
                    
                    combat_stats = combat_stats + f'{participant.pretty_name()} [@red{participant.stats["hp"]}/{participant.stats["hp_max"]}@normal]\n'
                i.protocol.sendLine(combat_stats)
                i.protocol.sendLine(f'@yellowTurn order: {[actor.name for actor in self.order]}@normal')
                
        self.round += 1
        for i in self.order:
            i.status = 'fighting'
        self.next_turn()

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

    def spawn_enemy(self, name):
        _ = Enemy(name, self)

    def inventory_add_item(self, item):
        self.inventory[item.id] = item

    def inventory_remove_item(self, item_id):
        del self.inventory[item_id]

    def new_combat(self):
        if self.combat != None:
            #print('there is combat')
            return 'There is already a fight here!'

        participants = {}
        for i in self.entities.values():
            #print(i)
            if type(i).__name__ == "Player":
                participants[i.name] = i
            if type(i).__name__ == "Enemy":
                participants[i.name] = i

        self.combat = Combat(self, participants)
        
    def move_player(self, player, silent = False):
        #old_room = player.room

        #for p in player.room.entities.values():
        #    if not silent and p != player and isinstance(p, Player):
        #        p.protocol.sendLine(f'{player.pretty_name()} went to {self.name}.')

        #new_room.move_player(self)

        if player in player.room.entities.values():
            del player.room.entities[player.name]
        player.room = self
        self.entities[player.name] = player

        #if not silent:
        #    player.protocol.sendLine(f'You arrived at {self.name}.')

        #    for p in player.room.entities.values():
        #        if p != player and isinstance(p, Player):
        #            p.protocol.sendLine(f'{player.pretty_name()} arrived from {old_room.name}.')

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
                i.protocol.sendLine(f'You explore {i.room.name}')
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
    def __init__(self):
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
        import yaml
        with open('world.yaml', 'r') as file:
            rooms = yaml.safe_load(file)
            for r in rooms['world']:
                room = rooms['world'][r]
                self.rooms[r] = Room(self, r, room['name'], room['description'], room['exits']) 
                if 'enemies' in room:
                    for enemy in room['enemies']:
                        self.rooms[r].spawn_enemy(enemy)

    def save_world(self):
        pass

    def tick(self):
        for i in self.rooms.values():
            i.tick()
        #for i in self.dungeons.values():
        #    i.tick()
