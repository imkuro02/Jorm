#from actors.enemy import create_enemy
from actors.npcs import create_npc
from actors.player import Player
from items.manager import load_item
from configuration.config import ITEMS, ENEMIES, NPCS
import time
#from items import Item
import uuid
import random
from combat.manager import Combat
from configuration.config import WORLD, StatType, ActorStatusType, ITEMS, Audio, MsgType
import copy
from inventory import InventoryManager

from utils import REFTRACKER
from utils import unload
import utils
import os

class Spawner:
    def __init__(self, room):
        self.room = room
        self.room_dict = self.get_room_dict()

        #self.spawn_points_items = {}
        #self.spawn_points_npcs = {}

        #for i in range(0,len(self.room_dict['items'])):
        #    self.spawn_points_items[i] = None
        #for i in range(0,len(self.room_dict['npcs'])):
        #    self.spawn_points_npcs[i] = None

        self.spawn_points = {}
        for i in range(0,len(self.room_dict['spawner'])):
            self.spawn_points[i] = None

        #utils.debug_print(self.spawn_points_items)
        self.respawn_all()
        REFTRACKER.add_ref(self)

    def get_room_dict(self):
        room_id = self.room.id
        if room_id not in WORLD['world']:
            # remove the username affix on instanced rooms
            room_id = room_id.split('#')[0]

        room = WORLD['world'][room_id]
        return room
    
    def respawn_all(self, forced = True):
        '''
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
        '''
        
        for i in self.spawn_points:
            
            roll = 0
            if not self.room.is_player_present():
                roll = 1 #random.randint(0,100)
            

            if roll != 1 and (self.spawn_points[i] in self.room.actors.values() or self.spawn_points[i] in self.room.inventory_manager.items.values()):
                continue
            else:
                try:
                    #print('unload')
                    s = self.spawn_points[i]
                    self.spawn_points[i] = None
                    
                    s.unload()
                    #self.spawn_points[i] = None
                except Exception as e:
                    pass #utils.debug_print(e)

        #return
        if 'spawner' in self.room_dict:
            for i, _list in enumerate(self.room_dict['spawner']):
                #utils.debug_print(self.spawn_points[i])
                if self.spawn_points[i] != None:
                    continue
                    
                _selected = random.choice(_list)
                
                #utils.debug_print(ENEMIES)
                #utils.debug_print(NPCS[_selected])
                if _selected in ITEMS:
                    item = load_item(_selected)
                    self.room.inventory_manager.add_item(item)
                    self.spawn_points[i] = item
                    continue
                
                if _selected in ENEMIES:
                    #_selected = random.choice(_list)
                    npc = create_npc(self.room,_selected)
                    self.spawn_points[i] = npc
                    '''
                    roll = random.randint(0,100)
                    if roll == 1:
                        npc.simple_broadcast('',f'{npc.name} has spawned', send_to = 'world')
                    continue
                    '''
                    continue

                if _selected in NPCS:
                    #_selected = random.choice(_list)
                    npc = create_npc(self.room,_selected)
                    self.spawn_points[i] = npc
                    continue
                
      


    def tick(self):
        if self.room.world.factory.ticks_passed % (30*120) == 0:
            self.respawn_all()

