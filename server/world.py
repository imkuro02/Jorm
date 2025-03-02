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
        room_id = self.room.uid
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
        if self.room.world.factory.ticks_passed % 120 == 0:
            self.respawn_all()


class Room:
    def __init__(self, world, uid, name, description, exits, secret_exits, can_be_recall_site, instanced):
        self.world = world
        self.uid = uid
        self.name = name
        self.description = description
        self.exits = exits
        self.secret_exits = secret_exits
        self.can_be_recall_site = can_be_recall_site
        self.instanced = instanced
        self.inventory_manager = InventoryManager(self, limit = 20)
        self.combat = None
        self.entities = {}
        self.spawner = Spawner(self)

    def is_an_instance(self):
        if '/' in self.uid:
            return True
        return False


    def tick(self):
        actors = {}
        if not self.is_an_instance():
            self.spawner.tick()
        for a in self.entities.values():
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
            for i in self.entities.values():
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
        else:
            self.combat.add_participant(player_participant)

    def new_combat(self):
        if self.combat != None:
            return 'There is already a fight here!'

        participants = {}
        npcs_here = False
        players_here = False
        for i in self.entities.values():
            #print(i)
            if type(i).__name__ == "Player":
                participants[i.id] = i
                players_here = True
            if type(i).__name__ == "Enemy":
                participants[i.id] = i
                npcs_here = True

        if players_here and npcs_here:
            self.combat = Combat(self, participants)
        
    def move_entity(self, entity, silent = False):
        if not self.instanced:
            self.remove_entity(entity)
            if not silent and entity.room != self:
                entity.simple_broadcast('',f'{entity.pretty_name()} has left.')

            entity.room = self
            self.entities[entity.id] = entity

            if not silent:
                entity.simple_broadcast('',f'{entity.pretty_name()} has arrived.')
        
        else:
            if type(entity).__name__ != 'Player':
                return
            instanced_room_id = self.uid+'/'+entity.name
            self.world.rooms[instanced_room_id] = Room(self.world, instanced_room_id, self.name, self.description, self.exits, self.secret_exits, self.can_be_recall_site, instanced=False)
            instanced_room = self.world.rooms[instanced_room_id]
       
            #instanced_room.populate()

            self.remove_entity(entity)
            if not silent and entity.room != self:
                entity.simple_broadcast('',f'{entity.pretty_name()} has left.')

            entity.room = instanced_room
            instanced_room.entities[entity.id] = entity

            if not silent:
                entity.simple_broadcast('',f'{entity.pretty_name()} has arrived.')
            

        

    def remove_entity(self, entity):
        if entity.room == None:
            return
        if entity.id not in entity.room.entities:
            return
        del entity.room.entities[entity.id]


    #def move_enemy(self, enemy):
    #    enemy.room = self
    #    self.entities[enemy.id] = enemy
 
        
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
            for x in self.rooms[i].entities:
                if type(self.rooms[i].entities[x]).__name__ != 'Enemy':
                    continue
                if self.rooms[i].entities[x].status != ActorStatusType.NORMAL:
                    continue 
                all_mobs.append(self.rooms[i].entities[x])
        
        boss_mob = random.choice(all_mobs)
        boss_mob.name = '<!>' + boss_mob.name + '<!>'
        boss_mob.simple_broadcast('',
        f'{boss_mob.pretty_name()} is terrorizing {boss_mob.room.name}', worldwide = True)
        for s in boss_mob.stats:
            boss_mob.stats[s] = boss_mob.stats[s] * 2
        boss_mob.stats[StatType.EXP] = boss_mob.stats[StatType.EXP] * 5


    def reload(self):
        print(f'loading rooms t:{self.factory.ticks_passed} s:{int(self.factory.ticks_passed/30)}')
        world = WORLD
        #print('>.', world)
        for r in world['world']:
            room = world['world'][r]
            

            if r in self.rooms:
                players = [entity for entity in self.rooms[r].entities.values() if type(entity).__name__ == "Player"]
                if len(players) >= 1:
                    continue

                # prepare to reload
                for e in self.rooms[r].entities.values():
                    e.room = None
                del self.rooms[r]

            #if room['instanced'] == True:
            self.rooms[r] = Room(self, r, room['name'], room['description'], room['exits'], room['secret_exits'], room['can_be_recall_site'], room['instanced']) 
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
