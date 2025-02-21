

from configuration.config import QUESTS, ENEMIES
import utils

class OBJECTIVE_TYPES:
    KILL_X =        'kill_x'        # kill x amount of mobs
    COLLECT_X =     'collect_x'     # collect x amount of y items
    CONVERSATION =  'conversation'  # npcs can trigger this upon correct dialogue
    TURNED_IN    =  'turned_in'     # whether this quest has been turned in or not

class QUEST_STATE_TYPES:
    IN_PROGRESS = 'in progress'
    COMPLETED = 'completed'
    TURNED_IN = 'turned in'
    NOT_STARTED = 'not started'

class QuestManager:
    def __init__(self, actor):
        self.actor = actor
        self.quests = {}

    def check_quest_state(self, quest_id):
        if quest_id not in self.quests:
            return QUEST_STATE_TYPES.NOT_STARTED
        return self.quests[quest_id].get_state()

    def turn_in_quest(self, quest_id):
        if quest_id not in self.quests:
            self.actor.sendLine('You can\'t turn in a quest you dont have')
            return


        proposal = ObjectiveCountProposal(OBJECTIVE_TYPES.TURNED_IN, OBJECTIVE_TYPES.TURNED_IN, 1)
        self.quests[quest_id].propose_objective_count_addition(proposal)

    def start_quest(self, quest_id):
        if quest_id in self.quests:
            self.actor.sendLine('You already have this quest')
            return

        quest = create_quest(quest_id)
        quest.quest_manager = self
        for objective in quest.objectives.values():
            objective.quest_manager = self
        
        if quest == None:
            self.actor.sendLine('could not start this quest')
            return

        self.quests[quest_id] = quest
        self.actor.sendLine(f'New quest: {quest.quest_name}')

    def view(self, quest_name):
        if len(self.quests) == 0:
            self.actor.sendLine('You got no quests')
            return

        quest_name = utils.match_word(quest_name, [quest.quest_name for quest in self.quests.values()])
        quest_id = None

        for quest in self.quests.values():
            if quest.quest_name == quest_name:
                quest_id = quest.quest_id
                break

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
        for quest in self.quests.values():
            if quest.objectives[OBJECTIVE_TYPES.TURNED_IN].is_completed():
                continue
            quest.propose_objective_count_addition(objective_count_proposal)

class Quest:
    def __init__(self, quest_id, quest_name, quest_description = ''):
        self.quest_id = quest_id
        self.quest_manager = None
        self.quest_name = quest_name
        self.quest_description = quest_description
        self.objectives = {}

    def view(self):
        output = ''
        output += '@yellow' + self.quest_name + '@normal' + '\n'
        output += '@cyan' + self.quest_description + '@normal\n'
        for objective in self.objectives.values():
            #print(objective.__dict__)
            if objective.objective_type == OBJECTIVE_TYPES.TURNED_IN:
                continue

            match objective.objective_type:
                case OBJECTIVE_TYPES.KILL_X:
                    enemy_name = ENEMIES[objective.objective_objective]['name']
                    output += f'Kill @red{enemy_name}@normal: {objective.objective_count}/{objective.objective_completed_at}' + '\n'


        output += self.get_state(as_string = True) + '\n'
        return output

    def get_state(self, as_string = False):
        if as_string:
            if self.objectives[OBJECTIVE_TYPES.TURNED_IN].is_completed():
                return '@greenTurned in@normal'
            if self.is_completed():
                return '@yellowCompleted@normal'
            return '@yellowIn Progress@normal'
        else:     
            if self.objectives[OBJECTIVE_TYPES.TURNED_IN].is_completed():
                return QUEST_STATE_TYPES.TURNED_IN
            if self.is_completed():
                return QUEST_STATE_TYPES.COMPLETED
            return QUEST_STATE_TYPES.IN_PROGRESS

    def is_turned_in(self):
        if self.objectives[OBJECTIVE_TYPES.TURNED_IN].is_completed():
            return True
        return False

    def is_completed(self):
        for objective in self.objectives.values():
            if objective.objective_type == OBJECTIVE_TYPES.TURNED_IN:
                continue
            if not objective.is_completed():
                return False
        return True

    def propose_objective_count_addition(self, objective_count_proposal: 'ObjectiveCountProposal'):
        for objective in self.objectives.values():
            objective.propose_objective_count_addition(objective_count_proposal)

    def add_objective(self, objective: 'Objective'):
        objective.quest_manager = self.quest_manager
        self.objectives[objective.objective_name] = objective
        

# a singular objective of a quest
class Objective:
    def __init__(self, quest_id, objective_name, objective_type, objective_objective, objective_completed_at):
        self.quest_id = quest_id                                    # the quest id for the quest
        self.quest_manager = None
        self.objective_name = objective_name                        # the name of the objective for db purposes
        self.objective_type = objective_type                        # the type of objective
        self.objective_objective = objective_objective              # the "objective" like an item etc
        self.objective_completed_at = objective_completed_at        # the value of when this objective is is_completed
        self.objective_count = 0                                    # the current value of the objective

    def is_completed(self):
        if self.objective_completed_at <= self.objective_count:
            return True

        return False

    def propose_objective_count_addition(self, objective_count_proposal: 'ObjectiveCountProposal'):
        if objective_count_proposal.objective_objective != self.objective_objective:
            return
        if objective_count_proposal.objective_type != self.objective_type:
            return
        self.objective_count += objective_count_proposal.to_add
        
def create_quest(quest_id):
    if quest_id not in  QUESTS:
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

# this is the object killing, or ooting items, will create, and send to players quest managers
# to see if any quests can go up in objective_count
class ObjectiveCountProposal:
    def __init__(self, objective_type, objective_objective, to_add = 1):
        self.objective_type = objective_type
        self.objective_objective = objective_objective
        self.to_add = to_add
 
if __name__ == '__main__':
    from configuration.config import load
    load()
    quest = create_quest('debug_quest')
    print(quest.quest_id)
    print(quest.objectives)
    for obj in quest.objectives:
        print(obj,  quest.objectives)
        print(quest.objectives[obj].__dict__)

