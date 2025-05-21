from actors.actor import Actor
import utils
from trade import TradeManager
# import commands maps
from actors.player_only_functions.commands import one_letter_commands, commands, shortcuts_to_commands
# import the commands module so all functions can be imported and assigned to player class
import actors.player_only_functions.commands 
from configuration.config import StatType
import time
from actors.player_only_functions.settings import Settings
#from actors.enemy_ai import AIBasic
from actors.ai import PlayerAI

class Player(Actor):
    def __init__(self, protocol, name, room, _id = None):
        self.protocol = protocol
        self.admin = 0
        

        super().__init__(name = name, room = room, _id = _id)

        self.last_line_sent = None
        self.last_command_used = None

        self.check_if_admin()

        self.recall_site = 'tutorial#tutorial'
        self.trade_manager = TradeManager(self)
        self.current_dialog = None

        # meta data
        self.date_of_creation = utils.get_unix_timestamp()
        self.date_of_last_login = utils.get_unix_timestamp()
        self.time_in_game = 0
        self.recently_send_message_count = 0
        
        self.settings_manager = Settings(self)
        self.ai = PlayerAI(self)
        
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
        if self.recently_send_message_count > 0:
            self.recently_send_message_count -= 1

    #def combat_over_prompt(self):
    #    self.sendLine('@yellowCombat over!@normal')
    #    if (self.stat_manager.stats[StatType.EXP] >= self.get_exp_needed_to_level()):
    #        self.sendLine('@greenYou can level up!@back')
    #    else:
    #        self.sendLine(f'@yellowNext level@back: @green{int((self.stat_manager.stats[StatType.EXP]/self.get_exp_needed_to_level())*100)}@back%')
    
    def sendSound(self, sfx):
        self.protocol.send_gmcp({'name':sfx}, 'Client.Media.Play')

    def sendLine(self, line, color = True, sound = None):
        if sound != None:
            self.sendSound(sound)
            
        if color:
            #start = time.time()
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

    def handle(self, line):
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
            script(line)
            return

        best_match, best_score = utils.match_word(command, commands.keys(), get_score = True)
        if best_score < 75:
            self.sendLine(f'You wrote "{command}" did you mean "{best_match}"?\nUse "help {best_match}" to learn more about this command.')
            return

        
        script = getattr(self, commands[best_match])
        self.last_command_used = best_match
        script(line)

# Compile all player functions
# grabs all imported functions inside of actors.player_only_functions 
# and adds those functions to the player object 
for func_name in dir(actors.player_only_functions.commands):
    func = getattr(actors.player_only_functions.commands, func_name)
    # Only assign functions to the Player class
    if callable(func):
        setattr(Player, func_name, func)
            
            