from actors.actor import Actor
import utils
from trade import TradeManager
# import commands maps
from actors.player_only_functions.commands import one_letter_commands, commands, shortcuts_to_commands, translations
# import the commands module so all functions can be imported and assigned to player class
import actors.player_only_functions.commands 
from configuration.config import StatType, MsgType
import time
from actors.player_only_functions.settings import Settings
#from actors.enemy_ai import AIBasic
from actors.ai import PlayerAI
from actors.player_only_functions.charging_mini_game import ChargingMiniGame
        
class UpdateChecker:
    def __init__(self,actor):
        self.actor = actor
        self.protocol = actor.protocol

        self.last_room = None

    

    def tick_show_actors(self):
        if not self.actor.factory.ticks_passed % 30/10 == 0:
            return
        
        output = 'Entities:\n'
        _list = self.actor.room.actors.values()

        for par in _list:
            if par == self.actor: 
                continue
            output = output + par.pretty_name()+'\n'+par.prompt()+'\n'
        
        
        output = output[:-1] if output.endswith("\n") else output
        #output = output + self.actor.get_affects(self.actor)
        output = utils.add_color(output)
        #output = {"actors":output}
        
        self.actor.protocol.send_gmcp(output, 'Actors')


    def tick_show_map(self):
        split = ','
        if self.last_room != self.actor.room:
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
                _grid[r] = {'id': room.id, 'name': room.name, 'exits': exits, 'doorway': int(room.doorway)}

            #print(_grid)
            self.protocol.send_gmcp(_grid,'Map')

    def tick(self):
        #return
        #self.tick_show_actors()
        self.tick_show_map()
        
class Player(Actor):
    def __init__(self, protocol, name, room, _id = None):
        self.protocol = protocol
        self.admin = 0
        self.queued_lines = []
        self.msg_history = {}
        self.recently_send_message_count = 0
        self.instanced_rooms = []
        
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
        self.date_of_last_login = utils.get_unix_timestamp()
        self.time_in_game = 0
        
        
        self.settings_manager = Settings(self)
        self.ai = PlayerAI(self)

        self.charging_mini_game = ChargingMiniGame(self)

        self.update_checker = UpdateChecker(self)
        
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
        super().tick()
        
        if self.settings_manager.autobattler:
            self.ai.tick()

        self.charging_mini_game.tick()

        if self.recently_send_message_count > 0:
            self.recently_send_message_count -= 1

        if len(self.queued_lines) >= 1:
            self.handle(self.queued_lines[0])
            self.queued_lines.pop(0)

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
            
            
            
            #print((time.time()-start)*1000)
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
        if exp <= 0:
            self.sendLine('You lost: @bad' + str(abs(exp)) + ' experience@back')
        else:
            self.sendLine('You got: @yellow' + str(abs(exp)) + ' experience@back')

    def queue_handle(self, line):
        self.queued_lines.append(line)

    def handle(self, line):
        #print(line)
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
            for alias in aliases:
                line = line.replace(' '+alias+' ', ' '+aliases[alias]+' ')
            line = line.strip()

        command = line.split()[0]
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

    def finish_turn(self, force_cooldown = False):
        self.trade_manager.trade_stop(silent=True)
        self.charging_mini_game.stop()
        super().finish_turn(force_cooldown=force_cooldown)
        


# Compile all player functions
# grabs all imported functions inside of actors.player_only_functions 
# and adds those functions to the player object 
for func_name in dir(actors.player_only_functions.commands):
    func = getattr(actors.player_only_functions.commands, func_name)
    # Only assign functions to the Player class
    if callable(func):
        setattr(Player, func_name, func)
            
            