class Exit:
    def __init__(self, room, direction, to_room_id, blocked = False, secret = False, item_required = None, item_required_consume = False, active_time_of_day = None):
        self.room = room
        self.direction = direction
        self.to_room_id = to_room_id
        self.blocked = blocked
        self.secret = secret
        self.item_required = item_required
        self.item_required_consume = item_required_consume
        self.active_time_of_day = active_time_of_day

    def is_active(self):
        if self.active_time_of_day == None:
            return True
        if self.active_time_of_day not in self.room.world.game_time.TIME_OF_DAY:
            utils.debug_print(self.active_time_of_day, f'not in TIME OF DAY, object: {self.__dict__}')
        return self.room.world.game_time.TIME_OF_DAY[self.active_time_of_day]

    #def get_room_name(self):
    #    if self.to_room_id not in WORLD['world']:
    #        return '-no name-'

    def get_room_obj(self):
        if self.to_room_id not in self.room.world.rooms:
            return None
        return self.room.world.rooms[self.to_room_id]

    def pretty_direction(self):
        direction_name = self.direction.capitalize()
        direction_room_name = self.room.world.rooms[self.to_room_id].pretty_name()
        dir_name_and_room = direction_name #f'"{direction_name}" to {direction_room_name}'
        
        if self.blocked:
            e = self.room.is_enemy_present()
            if e != False:
                return f'{dir_name_and_room}, is blocked by {e.pretty_name()}'

        if self.item_required:
            if self.item_required_consume:
                return f'{dir_name_and_room}, requires one "{ITEMS[self.item_required]["name"]}"'
            else:
                return f'{dir_name_and_room}, requires "{ITEMS[self.item_required]["name"]}"'
        return f'{dir_name_and_room}'


