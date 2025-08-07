

from configuration.config import QUESTS, ENEMIES, ITEMS, NPCS, StatType
import utils
from items.manager import load_item
import random

class OBJECTIVE_TYPES:
    KILL_X =        'kill_x'        # kill x amount of mobs
    COLLECT_X =     'collect_x'     # collect x amount of y items
    CONVERSATION =  'conversation'  # npcs can trigger this upon correct dialogue
    TURNED_IN    =  'turned_in'     # whether this quest has been turned_in or not

class QUEST_STATE_TYPES:
    IN_PROGRESS =   'in_progress'
    COMPLETED =     'completed'
    TURNED_IN =     'turned_in'
    NOT_STARTED =   'not_started'

class QuestManager:
    def __init__(self, actor):
        self.actor = actor
        self.quests = {}

    def get_quest_id_from_quest_name(self, quest_name):
        quest_id = None

        if len(self.quests) == 0:
            return quest_id 
        
        quest_name = utils.match_word(quest_name, [quest.name for quest in self.quests.values()])
        

        for quest in self.quests.values():
            if quest.name == quest_name:
                quest_id = quest.id
                break

        return quest_id
    
    def drop(self, quest_name):
        quest_id = self.get_quest_id_from_quest_name(quest_name)
        if quest_id == None:
            self.actor.sendLine('Drop what quest?')
            return
        
        self.actor.sendLine(f'You drop {self.quests[quest_id].name}')
        del self.quests[quest_id]

    def check_quest_state(self, quest_id):
        if quest_id not in self.quests:
            return QUEST_STATE_TYPES.NOT_STARTED
        return self.quests[quest_id].get_state()

    def turn_in_quest(self, quest_id):
        if quest_id not in self.quests:
            self.actor.sendLine('You can\'t turn in a quest you dont have')
            return

        proposal = ObjectiveCountProposal(OBJECTIVE_TYPES.TURNED_IN, OBJECTIVE_TYPES.TURNED_IN, 1)
        proposal_accepted = self.quests[quest_id].propose_objective_count_addition(proposal)

        # turn in quest items
        if proposal_accepted:
            items = {}

            for item in self.actor.inventory_manager.items.values():
                items[item.id] = item

            for objective in self.quests[quest_id].objectives.values():
                if objective.type != OBJECTIVE_TYPES.COLLECT_X:
                    continue
                
                stacks_to_remove = objective.goal
                removed = self.actor.inventory_manager.remove_items_by_id(objective.requirement_id, stacks_to_remove)
                if not removed:
                    return False
                else:
                    return True
                '''
                for item in items.values():
                    if objective.requirement_id == item.premade_id:
                        # if stack is exact, remove that item
                        if item.stack == stacks_to_remove:
                            self.actor.inventory_manager.remove_item(item)
                            break
                        # if stack is bigger than requirement, remove only x of that 
                        if item.stack > stacks_to_remove:
                            self.actor.inventory_manager.items[item.id].stack -= stacks_to_remove
                            stacks_to_remove -= stacks_to_remove
                            break
                        # if stack is less than required, remove the item, and loop again with requirement-stack
                        if item.stack < stacks_to_remove:
                            stacks_to_remove -= item.stack
                            self.actor.inventory_manager.remove_item(item)
                            continue
                        # if you have turned_in all items then escape
                        if stacks_to_remove == 0:
                            break
                '''
        
        
    def start_quest(self, quest_id, silent = False):
        # if quest is already in your quests, skip and throw an error
        # unless its a daily quest, then delete that quest
        # and create new daily quest
        if quest_id in self.quests:
            if quest_id != 'daily_quest':
                if not silent: 
                    self.actor.sendLine('You already have this quest')
                return False
            else:
                # remove daily_quest so it can be re-added
                del self.quests[quest_id]

        quest = create_quest(quest_id, self.actor)
        if quest == None:
            self.actor.sendLine(f'@redError starting quest@normal: "{quest_id}"')
            return False
        
        quest.quest_manager = self
        for objective in quest.objectives.values():
            objective.quest_manager = self

        self.quests[quest_id] = quest
        if silent == False:
            self.actor.sendLine(f'@greenNew quest@normal: {quest.name}')
            self.view(quest.name)
        self.actor.inventory_manager.count_quest_items()

        return True # if quest was started succesfully

    def view(self, quest_name):
        if len(self.quests) == 0:
            self.actor.sendLine('You got no quests')
            return

        quest_id = self.get_quest_id_from_quest_name(quest_name)
        if quest_id == None:
            self.sendLine('View what quest?')
            return

        quest_view = self.quests[quest_id].view()
        self.actor.sendLine(quest_view)
        #for objective in self.quests[quest_id].objectives.values():
        #    self.actor.sendLine(objective.__dict__)


    def check_for_quest_completion(self, quest_id):
        if quest_id not in self.quests:
            return False
        if not self.quests[quest_id].is_completed():
            return False
        return True

    def propose_objective_count_addition(self, objective_count_proposal: 'ObjectiveCountProposal'):
        proposal_accepted = False
        for quest in self.quests.values():
            if quest.objectives[OBJECTIVE_TYPES.TURNED_IN].is_completed():
                continue
            proposal_accepted = quest.propose_objective_count_addition(objective_count_proposal)
            if proposal_accepted:
                break
        return proposal_accepted

