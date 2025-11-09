from actors.actor import Actor
import utils
from trade import TradeManager
# import commands maps
from actors.player_only_functions.commands import one_letter_commands, commands, shortcuts_to_commands, translations
# import the commands module so all functions can be imported and assigned to player class
import actors.player_only_functions.commands 
from configuration.config import StatType, MsgType, ActorStatusType, Color
import time
from actors.player_only_functions.settings import Settings
#from actors.enemy_ai import AIBasic
from actors.ai import PlayerAI, EnemyAI
from actors.player_only_functions.charging_mini_game import ChargingMiniGame


import gc
from utils import unload

class FriendManager:
    def __init__(self, owner):
        self.owner = owner
        self.friends = []

    def find_actor_id_from_actor_name(self, username):
        return self.owner.room.world.factory.db.find_actor_id_from_actor_name(username)

    def find_actor_name_from_actor_id(self, _id):
        return self.owner.room.world.factory.db.find_actor_name_from_actor_id(_id)
        
    def friend_add(self, friend_to_add_username, silent = False):
        found = self.find_actor_id_from_actor_name(friend_to_add_username)
        if found == None:
            self.owner.sendLine('Cannot add friend, they do not exist')
            return
        if found[0] in self.friends:
            self.owner.sendLine('Cannot add friend, already befriended')
            return
        if found[0] == self.owner.id:
            self.owner.sendLine('Cannot add friend, kinda sad you tried')
            return
        self.owner.sendLine(f'{str(found[1])} added as your friend!')
        self.friends.append(found[0])

    def friend_remove(self, friend_to_remove_username, silent = False):
        found = self.find_actor_id_from_actor_name(friend_to_remove_username) 
        if found != None:
            if found[0] in self.friends:
                self.friends.remove(found[0])
                self.owner.sendLine('removed 1 friend')
            else:
                self.owner.sendLine('Cannot remove friend, either they are not your friend or do not exist')

    def friend_list(self):
        self.owner.sendLine('Friend list:')
        accs = []
        t = utils.Table(2,3)
        t.add_data('Name')
        t.add_data('Status')
        online = False
        is_friend = True
        for i in self.friends:
            name = str(self.find_actor_name_from_actor_id(i)[1])
            
            online = False
            for prot in self.owner.room.world.factory.protocols:
                if prot.actor == None:
                    continue
                if prot.actor.id == i:
                    online = True
                    name = prot.actor.name
                    if self.owner.id not in prot.actor.friend_manager.friends:
                        is_friend = False
                    

            col = Color.BAD
            status = 'Unknown'
            if online:
                col = Color.GOOD
            if online:
                status = 'Online'
            else:
                status = 'Offline'

            if is_friend == False:
                status = 'Not Friend'
                col = Color.BAD

            t.add_data(name)
            t.add_data(f'{status}',col)

        output = t.get_table()
        self.owner.sendLine(output)


            
            

    def friend_broadcast_login(self):
        for prot in self.owner.room.world.factory.protocols:
            if prot.actor == None:
                continue
            if prot.actor.id in self.friends:
                if self.owner.id in prot.actor.friend_manager.friends:
                    prot.actor.sendLine(f'Your friend {self.owner.pretty_name()} has logged in', msg_type = [MsgType.GOSSIP])

    def friend_broadcast_logout(self):
        for prot in self.owner.room.world.factory.protocols:
            if prot.actor == None:
                continue
            if prot.actor.id in self.friends:
                if self.owner.id in prot.actor.friend_manager.friends:
                    prot.actor.sendLine(f'Your friend {self.owner.pretty_name()} has logged out', msg_type = [MsgType.GOSSIP])

    def friend_broadcast(self, line):
        self.owner.sendLine(f'You gossip "@important{line}@normal"', msg_type = [MsgType.CHAT, MsgType.GOSSIP])
        for prot in self.owner.room.world.factory.protocols:
            if prot.actor == None:
                continue
            if prot.actor.id in self.friends:
                if self.owner.id in prot.actor.friend_manager.friends:
                    prot.actor.sendLine(f'{self.owner.pretty_name()} gossips "@important{line}@normal"', msg_type = [MsgType.CHAT, MsgType.GOSSIP])