class Room:
    def __init__(self, world, _id, name, description, from_file, exits, can_be_recall_site, doorway, instanced, no_spawner = False):
        self.world = world
        self.id = _id                   # id of the room
        self.name = name                # display name
        self.description = description  # display desc
        self.from_file = from_file      # which file loaded this room
        self.exits = []                 # exits in this room
        self.tick_when_loaded = self.world.factory.ticks_passed
        for _exit in exits:
            #utils.debug_print(_exit)
            if type(_exit).__name__ == 'Exit':
                _exit_dict = {
                    'direction': _exit.direction, 
                    'to_room_id': _exit.to_room_id,
                    'blocked': _exit.blocked, 
                    'secret': _exit.secret,
                    'item_required': _exit.item_required, 
                    'item_required_consume': _exit.item_required_consume,
                    'active_time_of_day': _exit.active_time_of_day, }
            else:
                _exit_dict = {
                    'direction': _exit['direction'], 
                    'to_room_id': _exit['to_room_id'],
                    'blocked': _exit['blocked'], 
                    'secret': _exit['secret'],
                    'item_required': _exit['item_required'], 
                    'item_required_consume': _exit['item_required_consume'], 
                    'active_time_of_day': _exit['active_time_of_day'], }

            self.exits.append(
                                Exit(
                                    room = self,
                                    direction = _exit_dict['direction'],
                                    to_room_id = _exit_dict['to_room_id'],
                                    blocked = _exit_dict['blocked'],
                                    secret = _exit_dict['secret'],
                                    item_required = _exit_dict['item_required'],
                                    item_required_consume = _exit_dict['item_required_consume'],
                                    active_time_of_day = _exit_dict['active_time_of_day']
                                )
                            )
        
        self.can_be_recall_site = can_be_recall_site # whether you can rest now / rest set
        self.instanced = instanced        # is this room a private instance?
        self.doorway = doorway            # whether this room is a doorway, can you see thru it?
        self.inventory_manager = InventoryManager(self, limit = 20)
        self.inventory_manager.can_pick_up_anything = True
        self.combat = None                # placeholder for combat
        self.actors = {}                  # actors in room dict

        self.spawner = None
        if not no_spawner:
            self.spawner = Spawner(self)      # spawner

        REFTRACKER.add_ref(self)

    def get_wall_data(self):
        wall_data = WORLD['world'][self.get_real_id()]['wall_data'].split(':')
        #wall_data_col =  wall_data[0]
        #wall_data_char = wall_data[1]
        #wall_data_prio = wall_data[2]
        return wall_data
    def get_real_id(self):
        #utils.debug_print(self.id)
        if '#' in self.id:
            #utils.debug_print(self.id.split('#')[0])
            return self.id.split('#')[0] 
        return self.id

    def get_active_exits(self):
        active_exits = []
        for i in self.exits:
            if i.is_active():
                active_exits.append(i)
        return active_exits

    def pretty_name(self):
        col = '@yellow'
        if self.is_an_instance():
            col = '@bad'
        if self.can_be_recall_site:
            col = '@good'

        return col+self.name+'@back'

    def is_an_instance(self):
        if '#' in self.id:
            return True
        return False

    def is_enemy_present(self):
        for i in self.actors.values():
            if type(i).__name__ != 'Player':
                return i
        return False

    def is_player_present(self):
        for i in self.actors.values():
            if type(i).__name__ == 'Player':
                return i
        return False 

    def get_description(self):
        desc = self.description
        for i in self.inventory_manager.items.values(): 
            if i.description_room != None:
                desc = desc + f' {i.description_room}.'
        return desc

    def tick(self):
        actors = {}
        if not self.is_an_instance():
            if self.spawner != None:
                self.spawner.tick()
        
        for a in self.actors.values():
            actors[a.id] = a

        for e in actors.values():
            e.tick()

        # remove items that have been on the ground for too long
        items_to_remove = []
        for i in self.inventory_manager.items.values():
            i.tick()
            if self.spawner != None:
                if i in self.spawner.spawn_points.values():
                    continue
            i.time_on_ground += 1
            if i.time_on_ground >= 30*120:
                items_to_remove.append(i)
        for i in items_to_remove:
            self.inventory_manager.remove_item(i)
    

        if self.combat == None:
            return
        self.combat.tick()
        

    def join_combat(self, player_participant):
        if self.combat == None:
            participants = {}
            npcs_here = False
            players_here = False
            for i in self.actors.values():
                #utils.debug_print(i)
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

                #participants[i.id] = i
                if type(i).__name__ == "Enemy":
                    if i.dont_join_fights:
                        continue
                    participants[i.id] = i
                if type(i).__name__ == "Npc":
                    if i.dont_join_fights:
                        continue
                    participants[i.id] = i

            #if players_here and npcs_here:
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
            #utils.debug_print(i)
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
        
    def move_actor(self, actor, silent = False, dont_unload_instanced = False):
        
        self.remove_actor(actor)

        if not silent and actor.room != self:
            if actor.party_manager.party == None:
                actor.simple_broadcast('',f'{actor.pretty_name()} leaves', send_to = 'room_not_party', sound = Audio.walk())
            else:
                actor.simple_broadcast('',f'{actor.pretty_name()} and their party leaves', send_to = 'room_not_party', sound = Audio.walk())


        actor.room = self
        self.actors[actor.id] = actor

        if not self.instanced:
            if not dont_unload_instanced and not self.is_an_instance():
                if type(actor).__name__ == 'Player':
                    for i in actor.instanced_rooms:
                        if i in actor.room.world.rooms:
                            actor.sendLine(f'instanced room: {i} deleted', msg_type = [MsgType.DEBUG])
                            self.world.rooms_to_unload.append(i)

                    actor.instanced_rooms = []
        else:
            
            if type(actor).__name__ == 'Player':
                instanced_room_id = self.id+'#'+actor.name
                if instanced_room_id not in self.world.rooms:
                    self.world.rooms[instanced_room_id] = Room(self.world, instanced_room_id, self.name, self.description, self.from_file, self.exits, self.can_be_recall_site, self.doorway, instanced=False)
                    if type(actor).__name__ == 'Player':
                        actor.instanced_rooms.append(instanced_room_id)
                instanced_room = self.world.rooms[instanced_room_id]
                instanced_room.actors[actor.id] = actor
                del self.actors[actor.id]
                instanced_room = self.world.rooms[instanced_room_id]
                actor.room = instanced_room

        if not silent:
            if actor.party_manager.party == None:
                actor.simple_broadcast('',f'{actor.pretty_name()} arrives', send_to = 'room_not_party', sound = Audio.walk())
            else:
                actor.simple_broadcast('',f'{actor.pretty_name()} and their party arrives', send_to = 'room_not_party', sound = Audio.walk())

    def remove_actor(self, actor):
        if actor.room == None:
            return
        if actor.id not in actor.room.actors:
            return
        if actor.room.combat != None:
            if actor in actor.room.combat.participants.values():
                del actor.room.combat.participants[actor.id]
        del actor.room.actors[actor.id]