class Quest:
    def __init__(self, _id, _name, _description):
        self.id = _id
        self.quest_manager = None
        self.name = _name
        self.description = _description
        self.objectives = {}

    def view(self):
        output = ''
        output += '@yellow' + self.name + '@normal' + '\n'
        output += '@cyan' + self.description['in_progress'] + '@normal\n'
        if self.is_completed() and not self.is_turned_in():
            output += '@cyan' + self.description['completed'] + '@normal\n'
        if self.is_turned_in():
            output += '@cyan' + self.description['completed'] + '@normal\n'
            output += '@cyan' + self.description['turned_in'] + '@normal\n'

        for objective in self.objectives.values():
            #print(objective.__dict__)
            if objective.type == OBJECTIVE_TYPES.TURNED_IN:
                continue
            
            if not self.objectives[OBJECTIVE_TYPES.TURNED_IN].is_completed():
                match objective.type:
                    case OBJECTIVE_TYPES.KILL_X:
                        enemy_name = ENEMIES[objective.requirement_id]['name']
                        output += f'Kill @red{enemy_name}@normal: {objective.count}/{objective.goal}' + '\n'
                    case OBJECTIVE_TYPES.COLLECT_X:
                        enemy_name = ITEMS[objective.requirement_id]['name']
                        output += f'Collect @white{enemy_name}@normal: {objective.count}/{objective.goal}' + '\n'
                    case OBJECTIVE_TYPES.CONVERSATION:
                        #npc = NPCS[objective.requirement_id]['name']
                        output += f'{objective.name}: {"Done" if objective.count >= objective.goal else "In progress"}' + '\n'
        output += self.get_state(as_string = True) + '\n'
        return output

    def get_state(self, as_string = False):
        if as_string:
            if self.objectives[OBJECTIVE_TYPES.TURNED_IN].is_completed():
                return '@greenTurned in@normal'
            if self.is_completed():
                return '@greenCompleted@normal'
            return '@yellowIn Progress@normal'
        else:     
            if self.objectives[OBJECTIVE_TYPES.TURNED_IN].is_completed():
                return QUEST_STATE_TYPES.TURNED_IN
            if self.is_completed():
                return QUEST_STATE_TYPES.COMPLETED
            return QUEST_STATE_TYPES.IN_PROGRESS
        
    def get_progress_percentage(self):
        count = 0
        goal = 0
        for objective in self.objectives.values():
            if objective.type == OBJECTIVE_TYPES.TURNED_IN:
                continue
            _count = objective.count
            _goal = objective.goal
            if _count > _goal:
                _count = _goal
            count += _count
            goal += _goal
            
        if goal == 0:
            return 'ERROR'
        return int((count/goal)*100)

    def is_turned_in(self):
        if self.objectives[OBJECTIVE_TYPES.TURNED_IN].is_completed():
            return True
        return False

    def is_completed(self):
        for objective in self.objectives.values():
            if objective.type == OBJECTIVE_TYPES.TURNED_IN:
                continue
            if not objective.is_completed():
                return False
        return True

    def propose_objective_count_addition(self, objective_count_proposal: 'ObjectiveCountProposal'):
        proposal_accepted = False
        for objective in self.objectives.values():
            completed = objective.is_completed()
            proposal_accepted = objective.propose_objective_count_addition(objective_count_proposal)
            if completed == False and objective.is_completed() and objective.type != OBJECTIVE_TYPES.TURNED_IN:
                # this is buggy cuz it displays quest completed BEFORE stuff actually happnes
                # like before loot is displayed as picked up for example
                self.quest_manager.actor.sendLine(f'@green{QUESTS[objective.quest_id]["name"]}@back: {objective.name} completed@normal')
            if proposal_accepted:
                continue

        return proposal_accepted

    def add_objective(self, objective: 'Objective'):
        objective.manager =                 self.quest_manager
        self.objectives[objective.name] =   objective