class UpdateChecker:
    def __init__(self,actor):
        self.actor = actor
        self.protocol = actor.protocol

        self.last_room = None
        self.last_grid = None

    

    def tick_show_actors(self):
        if not self.actor.factory.ticks_passed % 30/10 == 0:
            return
        
        output = 'Entities:\n'
        _list = self.actor.room.actors.values()

        for par in _list:
            if par == self.actor: 
                continue
            output = output + par.pretty_name()+'\n'+par.prompt(self)+'\n'
        
        
        output = output[:-1] if output.endswith("\n") else output
        #output = output + self.actor.get_affects(self.actor)
        output = utils.add_color(output)
        #output = {"actors":output}
        
        self.actor.protocol.send_gmcp(output, 'Actors')


    def tick_show_map(self):
        split = ','

        

        #if self.last_room == self.actor.room:
        #    return

        self.last_room = self.actor.room
        offsets = {
            'north': [ 0  ,  -1 , 0],
            'west':  [ -1 ,  0 , 0],
            'south': [ 0  , 1 , 0],
            'east':  [ 1  ,  0 , 0],
            'up':    [0,0,1],
            'down':  [0,0,-1]
        }
        room_id = self.actor.room.id
        VIEW_RANGE = 7
        START_LOC = f'{0}{split}{0}{split}{0}'
        start_room = self.protocol.factory.world.rooms[room_id]
        grid = {}
        grid[START_LOC] = room_id

        for _exit in start_room.exits:
            if _exit.direction not in offsets:
                continue
            if _exit.secret:
                continue
            if _exit.item_required != None:
                continue
            if _exit.to_room_id in grid.values():
                continue

            x = 0
            y = 0
            z = 0
            x += offsets[_exit.direction][0] #+ VIEW_RANGE
            y += offsets[_exit.direction][1] #+ VIEW_RANGE
            z += offsets[_exit.direction][2] 
            _loc = f'{x}{split}{y}{split}{z}'

            
            
            if _loc not in grid:
                grid[_loc] = _exit.to_room_id
            



        _grid = {}
        for r in grid:
            _grid[r] = grid[r]
            
        for r in range(0,VIEW_RANGE*1):
            for room_loc in _grid:

                room = self.protocol.factory.world.rooms[grid[room_loc]]
                
                if room.doorway:
                    continue

                _x = int(room_loc.split(f'{split}')[0])
                _y = int(room_loc.split(f'{split}')[1])
                _z = int(room_loc.split(f'{split}')[2])

                for _exit in room.exits:
                    if _exit.direction not in offsets:
                        continue
                    if _exit.secret:
                        continue
                    
    
                    x = _x + offsets[_exit.direction][0] 
                    y = _y + offsets[_exit.direction][1] 
                    z = _z + offsets[_exit.direction][2] 
                    _loc = f'{x}{split}{y}{split}{z}'

                    if _exit.to_room_id in grid.values():
                        continue
            

                    if _loc not in grid:
                        grid[_loc] = _exit.to_room_id

            _grid = {}
            for r in grid:
                _grid[r] = grid[r]

        for r in _grid:
            room = self.actor.room.world.rooms[_grid[r]]
            exits = []
            for e in room.exits:
                if e.secret:
                    continue
                exits.append({'direction':e.direction})
            
            quest_not_started = False
            quest_turn_in = False

            for actor in room.actors.values():
                important_dialog_dict = actor.get_important_dialog(actor_to_compare = self.actor, return_dict = True)
                if important_dialog_dict == False:
                    continue
                if important_dialog_dict['quest_not_started']:
                    quest_not_started = True
                if important_dialog_dict['quest_turn_in']:
                    quest_turn_in = True

            _grid[r] = {
                'id': room.id, 
                'name': room.name, 
                'exits': exits, 
                'doorway': int(room.doorway), 
                'quest_not_started': int(quest_not_started),
                'quest_turn_in': int(quest_turn_in)
                }


        #utils.debug_print(_grid)
        if self.last_grid == _grid:
            return
        self.last_grid = _grid
        #self.actor.sendLine(str(_grid))
        self.protocol.send_gmcp(_grid,'Map')

    def tick_send_time(self):
        time = self.actor.room.world.game_time.get_game_time()
        self.actor.protocol.send_gmcp({'hour':time['hour'],'minute':time['minute']}, 'Time')

    def tick(self):
        
        #return
        #if self.actor.factory.ticks_passed % 30 != 0:
        #    return
        #self.tick_show_actors()
        _look = self.actor.command_look('', return_gmcp = True)
        _map = self.actor.command_map('',   return_gmcp = True) 
        self.actor.protocol.send_gmcp(utils.add_color(_map), 'MAP')
        self.actor.protocol.send_gmcp(utils.add_color(_look), 'LOOK_ROOM')
        
        #self.tick_show_map()
        self.tick_send_time()
        