class GameTime:
    def __init__(self, factory, game_date_time = 0):
        self.factory = factory
        self.TICKS_PER_SECOND = 30
        self.SECONDS_PER_TICK = 2  # game seconds per tick
        self.SECONDS_PER_MINUTE = 60
        self.MINUTES_PER_HOUR = 60
        self.HOURS_PER_DAY = 24
        self.DAYS_PER_WEEK = 7
        self.WEEKS_PER_MONTH = 4
        self.MONTHS_PER_YEAR = 12
        self.DAYS_PER_MONTH = self.DAYS_PER_WEEK * self.WEEKS_PER_MONTH  # 28
        self.DAYS_PER_YEAR = self.DAYS_PER_MONTH * self.MONTHS_PER_YEAR  # 336
        
        self.game_date_time = game_date_time

        self.WEEKDAYS = ["Moonsday", "Twosday", "Wakesday", "Thornsday", "Firesday", "Starsday", "Endsday"]
        self.MONTHS = [
            "Suncall", "Moondrift", "Stormreach", "Frostwane",
            "Blossomveil", "Flamehollow", "Duskwind", "Brightshade",
            "Hollowfall", "Dawnspire", "Gloomtide", "Starcrest"
        ]

        
        self.TIME_OF_DAY = {
            'morning' :         False,
            'noon':             False,
            'evening':          False,
            'night':            False,
            'not_morning' :     False,
            'not_noon':         False,
            'not_evening':      False,
            'not_night':        False,
            'hour_even':        False,
            'hour_uneven':      False,

        }

        self.load_game_time()

    def load_game_time(self):
        filename = "gametime.txt"
        if not os.path.exists(filename):
            # File doesn't exist — create it and write 420
            with open(filename, "w") as f:
                f.write(f"{self.game_date_time}")
            value = self.game_date_time
        else:
            # File exists — read the integer inside
            with open(filename, "r") as f:
                self.game_date_time = int(f.read().strip())

        utils.debug_print("Game Time:", self.game_date_time)

    def save_game_time(self):
        filename = "gametime.txt"
        with open(filename, "w") as f:
            f.write(f"{self.game_date_time}")

    def time_of_day_trigger(self):
        time_dict = self.get_game_time()

        self.TIME_OF_DAY['morning'] =           time_dict['hour'] >= 5 and time_dict['hour'] <= 10
        self.TIME_OF_DAY['noon'] =               time_dict['hour'] >= 10 and time_dict['hour'] <= 16
        self.TIME_OF_DAY['evening'] =         time_dict['hour'] >= 17 and time_dict['hour'] <= 20
        self.TIME_OF_DAY['night'] =             time_dict['hour'] >= 21 or time_dict['hour'] <= 4
        self.TIME_OF_DAY['not_morning'] =       not self.TIME_OF_DAY['morning']
        self.TIME_OF_DAY['not_noon'] =           not self.TIME_OF_DAY['noon']
        self.TIME_OF_DAY['not_evening'] =     not self.TIME_OF_DAY['evening']
        self.TIME_OF_DAY['not_night'] =         not self.TIME_OF_DAY['night']
        self.TIME_OF_DAY['hour_even'] =         time_dict['hour'] % 2 == 0
        self.TIME_OF_DAY['hour_uneven'] =       time_dict['hour'] % 2 != 0


    def tick(self):
        self.game_date_time += 1
        self.time_of_day_trigger()

    def set_game_time(self, line):
        try:
            time = int(line)
            self.game_date_time = time
        except Exception as e:
            self.sendLine(f'Cant set time: {e}')

    def get_game_time_compact_str(self):
        _time = self.get_game_time()
        time = f"{_time['second']:02}.{_time['minute']:02}.{_time['hour']:02}.{_time['day']:02}.{_time['month']:02}.{_time['year']:04}"
        return time
    
    def get_game_time_int(self):
        return self.game_date_time

    def get_game_time(self):
        total_game_seconds = self.game_date_time * self.SECONDS_PER_TICK

        total_minutes = total_game_seconds // 60
        seconds = total_game_seconds % 60

        total_hours = total_minutes // 60
        minutes = total_minutes % 60

        total_days = total_hours // 24
        hours = total_hours % 24

        year = total_days // self.DAYS_PER_YEAR + 1
        day_of_year = total_days % self.DAYS_PER_YEAR

        month_index = day_of_year // self.DAYS_PER_MONTH
        day_of_month = day_of_year % self.DAYS_PER_MONTH + 1

        weekday_index = total_days % self.DAYS_PER_WEEK

        return {
            "day_name": self.WEEKDAYS[weekday_index],
            "month_name": self.MONTHS[month_index],
            "year": year,
            
            "day": day_of_month,
            "month": month_index,
            "hour": int(hours),
            "minute": int(minutes),
            "second": int(seconds)
        }

