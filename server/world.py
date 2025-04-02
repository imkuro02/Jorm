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

        self.spawn_points_items = {}
        self.spawn_points_npcs = {}

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
    def __init__(self, room, direction, to_room_id, blocked = False, secret = False):
        self.room = room
        self.direction = direction
        self.to_room_id = to_room_id
        self.blocked = blocked
        self.secret = secret

    #def get_room_name(self):
    #    if self.to_room_id not in WORLD['world']:
    #        return '-no name-'

    def get_room_obj(self):
        if self.to_room_id not in self.room.world.rooms:
            return None
        return self.room.world.rooms[self.to_room_id]

    def pretty_direction(self):
        if self.blocked:
            return f'[{self.direction}]'
        return self.direction


class Room:
    def __init__(self, world, _id, name, description, exits, can_be_recall_site, instanced):
        self.world = world
        self.id = _id
        self.name = name
        self.description = description

        self.exits = []
        for _exit in exits:
            print(_exit)
            if type(_exit).__name__ == 'Exit':
                self.exits.append(_exit)
                continue

            _exit_dict = {
                'direction': _exit['direction'], 
                'to_room_id': _exit['to_room_id'],
                'blocked': _exit['blocked'], 
                'secret': _exit['secret']}

            self.exits.append(
                                Exit(
                                    room = self,
                                    direction = _exit_dict['direction'],
                                    to_room_id = _exit_dict['to_room_id'],
                                    blocked = _exit_dict['blocked'],
                                    secret = _exit_dict['secret']
                                )
                            )
        
        self.can_be_recall_site = can_be_recall_site
        self.instanced = instanced
        self.inventory_manager = InventoryManager(self, limit = 20)
        self.combat = None
        self.actors = {}
        self.spawner = Spawner(self)

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
            self.spawner.tick()
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

                if type(i).__name__ == "Npc":
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
            if type(i).__name__ == "Npc":
                participants[i.id] = i
                npcs_here = True

        if players_here and npcs_here:
            self.combat = Combat(self, participants)
        
    def move_actor(self, actor, silent = False):
        if not self.instanced:
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
            self.world.rooms[instanced_room_id] = Room(self.world, instanced_room_id, self.name, self.description, self.exits, self.can_be_recall_site, instanced=False)
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


    #def move_enemy(self, enemy):
    #    enemy.room = self
    #    self.actors[enemy.id] = enemy
 
        
class World:
    def __init__(self, factory):
        self.factory = factory
        self.rooms = {}
        self.reload()

    def spawn_boss(self):
        all_mobs = []
        for i in self.rooms:
            if self.rooms[i].instanced: 
                continue
            for x in self.rooms[i].actors:
                if type(self.rooms[i].actors[x]).__name__ != 'Enemy':
                    continue
                if self.rooms[i].actors[x].status != ActorStatusType.NORMAL:
                    continue 
                all_mobs.append(self.rooms[i].actors[x])
        
        boss_mob = random.choice(all_mobs)
        boss_mob.name = '<!>' + boss_mob.name + '<!>'
        boss_mob.simple_broadcast('',
        f'{boss_mob.pretty_name()} is terrorizing {boss_mob.room.name}', worldwide = True)
        for s in boss_mob.stat_manager.stats:
            boss_mob.stat_manager.stats[s] = boss_mob.stat_manager.stats[s] * 2
        boss_mob.stat_manager.stats[StatType.EXP] = boss_mob.stat_manager.stats[StatType.EXP] * 5


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

            #if room['instanced'] == True:
            #print(room['exits'])
            self.rooms[r] = Room(self, r, room['name'], room['description'], room['exits'], room['can_be_recall_site'], room['instanced']) 
            #else:
            #    self.rooms[r] = Room(self, r, room['name'], room['description'], room['exits'], room['secret_exits'], room['can_be_recall_site']) 
            #self.rooms[r].populate()
            



    def save_world(self):
        pass

    def tick(self):
        #if self.factory.ticks_passed % (30*(60*1)) == 0 or self.factory.ticks_passed == 3:
        #    self.reload()
            #self.spawn_boss()
            
        #if self.factory.ticks_passed % (30*(60*10)) == 0 or self.factory.ticks_passed == 1:
        #    for i in self.rooms.values():
        #        i.respawn_enemies()
        for i in self.rooms.values():
            i.tick()
