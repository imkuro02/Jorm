from actors.actor import Actor
from configuration.config import NPCS

def create_npc(room, npc_id):
    
    npc = Npc(npc_id, room)

    _npc = NPCS[npc_id]
    npc.name = _npc['name']
    npc.description = _npc['description']
    npc.dialog_tree = _npc['tree']


class Dialog:
    def __init__(self, player, dialog_tree):
        self.player = player
        self.dialog_tree = dialog_tree
        self.current_line = 'start'
        self.print_dialog()    


    def get_valid_options(self):
        options = []
        if 'options' not in self.dialog_tree[self.current_line]:
            return options

        i = 1
        for option in self.dialog_tree[self.current_line]['options']:
            options.append({'index':i,'say': option['say'], 'goto': option['goto']})
            i += 1

        options.append({'index':0, 'say': 'bye', 'goto': 'bye'})
        return options

    def print_dialog(self):
        output = self.dialog_tree[self.current_line]['dialog']
        output += str(self.get_valid_options())
        self.player.sendLine(output)

        if self.current_line == 'end':
            self.end_dialog()
        
    def answer(self, line):
        try:
            line = int(line)
        except ValueError:
            line = 0
        
        options = self.get_valid_options()
        if line not in range(0,len(options)):
            line = 0

        # pick the last line that is BYE
        if line == 0:
            line = len(options) - 1

        option_chosen = options[line]

        self.player.sendLine(option_chosen['say'])
        self.current_line = option_chosen['goto']
        self.print_dialog()

    def end_dialog(self):
        self.player.current_dialog = None
        self.player = None

'''    
class Dialog:
    def __init__(self, player, dialog_tree):
        self.player = player
        self.dialog_tree = dialog_tree
        self.start_dialog()    

    def get_branch(self):
        return self.dialog_tree[self.current_line]
    
    def start_dialog(self):
        self.current_line = 'start'
        self.print_dialog()

    def print_dialog(self):
        output = ''
        output += f'@yellow{self.get_branch()["dialog"]}@normal\n'
        if 'options' in self.get_branch():
            for option in range(0,len(self.get_branch()['options'])):
                output += f'{option}: @cyan{self.get_branch()["options"][option]["say"]}@normal\n' 

        self.player.sendLine(output)

        if self.current_line == 'end':
            self.end_dialog()

    def end_dialog(self):
        self.player.current_dialog = None
        self.player = None

    def answer(self,line):
        if 'options' not in self.get_branch():
            self.print_dialog()
            self.end_dialog()
            return
        
        line = int(line)
        if line in range(0,len(self.get_branch()['options'])):
            self.player.sendLine(f'@cyan{self.get_branch()["options"][line]["say"]}@normal')
            self.current_line = self.get_branch()["options"][line]["goto"]
            self.print_dialog()
            return
        self.print_dialog()
'''

        
class Npc(Actor):
    def __init__(self, name = None, room = None, _id = None):
        super().__init__(name,room,_id)
        self.dialog_tree = None
        if self.room != None:
            self.room.move_entity(self, silent = True)

    def talk_to(self, talker):
        if talker.current_dialog != None:
            talker.sendLine('You are already conversing.')
            return
        if self.dialog_tree == None:
            talker.sendLine('There is nothing to talk about.')
            return
        talker.current_dialog = Dialog(talker, self.dialog_tree)

    def get_character_sheet(self):
        output = f'{self.pretty_name()}\n'
        # if no description then ignore
        if self.description != '': 
            output += f'@cyan{self.description}@normal\n'

        return output
    


