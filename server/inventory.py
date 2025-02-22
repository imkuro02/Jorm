from configuration.config import ItemType
from quest import ObjectiveCountProposal, OBJECTIVE_TYPES
from items.manager import load_item


#               proposal = ObjectiveCountProposal(OBJECTIVE_TYPES.KILL_X, self.enemy_id, 1)
#                entity.quest_manager.propose_objective_count_addition(proposal)
class InventoryManager:
    def __init__(self, owner, limit = 20):
        self.owner = owner
        self.limit = limit
        self.items = {}

    def item_count(self):
        return len(self.items)

    def is_empty(self):
        if len(self.items) == 0: 
            return True
        return False

    def add_item(self, item, stack_items = True, dont_send_objective_proposal = False):
        if stack_items:
            for _i in self.items.values():
                if item.premade_id != _i.premade_id:
                    continue
                if item.item_type != ItemType.MISC:
                    continue
                if _i.item_type != ItemType.MISC:
                    continue
                _i.stack += item.stack
                if not dont_send_objective_proposal and type(self.owner).__name__ == 'Player':
                    self.owner.quest_manager.propose_objective_count_addition(
                        ObjectiveCountProposal(OBJECTIVE_TYPES.COLLECT_X, item.premade_id, item.stack)
                    )
                return True
            
        if len(self.items) >= self.limit:
            return False
        self.items[item.id] = item
        item.new = True

        if not dont_send_objective_proposal and type(self.owner).__name__ == 'Player':
            self.owner.quest_manager.propose_objective_count_addition(
                ObjectiveCountProposal(OBJECTIVE_TYPES.COLLECT_X, item.premade_id, item.stack)
            )

        return True

    def remove_item(self, item):
        if type(self.owner).__name__ == 'Player':
            self.owner.quest_manager.propose_objective_count_addition(
                ObjectiveCountProposal(OBJECTIVE_TYPES.COLLECT_X, item.premade_id, -item.stack)
            )
        del self.items[item.id]

    def split_stack(self, item, value):
        # dont split if you are trying to take more than what is there
        if value >= item.stack:
            return
        new_item = load_item(item.premade_id)
        item.stack -= value
        new_item.stack = value
        self.add_item(new_item, stack_items = False, dont_send_objective_proposal = True) 

    def count_quest_items(self):
        if type(self.owner).__name__ == 'Player':
            for item in self.items.values():
                self.owner.quest_manager.propose_objective_count_addition(
                    ObjectiveCountProposal(OBJECTIVE_TYPES.COLLECT_X, item.premade_id, item.stack)
                )

    def give_item(self, item, receiver):
        receiver.add_item(item)
        self.remove_item(item)

    def all_items_set_new(self, new = False):
        for i in self.items.values():
            i.new = new




    