from actors.actor import Actor
from configuration.config import NPCS, StatType
from items.manager import load_item
from quest import QUEST_STATE_TYPES
def create_npc(room, npc_id):
    
    npc = Npc(npc_id, room)

    _npc = NPCS[npc_id]
    npc.name = _npc['name']
    npc.description = _npc['description']
    npc.dialog_tree = _npc['tree']
    return npc

class Dialog:
    def __init__(self, _player, _npc, _dialog_tree):
        self.player = _player
        self.npc = _npc
        self.dialog_tree = _dialog_tree
        self.current_line = 'start' 

    def get_valid_options(self):
        options = []
        if 'options' not in self.dialog_tree[self.current_line]:
            # dont return anything if this is the last line bcuz
            # the players wont be able to access it because of end_dialog() anyway
            if self.current_line == 'end':
                return options
            options.append({'index':0, 'say': 'bye', 'goto': 'end'})
            return options

        i = 1
        for option in self.dialog_tree[self.current_line]['options']:
            dic = {}
            if 'quest_check' in option:
                this_option_is_good = True
                for check in option['quest_check']:
                    quest_id =      check['id']
                    quest_state =   check['state']

                    if not self.player.quest_manager.check_quest_state(quest_id) == quest_state:
                        this_option_is_good = False

                if not this_option_is_good:
                    continue

            dic['index'] = i
            dic['say'] = option['say']
            dic['goto'] = option['goto']

            if 'quest_turn_in' in option:
                quest_id =      option['quest_turn_in']['id']
                if not self.player.quest_manager.check_quest_state(quest_id) == QUEST_STATE_TYPES.COMPLETED:
                    continue
                    
                dic['quest_turn_in'] =   {'id':quest_id}
                if 'reward' in option['quest_turn_in']:
                    dic['reward'] =          option['quest_turn_in']['reward']
                if 'reward_exp' in option['quest_turn_in']: 
                    dic['reward_exp'] =      option['quest_turn_in']['reward_exp'] 

            if 'quest_start' in option:
                quest_id =              option['quest_start']['id']
                dic['quest_start'] =    {'id':quest_id}
        
            options.append(dic)

            i += 1

        options.append({'index':0, 'say': 'bye', 'goto': 'end'})
        return options

    def print_dialog(self):
        output = f'{self.npc.pretty_name()} '+self.dialog_tree[self.current_line]['dialog']+'@normal'
        
        # if there is only one option, that option is end
        # so dont print anything dialogue should end
        if len(self.get_valid_options()) >= 2:
            for i in self.get_valid_options():
                output += f'{i["index"]}: {i["say"]}\n'


        self.player.sendLine(f'{output}')

        # if this is the end, or there is only one option
        # end dialogue
        if len(self.get_valid_options()) <= 1:
            self.end_dialog()
        if self.current_line == 'end':
            self.end_dialog()

        
        
    def answer(self, line):
        try:
            line = int(line)
        except ValueError:
            line = 0
        
        answer = None
        options = self.get_valid_options()

        for index, option in enumerate(options):
            if line == option['index']:
                answer = option
                break
                
        if answer == None:
            last_index = len(options)-1
            answer = options[last_index]


        self.player.sendLine('You say "'+answer['say']+'"')
        self.current_line = answer['goto']

        if 'quest_start' in answer:
            self.print_dialog()
            self.player.quest_manager.start_quest(answer['quest_start']['id'])
            return

        if 'quest_turn_in' in answer:
            if 'reward' in answer:
                if len(answer['reward']) > self.player.inventory_manager.item_free_space():
                    self.player.sendLine('You need more space in your inventory')
                    self.end_dialog()
                    return

            self.print_dialog()
            self.player.quest_manager.turn_in_quest(answer['quest_turn_in']['id'])
            self.player.sendLine(f'@greenQuest turned in@normal: {self.player.quest_manager.quests[answer["quest_turn_in"]["id"]].name}')

            if 'reward' in answer:
                for item_id in answer['reward']:
                    item = load_item(item_id)
                    if item == None:
                        continue
                    self.player.inventory_manager.add_item(item)
                    self.player.sendLine(f'You got: {item.pretty_name()}')

            if 'reward_exp' in answer:
                self.player.stats[StatType.EXP] += answer['reward_exp']
                self.player.sendLine(f'You got: {answer["reward_exp"]} Experience')

            
            return
            

        self.print_dialog()

    def end_dialog(self):
        self.player.current_dialog = None
        #self.player = None
        

        
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
            
        talker.current_dialog = Dialog(talker, self, self.dialog_tree)
        talker.current_dialog.print_dialog()

    def get_character_sheet(self):
        output = f'{self.pretty_name()}\n'
        # if no description then ignore
        if self.description != '': 
            output += f'@cyan{self.description}@normal\n'

        return output
    