class Player(Actor):
    def __init__(self, protocol, name, room, _id = None):
        self.loaded = False
        self.protocol = protocol
        self.admin = 0
        self.queued_lines = []
        self.msg_history = {}
        self.recently_send_message_count = 0
        self.instanced_rooms = []
        self.collect_lost_exp_rooms = {}
        
        
        super().__init__(name = name, room = room, _id = _id)

        self.last_line_sent = None
        #self.last_line_received = None
        self.last_command_used = None

        self.check_if_admin()

        self.recall_site = 'tutorial#tutorial'
        self.trade_manager = TradeManager(self)
        self.current_dialog = None

        # meta data
        self.date_of_creation = utils.get_unix_timestamp()
        self.date_of_last_login_previous = utils.get_unix_timestamp()
        self.date_of_last_login = utils.get_unix_timestamp()
        self.time_in_game = 0
        self.explored_rooms = []
        
        
        self.settings_manager = Settings(self)
        self.ai = PlayerAI(self)

        self.charging_mini_game = ChargingMiniGame(self)

        self.update_checker = UpdateChecker(self)
        self.friend_manager = FriendManager(self)
        self.loaded = True
        
    def die(self, unload = False):
        super().die(unload = False)
        lost_exp = int(self.stat_manager.stats[StatType.EXP]*0.025)
        self.collect_lost_exp_rooms[self.room.id] = lost_exp
        self.gain_exp(-lost_exp)
        
        

    def unload(self):
        self.loaded = False
        self.status = ActorStatusType.NORMAL
        self.affect_manager.unload_all_affects(silent = True)
        self.trade_manager.trade_stop()
        self.party_manager.party_leave()
        
       
        super().unload()
        


    def check_if_admin(self):
        if self.protocol == None:
            return
        
        admins = self.protocol.factory.db.read_admins(self)
        
        if admins == None:
            self.admin = 0
        else:
            self.admin = admins[1]

        self.inventory_manager.can_pick_up_anything = self.admin >= 1
        
    def set_admin(self, admin_level):
        self.admin = admin_level

    #def get_character_sheet(self):
    #    output = super().get_character_sheet()
    #    return output

    def tick(self):
        if not self.loaded:
            return
            
        super().tick()

        # regain lost exp
        if self.status != ActorStatusType.DEAD:
            if self.room.id in self.collect_lost_exp_rooms:
                self.gain_exp(self.collect_lost_exp_rooms[self.room.id])
                del self.collect_lost_exp_rooms[self.room.id]

        #if self.settings_manager.autobattler:
        if self.ai != None:
            self.ai.tick()

        if self.charging_mini_game != None:
            self.charging_mini_game.tick()

        if self.recently_send_message_count > 0:
            self.recently_send_message_count -= 1

        if len(self.queued_lines) >= 1:
            to_handle = self.queued_lines[0]
            self.queued_lines.pop(0)
            self.handle(to_handle)
            
                
        if self.update_checker != None:
            if self.factory.ticks_passed % 30 == 0:
                self.update_checker.tick()
    
    
    def sendSound(self, sfx):
        self.protocol.send_gmcp({'name':sfx}, 'Client.Media.Play')

    def sendLine(self, line, color = True, sound = None, msg_type = None):

       
        #if self.last_line_received == line:
        #   return
        
        #self.last_line_received = line
        if msg_type != None:
            _msg_type = msg_type
            msg_type = ' '.join(_msg_type)
            self.msg_history[len(self.msg_history)] = {'type':msg_type, 'line':line}

        if self.settings_manager.debug == False and msg_type == MsgType.DEBUG:
            return

        if sound != None:
            self.sendSound(sound)
            
        

        if color:
            #start = time.time()
            
            # this line is responsible for making the length of text 28 chars or smth
            line = utils.add_line_breaks(line)
            
            
            
            #utils.debug_print((time.time()-start)*1000)
            line = utils.add_color(line)
            #line += f'\n'

            
            # send null byte several times to indicate new line
            #self.protocol.transport.write(b'\x00\x00\x00\x00\x00' + line.encode('utf-8'))
            self.protocol.transport.write(line.encode('utf-8'))
        else:
            #self.protocol.transport.write(b'\x00\x00\x00\x00\x00' + line.encode('utf-8'))
            self.protocol.transport.write(line.encode('utf-8'))
        return

    def gain_exp(self, exp):
        exp = self.inventory_manager.gain_exp(exp)
        exp = int(exp)
        self.stat_manager.stats[StatType.EXP] += exp
        if self.stat_manager.stats[StatType.EXP] == 0:
            self.stat_manager.stats[StatType.EXP] = 0
        if exp < 0:
            self.sendLine(f'You lost: {Color.BAD}' + str(abs(exp)) + f' experience{Color.BACK}')
        if exp > 0:
            self.sendLine(f'You got: {Color.GOOD}' + str(abs(exp)) + f' experience{Color.BACK}')

    def gain_practice_points(self, pp):
        self.stat_manager.stats[StatType.PP] += pp
        if self.stat_manager.stats[StatType.PP] == 0:
            self.stat_manager.stats[StatType.PP] = 0

        if pp < 0:
            if abs(pp) >= 2:
                self.sendLine(f'You lost: {Color.BAD}' + str(abs(pp)) + f' Practice points{Color.BACK}')
            else:
                self.sendLine(f'You lost: {Color.BAD}' + str(abs(pp)) + f' Practice point{Color.BACK}')
        if pp > 0:
            if abs(pp) >= 2: 
                self.sendLine(f'You got: {Color.GOOD}' + str(abs(pp)) + f' Practice points{Color.BACK}')
            else:
                self.sendLine(f'You got: {Color.GOOD}' + str(abs(pp)) + f' Practice point{Color.BACK}')

    def queue_handle(self, line):
        self.queued_lines.append(line)

    def handle(self, line):
        #utils.debug_print(line)
        for trans in translations:
            if line.startswith(trans):
                line = translations[trans] + line[len(trans):]
                
        

        # empty lines are handled as resend last line

        # try to send answer to dialog
        # if you input something that is not a dialog answer
        # stop dialog and continue with command handling
        
            
        if self.current_dialog != None:
            if self.current_dialog.answer(line):
                return
        
        
        if not line: 
            line = self.last_line_sent
            if not line:
                return

        self.last_line_sent = line

        command = line.split()[0]

        # replace with aliases as long as it is not a settings command
        if ' '+command+'' not in ' settings ': 
            aliases = self.settings_manager.aliases
            line = ' '+line+' '
            alias_text = line            
            for alias in aliases:
                if command != alias:
                    line.replace(alias, 'say ERROR')
                    continue
                #line = line.replace(' '+alias+' ', ' '+aliases[alias]+' ')
                lines = line.split()
                length = len(lines)

                alias_text = aliases[alias]
                for i in range(0,10):
                    to_replace = f'#{i}#'
                    
                    if i < length-1:
                        
                        alias_text = alias_text.replace(to_replace, lines[i+1]).replace(to_replace,'')
                    else:
                        alias_text = alias_text.replace(to_replace,'')

                    
                #lines[0] = aliases[alias]
                #line = ' '.join(lines)
            #line = line.strip()
            line = alias_text.strip()
            
        
        

        command = line.split()[0]

        if command not in 'settings':
            if ';' in line:
                lines = line.split(';')
                for l in lines:
                    if l.split()[0] in self.settings_manager.aliases:
                        self.sendLine('An alias cannot trigger another alias')
                        continue
                    self.queued_lines.append(l)
                    #utils.debug_print(l)
                    
                return

        full_line =  line
        line = " ".join(line.split()[1::]).strip() 

        if full_line in shortcuts_to_commands:
            self.handle(shortcuts_to_commands[command])
            return

        if command in one_letter_commands:
            script = getattr(self, commands[one_letter_commands[command]])
            self.last_command_used = one_letter_commands[command]
            self.sendLine(commands[one_letter_commands[command]], msg_type = [MsgType.DEBUG])
            script(line)
            return

        best_match, best_score = utils.match_word(command, commands.keys(), get_score = True)
        if best_score < 75:
            self.sendLine(f'You wrote "{command}" did you mean "{best_match}"?\nUse "help {best_match}" to learn more about this command.')
            return

        
        script = getattr(self, commands[best_match])
        self.last_command_used = best_match
        self.sendLine('Command found: '+str(commands[best_match]), msg_type = [MsgType.DEBUG])
        script(line)

    def set_turn(self):
        super().set_turn()
        #self.sendLine(self.prompt(self))

    def finish_turn(self, force_cooldown = False):
        self.trade_manager.trade_stop(silent=True)
        self.charging_mini_game.stop()
        super().finish_turn(force_cooldown=force_cooldown)
        #self.sendLine(self.prompt(self))
        
        


# Compile all player functions
# grabs all imported functions inside of actors.player_only_functions 
# and adds those functions to the player object 
for func_name in dir(actors.player_only_functions.commands):
    func = getattr(actors.player_only_functions.commands, func_name)
    # Only assign functions to the Player class
    if callable(func):
        setattr(Player, func_name, func)
            
            