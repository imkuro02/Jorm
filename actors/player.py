from actors.actor import Actor
import utils

# import commands maps
from actors.player_only_functions.commands import one_letter_commands, commands
# import the commands module so all functions can be imported and assigned to player class
import actors.player_only_functions.commands 

class Player(Actor):
    def __init__(self, protocol, name, room, _id = None):
        self.protocol = protocol
        
        super().__init__(name, room, _id)

        self.last_line_sent = None
        self.last_command_used = None
        self.send_line_buffer = []

        self.admin = False
        self.set_admin()

        if self.room != None:
            self.room.move_player(self, silent = True)

        self.inventory = {}

    def set_admin(self):
        if self.protocol == None:
            return
        with open('admins.txt', 'r') as file:
            lines = file.readlines()  # Read all lines into a list
        # Check if the target string is in any of the lines
        found = any(self.protocol.id in admin for admin in lines)
        if found:
            self.sendLine('You are an admin')
            self.admin = True

    def tick(self):
        # Send buffer
        if self.factory.ticks_passed % 1 != 0:
            return
        if self.send_line_buffer == []:
            return
        line = self.send_line_buffer[0]
        self.protocol.transport.write(line.encode('utf-8'))
        self.send_line_buffer.pop(0)
        
    def sendLine(self, line, color = True):
        if color:
            line = utils.add_color(f'{line}\n')
        lines = line.replace('\n','#SPLIT#\n').split('#SPLIT#')
        for l in lines:
            self.send_line_buffer.append(l)
        

    def handle(self, line):
        # empty lines are handled as resend last line
        if not line: 
            line = self.last_line_sent
            if not line:
                return

        self.last_line_sent = line

        command = line.split()[0]
        line = " ".join(line.split()[1::]).strip()

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
            
            