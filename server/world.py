from actors.enemy import create_enemy
from actors.npcs import create_npc
from actors.player import Player
from items.manager import load_item
import time
#from items import Item
import uuid
import random
from combat.manager import Combat
from configuration.config import WORLD, StatType, ActorStatusType
import copy
from inventory import InventoryManager

class Spawner:
    def __init__(self, room):
        self.room = room
        self.room_dict = self.get_room_dict()
        

        self.spawn_points_enemies = {}
        self.spawn_points_items = {}
        self.spawn_points_npcs = {}

        

        for i in range(0,len(self.room_dict['enemies'])):
            self.spawn_points_enemies[i] = None
        for i in range(0,len(self.room_dict['items'])):
            self.spawn_points_items[i] = None
        for i in range(0,len(self.room_dict['npcs'])):
            self.spawn_points_npcs[i] = None

        #print(self.spawn_points_items)
        self.respawn_all()

    def get_room_dict(self):
        room_id = self.room.id
        if room_id not in WORLD['world']:
            # remove the username affix on instanced rooms
            room_id = room_id.split('/')[0]

        room = WORLD['world'][room_id]
        return room
    
    def respawn_all(self, forced = True):
        for i in self.spawn_points_enemies:
            if self.spawn_points_enemies[i] == None:
                continue
            if self.spawn_points_enemies[i].room == None:
                self.spawn_points_enemies[i] = None

        for i in self.spawn_points_items:
            if self.spawn_points_items[i] == None:
                continue
            if self.spawn_points_items[i] not in self.room.inventory_manager.items.values():
                self.spawn_points_items[i] = None      

        for i in self.spawn_points_npcs:
            if self.spawn_points_npcs[i] == None:
                continue
            if self.spawn_points_npcs[i].room == None:
                self.spawn_points_npcs[i] = None      

        if 'enemies' in self.room_dict:
            for i, _list in enumerate(self.room_dict['enemies']):
                if self.spawn_points_enemies[i] != None:
                    continue
                _selected = random.choice(_list)
                enemy = create_enemy(self.room, _selected)
                self.spawn_points_enemies[i] = enemy
                
        if 'items' in self.room_dict:
            for i, _list in enumerate(self.room_dict['items']):
                if self.spawn_points_items[i] != None:
                    continue
                _selected = random.choice(_list)
                item = load_item(_selected)
                self.room.inventory_manager.add_item(item)
                self.spawn_points_items[i] = item
                
        if 'npcs' in self.room_dict:
            for i, _list in enumerate(self.room_dict['npcs']):
                if self.spawn_points_npcs[i] != None:
                    continue
                _selected = random.choice(_list)
                npc = create_npc(self.room,_selected)
                self.spawn_points_npcs[i] = npc


    def tick(self):
        if self.room.world.factory.ticks_passed % (30*120) == 0:
            self.respawn_all()

class Exit:
    def __init__(self, direction = 'north', room_obj = None):
        self.direction = direction
        self.room_obj = room_obj
        self.is_secret = False
        self.is_blocked = False

class Room:
    def __init__(self, world, _id):
        self.world =            world
        self.id =               _id
        self.name =             'No Room Name'
        self.description =      'No Room Desc'

        self.exits = []
        self.can_be_recall_site = False

        self.inventory_manager = InventoryManager(self, limit = 20)
        self.combat = None
        self.actors = {}
        #self.spawner = Spawner(self)

    def is_an_instance(self):
        if '/' in self.id:
            return True
        return False

    def is_enemy_present(self):
        for i in self.actors.values():
            if type(i).__name__ == 'Enemy':
                return i
        return False


    def tick(self):
        actors = {}
        if not self.is_an_instance():
            pass
            #self.spawner.tick()
        for a in self.actors.values():
            actors[a.id] = a

        for e in actors.values():
            e.tick()

        if self.combat == None:
            return
        self.combat.tick()
        

    def join_combat(self, player_participant):
        if self.combat == None:
            participants = {}
            npcs_here = False
            players_here = False
            for i in self.actors.values():
                #print(i)
                if i == player_participant:
                    participants[i.id] = i
                    players_here = True

                    ### PARTY CODE - invite entire party to the fight
                    if player_participant.party_manager.party != None:
                        for par in player_participant.party_manager.party.participants.values():
                            if par == player_participant:
                                continue
                            if par.room != self:
                                continue
                            participants[par.id] = par
                            players_here = True
                    ### PARTY CODE

                if type(i).__name__ == "Enemy":
                    participants[i.id] = i
                    npcs_here = True

            if players_here and npcs_here:
                self.combat = Combat(self, participants)
                self.combat.initiative()
        else:
            self.combat.add_participant(player_participant)

    def new_combat(self):
        if self.combat != None:
            return 'There is already a fight here!'

        participants = {}
        npcs_here = False
        players_here = False
        for i in self.actors.values():
            #print(i)
            if type(i).__name__ == "Player":
                participants[i.id] = i
                players_here = True
            if type(i).__name__ == "Enemy":
                participants[i.id] = i
                npcs_here = True

        if players_here and npcs_here:
            self.combat = Combat(self, participants)
        
    def move_actor(self, actor, silent = False):
        if not self.is_an_instance():
            self.remove_actor(actor)
            if not silent and actor.room != self:
                actor.simple_broadcast('',f'{actor.pretty_name()} has left.')

            actor.room = self
            self.actors[actor.id] = actor

            if not silent:
                actor.simple_broadcast('',f'{actor.pretty_name()} has arrived.')
        
        else:
            if type(actor).__name__ != 'Player':
                return
            instanced_room_id = self.id+'/'+actor.name
            self.world.rooms[instanced_room_id] = Room(self.world, instanced_room_id, self.name, self.description, self.exits, self.blocked_exits, self.secret_exits, self.can_be_recall_site, instanced=False)
            instanced_room = self.world.rooms[instanced_room_id]
       
            #instanced_room.populate()

            self.remove_actor(actor)
            if not silent and actor.room != self:
                actor.simple_broadcast('',f'{actor.pretty_name()} has left.')

            actor.room = instanced_room
            instanced_room.actors[actor.id] = actor

            if not silent:
                actor.simple_broadcast('',f'{actor.pretty_name()} has arrived.')

    def remove_actor(self, actor):
        if actor.room == None:
            return
        if actor.id not in actor.room.actors:
            return
        del actor.room.actors[actor.id]

 
        
