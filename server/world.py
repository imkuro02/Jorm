from actors.npcs import create_enemy
from actors.player import Player
import time
#from items import Item
import uuid
import random
from combat.manager import Combat
from configuration.config import WORLD
import copy
from inventory import InventoryManager

class Room:
    def __init__(self, world, uid, name, description, exits, secret_exits, can_be_recall_site):
        self.world = world
        self.uid = uid
        self.name = name
        self.description = description
        self.exits = exits
        self.secret_exits = secret_exits
        self.can_be_recall_site = can_be_recall_site
        
        self.inventory_manager = InventoryManager(self, limit = 20)
        
        self.combat = None

        self.entities = {}


    def next(self):
        return

    def tick(self):
        for e in self.entities.values():
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
                            else:
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
        
    def move_player(self, player, silent = False, instanced = False):
        #if player.room != None:
        if player in player.room.entities.values():
            self.remove_player(player)
        player.room = self
        self.entities[player.id] = player
        if not silent:
            player.command_look('')

        if player.recall_site == 'tutorial' and self.can_be_recall_site:
            player.command_rest('set')

    def remove_player(self, player):
        del player.room.entities[player.id]

    def move_enemy(self, enemy):
        enemy.room = self
        self.entities[enemy.id] = enemy
 
class InstancedRoom(Room):

    def move_player(self, player, silent = False, instanced = False):
        if not instanced:
            instanced_room_id = self.uid+'/'+player.name
            self.world.rooms[instanced_room_id] = Room(self.world, instanced_room_id, self.name, self.description, self.exits)
            
            room_template = WORLD['world'][self.uid]

            if 'enemies' in room_template:
                for enemy_id in room_template['enemies']:
                    create_enemy(self.world.rooms[instanced_room_id], enemy_id)

            self.world.rooms[instanced_room_id].move_player(player, instanced = True)

        else:
            super().move_player(player)
        
class World:
    def __init__(self, factory):
        self.factory = factory
        
        self.rooms = {}
        '''
        world = WORLD
        for r in world['world']:
            room = world['world'][r]
            if 'instanced' in room:
                self.rooms[r] = InstancedRoom(self, r, room['name'], room['description'], room['exits']) 
            else:
                self.rooms[r] = Room(self, r, room['name'], room['description'], room['exits']) 

            if 'enemies' in room:
                for enemy in room['enemies']:
                    #self.rooms[r].spawn_enemy(enemy)
                    create_enemy(self.rooms[r], enemy)
                    #print(r, enemy)
        '''

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
                else:
                    for e in self.rooms[r].entities.values():
                        e.room = None
                    del self.rooms[r]

            if 'instanced' in room:
                self.rooms[r] = InstancedRoom(self, r, room['name'], room['description'], room['exits'], room['secret_exits'], room['can_be_recall_site']) 
            else:
                self.rooms[r] = Room(self, r, room['name'], room['description'], room['exits'], room['secret_exits'], room['can_be_recall_site']) 

            if 'enemies' in room:
                for enemy in room['enemies']:
                    #self.rooms[r].spawn_enemy(enemy)
                    create_enemy(self.rooms[r], enemy)
                    #print(r, enemy)



    def save_world(self):
        pass

    def tick(self):
        if self.factory.ticks_passed % (30*30) == 0 or self.factory.ticks_passed == 1:
            self.reload()
        for i in self.rooms.values():
            i.tick()
