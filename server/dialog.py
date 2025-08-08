from quest import QUEST_STATE_TYPES, ObjectiveCountProposal
from items.manager import load_item
from configuration.config import StatType
import random
class Dialog:
    def __init__(self, _player, _npc, _dialog_tree):
        self.player = _player
        self.npc = _npc
        self.dialog_tree = _dialog_tree
        self.current_line = 'start' 

    def send_output(self, output):
        self.player.sendLine(output.replace('<npc>',self.npc.pretty_name()).replace('<player>',self.player.pretty_name()))

    def get_valid_options(self):
        options = []
        if 'options' not in self.dialog_tree[self.current_line]:
            # dont return anything if this is the last line bcuz
            # the players wont be able to access it because of end_dialog() anyway
            if self.current_line == 'end':
                return options
            #options.append({'index':0, 'say': 'Bye', 'goto': 'end'})
            return options

        i = 1
        for option in self.dialog_tree[self.current_line]['options']:
            dic = {}
            if 'quest_check' in option:
                this_option_is_good = True
                for check in option['quest_check']:
                    quest_id =      check['id']
                    quest_state =   check['state']

                    if not 'NOT' in check:
                        if not self.player.quest_manager.check_quest_state(quest_id) == quest_state:
                            this_option_is_good = False
                    else:
                        if self.player.quest_manager.check_quest_state(quest_id) == quest_state:
                            this_option_is_good = False

                if not this_option_is_good:
                    continue
      

            if 'quest_objective_check' in option:
                this_option_is_good = True
                for check in option['quest_objective_check']:
                    quest_id =      check['id']
                    quest_objective_id = check['objective_id']
                    quest_objective_count = check['objective_count']

                    if self.player.quest_manager.check_quest_state(quest_id) == 'not_started':
                        this_option_is_good = False
                        break

                    if quest_objective_id not in self.player.quest_manager.quests[quest_id].objectives:
                        this_option_is_good = False
                        break

                    if self.player.quest_manager.quests[quest_id].objectives[quest_objective_id].count != quest_objective_count:
                        this_option_is_good = False
                        break

                
                if not 'NOT' in check:
                    if not this_option_is_good:
                        continue
                else:
                    if this_option_is_good:
                        continue

            dic['index'] = i
            dic['line'] = option['line']
            dic['goto'] = option['goto']


            if 'trade' in option:
                dic['trade'] = option['trade']

            if 'quest_turn_in' in option:
                quest_id =      option['quest_turn_in']['id']
                if not self.player.quest_manager.check_quest_state(quest_id) == QUEST_STATE_TYPES.COMPLETED:
                    continue
                    
                dic['quest_turn_in'] =   {'id':quest_id}
                if 'reward' in option['quest_turn_in']:
                    dic['reward'] =          option['quest_turn_in']['reward']
                if 'reward_exp' in option['quest_turn_in']: 
                    dic['reward_exp'] =      option['quest_turn_in']['reward_exp'] 
                if 'reward_practice_points' in option['quest_turn_in']: 
                    dic['reward_practice_points'] =      option['quest_turn_in']['reward_practice_points'] 

            if 'quest_start' in option:
                quest_id =              option['quest_start']['id']
                dic['quest_start'] =    {'id':quest_id}

            if 'quest_objective' in option:
                #self.type =             _type               # what kind of objective this is
                #self.requirement_id =   _requirement_id     # the id of whatever is required
                #self.to_add =           _to_add             # how much to add 
                requirement_id =              option['quest_objective']['requirement_id']
                objective_count_proposal = ObjectiveCountProposal('conversation', requirement_id, 1)
                dic['quest_objective_count_proposal'] = objective_count_proposal
        
            options.append(dic)

            i += 1

        #if len(options) >= 1:
        #    options.append({'index':0, 'say': 'Bye', 'goto': 'end'})
        return options

    def print_dialog(self):
        dialog_line = self.dialog_tree[self.current_line]['dialog']

        available_dialogs = []
        for option in self.dialog_tree[self.current_line]['dialog']:
            dic = {}
            if 'quest_check' in option:
                this_option_is_good = True
                for check in option['quest_check']:
                    quest_id =      check['id']
                    quest_state =   check['state']

                    if not 'NOT' in check:
                        if not self.player.quest_manager.check_quest_state(quest_id) == quest_state:
                            this_option_is_good = False
                    else:
                        if self.player.quest_manager.check_quest_state(quest_id) == quest_state:
                            this_option_is_good = False
                            
                if not this_option_is_good:
                    continue

            if 'quest_objective_check' in option:
                this_option_is_good = True
                for check in option['quest_objective_check']:
                    quest_id =      check['id']
                    quest_objective_id = check['objective_id']
                    quest_objective_count = check['objective_count']

                    if self.player.quest_manager.check_quest_state(quest_id) == 'not_started':
                        this_option_is_good = False
                        continue

                    if quest_objective_id not in self.player.quest_manager.quests[quest_id].objectives:
                        this_option_is_good = False
                        continue

                    if self.player.quest_manager.quests[quest_id].objectives[quest_objective_id].count != quest_objective_count:
                        this_option_is_good = False
                        continue

                if not 'NOT' in check:
                    if not this_option_is_good:
                        continue
                else:
                    if this_option_is_good:
                        continue

               


            available_dialogs.append(option)
        output = random.choice(available_dialogs)['line']+'@normal'



        #print('>',output)
        
        # if there is only one option, that option is end
        # so dont print anything dialogue should end

        #if len(self.get_valid_options()) >= 2:
        for i in self.get_valid_options():
            output += f'{i["index"]}: {i["line"]}\n'


        self.send_output(output)
        #self.player.sendLine(f'{output}')

        # if this is the end, or there is only one option
        # end dialogue
        if len(self.get_valid_options()) <= 0:
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
                
        # return False if the answer is invalid
        # or True if answer is valid and dialog continues
        if answer == None:
            #last_index = len(options)-1
            #answer = options[last_index]
            self.end_dialog()
            return False


        self.player.sendLine('You '+answer['line'])
        self.current_line = answer['goto']

        if 'trade' in answer:
            escape = False
            if 'give_to_player' in answer['trade']:
                if self.player.inventory_manager.get_amount_of_free_item_slots() < len(answer['trade']['give_to_player']):
                    escape = True
            if 'give_to_npc' in answer['trade']:
                for i in answer['trade']['give_to_npc']:
                    if self.player.inventory_manager.get_stacks_of_premade_id(i['item']) < i['amount']:
                        escape = True

            if escape:
                self.player.sendLine('You either lack items to give or item slots to receive.')
                self.end_dialog()
                return True

            if 'give_to_player' in answer['trade']:
                for i in answer['trade']['give_to_player']:
                    item = load_item(i['item'])
                    if item == None:
                        continue
                    item.stack = i['amount']
                    self.player.inventory_manager.add_item(item)
                    self.player.sendLine(f'You got: {item.pretty_name()}')

            if 'give_to_npc' in answer['trade']:
                for i in answer['trade']['give_to_npc']:
                    removed = self.player.inventory_manager.remove_items_by_id(i['item'], i['amount'])
                self.player.sendLine(f'You give away the items requested')

        if 'quest_objective_count_proposal' in answer:
            #self.print_dialog()
            self.player.quest_manager.propose_objective_count_addition(answer['quest_objective_count_proposal'])
            #return True

        if 'quest_start' in answer:
            #self.print_dialog()
            self.player.quest_manager.start_quest(answer['quest_start']['id'])
            #return True

        if 'quest_turn_in' in answer:
            if 'reward' in answer:
                if len(answer['reward']) > self.player.inventory_manager.get_amount_of_free_item_slots():
                    self.player.sendLine('You need more space in your inventory')
                    self.end_dialog()
                    return True

            #self.print_dialog()
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
                self.player.stat_manager.stats[StatType.EXP] += answer['reward_exp']
                self.player.sendLine(f'You got: {answer["reward_exp"]} Experience')

            if 'reward_practice_points' in answer:
                self.player.stat_manager.stats[StatType.PP] += answer['reward_practice_points']
                self.player.sendLine(f'You got: {answer["reward_practice_points"]} Practice point'+('s' if answer['reward_practice_points'] >= 2 else ''))

            
            #return True
            

        self.print_dialog()
        return True

    def end_dialog(self):
        self.player.current_dialog = None
        return
        #self.player = None