class World:
    def __init__(self, factory):
        self.factory = factory
        self.rooms = {}
        self.rooms = {
            '0': Room(self, '0'),
            '1': Room(self, '1')
        }
        ex = Exit(direction = 'north', room_obj = self.rooms['1'])
        self.rooms['0'].exits.append(ex)
        #self.reload()

    
    def edit_new_room(self, room, direction):
        room_id = str(len(self.rooms))
        self.rooms[room_id] = Room(self, room_id)
        _exit = Exit(direction, self.rooms[room_id])
        room.exits.append(_exit)
        return f'new exit {_exit.direction} -> {room_id}'
    
    def edit_room_new_exit(self, room, direction, other_room_id):
        if other_room_id not in self.rooms:
            return 'No room with that ID'

        _exit = Exit(direction, self.rooms[other_room_id])
        room.exits.append(_exit)

        return f'new exit {_exit.direction} -> {other_room_id}'

    def edit_del_room(self, room_id):
        if room_id not in self.rooms:
            return 'No room with that ID'

        if room_id == '0':
            return 'Cannot delete room 0'

        to_move = []
        for actor in self.rooms[room_id].actors.values():
            to_move.append(actor)
        for actor in to_move:
            self.rooms['0'].move_actor(actor)

        for room in self.rooms.values():
            to_del = []
            for _exit in room.exits:
                if _exit.room_obj == self.rooms[room_id]:
                    to_del.append(_exit)
            for d in to_del:
                room.exits.remove(d)

        del self.rooms[room_id]
        return 'Deleted'

    def edit_del_exit(self, room, direction):
        to_del = []
        for _exit in room.exits:
            if _exit.direction == direction:
                to_del.append(_exit)
        if to_del == []:
            return 'No exit deleted'
        for d in to_del:
            room.exits.remove(d)
        return 'Deleted'

    def edit_goto_room(self, user, room_id):
        if room_id not in self.rooms:
            return 'No room with that ID'
        self.rooms[room_id].move_actor(user)
        return f'You are in {room_id}'

    def edit_name_room(self, room, name):
        room.name = name
        return 'Name set'

    def edit_desc_room(self, room, desc):
        room.description = desc
        return 'Desc set'

    def edit_rest_room(self, room):
        room.can_be_recall_site = not room.can_be_recall_site
        return f'can be recall site set to {room.can_be_recall_site}'

    
                

    def reload(self):
        print(f'loading rooms t:{self.factory.ticks_passed} s:{int(self.factory.ticks_passed/30)}')
        world = WORLD
        #print('>.', world)
        for r in world['world']:
            room = world['world'][r]
            

            if r in self.rooms:
                players = [actor for actor in self.rooms[r].actors.values() if type(actor).__name__ == "Player"]
                if len(players) >= 1:
                    continue

                # prepare to reload
                for e in self.rooms[r].actors.values():
                    e.room = None
                del self.rooms[r]

            self.rooms[r] = Room(self, r, room['name'], room['description'], room['exits'], room['blocked_exits'], room['secret_exits'], room['can_be_recall_site'], room['instanced']) 

    def save_world(self):
        pass

    def tick(self):
        for i in self.rooms.values():
            i.tick()