# this is the object killing, or ooting items, will create, and send to players quest managers
# to see if any quests can go up in objective_count
class ObjectiveCountProposal:
    def __init__(self, 
                 _type, 
                 _requirement_id, 
                 _to_add = 1
                 ):
        self.type =             _type               # what kind of objective this is
        self.requirement_id =   _requirement_id     # the id of whatever is required
        self.to_add =           _to_add             # how much to add 

# a singular objective of a quest
class Objective:
    def __init__(self, 
                 _quest_id,
                 _name, 
                 _type, 
                 _requirement_id, 
                 _goal
                 ):
        
        self.quest_id =         _quest_id           # the quest id for the quest
        self.manager =          None                # quest manager
        self.name =             _name               # the name of the objective for db purposes
        self.type =             _type               # the type of objective
        self.requirement_id =   _requirement_id     # the "objective" like an item etc
        self.goal =             _goal               # the value of when this objective is is_completed
        self.count = 0                              # the current value of the objective

    def is_completed(self):
        if self.goal <= self.count:
            return True

        return False

    def propose_objective_count_addition(self, objective_count_proposal: 'ObjectiveCountProposal'):
        #print(self.__dict__, objective_count_proposal.__dict__)
        if objective_count_proposal.requirement_id != self.requirement_id:
            return False
        if objective_count_proposal.type != self.type:
            return False
        self.count += objective_count_proposal.to_add
        return True
        
def create_daily_quest(quest_id, actor):
    quest_dict =  QUESTS[quest_id]

    def create_objective(player_level):
        possible_enemies = [enemy for enemy in ENEMIES if ENEMIES[enemy]['stats']['lvl'] <= player_level + 3 and ENEMIES[enemy]['include_in_daily_quests']]
        enemy = random.choice(possible_enemies)
        return {
        'Kill':{
            'type': OBJECTIVE_TYPES.KILL_X,
            'objective': enemy,
            'completed_at': random.randint(20 + player_level, 20 + (player_level*3))
            }
        }

    player_level = actor.stat_manager.stats[StatType.LVL]
    random_quest_objective = create_objective(player_level)

    objectives = {}
    quest = Quest(quest_id, QUESTS[quest_id]['name'], QUESTS[quest_id]['description'])
    for objective_name in random_quest_objective:
        objective = random_quest_objective[objective_name]
        quest.add_objective( Objective(quest_id, objective_name, objective['type'], objective['objective'], objective['completed_at']) )

    quest.add_objective( Objective(quest_id, OBJECTIVE_TYPES.TURNED_IN, OBJECTIVE_TYPES.TURNED_IN, OBJECTIVE_TYPES.TURNED_IN, 1) )
    return quest

def create_quest(quest_id, actor):
    if quest_id == 'daily_quest':
        quest = create_daily_quest(quest_id, actor)
        return quest

    if quest_id not in QUESTS:
        print(quest_id, 'does not exist in configuration.config QUESTS')
        return
    
    quest_dict =  QUESTS[quest_id]

    objectives = {}
    quest = Quest(quest_id, QUESTS[quest_id]['name'], QUESTS[quest_id]['description'])
    for objective_name in quest_dict['objectives']:
        objective = quest_dict['objectives'][objective_name]
        quest.add_objective( Objective(quest_id, objective_name, objective['type'], objective['objective'], objective['completed_at']) )

    quest.add_objective( Objective(quest_id, OBJECTIVE_TYPES.TURNED_IN, OBJECTIVE_TYPES.TURNED_IN, OBJECTIVE_TYPES.TURNED_IN, 1) )
    return quest


 
if __name__ == '__main__':
    from configuration.config import load
    load()
    quest = create_quest('debug_quest')
    print(quest.quest_id)
    print(quest.objectives)
    for obj in quest.objectives:
        print(obj,  quest.objectives)
        print(quest.objectives[obj].__dict__)