class World:
    def __init__(self, factory):
        self.factory = factory
        self.rooms = {}
        self.rooms_to_unload = []
        self.game_time = GameTime(self.factory)
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
        f'{boss_mob.pretty_name()} is terrorizing {boss_mob.room.name}', send_to = 'world')
        for s in boss_mob.stat_manager.stats:
            boss_mob.stat_manager.stats[s] = boss_mob.stat_manager.stats[s] * 2
        boss_mob.stat_manager.stats[StatType.EXP] = boss_mob.stat_manager.stats[StatType.EXP] * 5

    def reload(self):
        utils.debug_print(f'loading rooms t:{self.factory.ticks_passed} s:{int(self.factory.ticks_passed/30)}')
        to_del = []
        for r in self.rooms:
            players = [actor for actor in self.rooms[r].actors.values() if type(actor).__name__ == "Player"]
            if len(players) >= 1:
                continue
            utils.debug_print('del room: ', self.rooms[r].id)
            to_del.append(r)

        for d in to_del:
            del self.rooms[d]

        world = WORLD

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

            self.rooms[r] = Room(self, r, 
            room['name'], room['description'], 
            room['from_file'], room['exits'], 
            room['can_be_recall_site'], room['doorway'],
            room['instanced']) 

    def save_world(self):
        pass

    def tick(self):
        self.game_time.tick() 
        for i in self.rooms_to_unload:
            to_kick_from_instance = [] 
            for x in self.rooms[i].actors.values():
                to_kick_from_instance.append(x)
            for x in to_kick_from_instance:
                if type(x).__name__ == 'Player':
                    x.party_manager.party_leave()
                    

            for x in self.rooms[i].inventory_manager.items.values():
                unload(x)
            unload(self.rooms[i].inventory_manager.triggerable_manager)

            to_unload = []
            for x in self.rooms[i].actors.values():
                to_unload.append(x)
            for x in to_unload:
                #x.die()
                x.unload()

            #self.rooms[i].actors = {}

            to_unload = []
            for x in self.rooms[i].exits:
                to_unload.append(x)
            for x in to_unload:
                unload(x)

            to_unload = []
            for x in self.rooms[i].__dict__:
                to_unload.append(x)
            for x in to_unload:
                unload(x)
                
            #utils.debug_print(self.rooms[i])
            unload(self.rooms[i])
            #utils.debug_print(self.rooms[i])
            del self.rooms[i]
            
        self.rooms_to_unload = []

        rooms = []
        for i in self.rooms:
            rooms.append(self.rooms[i])
        for i in rooms:
            ##if i.name.lower() == 'South-west corner'.lower():
            #    utils.debug_print(i.id)
            #    for x in i.actors.values():
            #        utils.debug_print('>', x.name)
            i.tick()
            

        utils.unload_fr()

from actors import ai
ai.Room = Room
ai.Exit = Exit