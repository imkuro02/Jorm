from configuration.config import ItemType, ActorStatusType
from quest import ObjectiveCountProposal, OBJECTIVE_TYPES
from items.manager import load_item

class TriggerableManager:
    def __init__(self, inventory):
        self.inventory = inventory
        self.actor = self.inventory.owner
        self.triggered = []

    def items(self):
        return [item for item in self.inventory.items.values()]
    
    def reset_triggered(self):
        self.triggered = []

    # basically make sure an item can be triggered once even if you have multiple stacks!
    def add_triggered(self,item):
        self.triggered.append(item.premade_id)

    # called at start of turn
    def set_turn(self):
        if self.actor.status != ActorStatusType.FIGHTING: 
            return
        for item in self.items():
            if item.premade_id in self.triggered:
                continue
            item.set_turn()
            self.add_triggered(item)
        self.reset_triggered()

    # called at end of turn
    def finish_turn(self):
        if self.actor.status != ActorStatusType.FIGHTING: 
            return
        for item in self.items():
            if item.premade_id in self.triggered:
                continue
            item.finish_turn()
            self.add_triggered(item)
        self.reset_triggered()

    # called whenever hp updates in any way
    def take_damage(self, damage_obj: 'Damage'):
        if self.actor.status != ActorStatusType.FIGHTING: 
            return damage_obj
        for item in self.items():
            if item.premade_id in self.triggered:
                continue
            damage_obj = item.take_damage(damage_obj)
            self.add_triggered(item)
        self.reset_triggered()
        return damage_obj
    
    def deal_damage(self, damage_obj: 'Damage'):
        if self.actor.status != ActorStatusType.FIGHTING: 
            return damage_obj
        for item in self.items():
            if item.premade_id in self.triggered:
                continue
            damage_obj = item.deal_damage(damage_obj)
            self.add_triggered(item)
        self.reset_triggered()
        return damage_obj
    
    def dealt_damage(self, damage_obj: 'Damage'):
        if self.actor.status != ActorStatusType.FIGHTING: 
            return damage_obj
        for item in self.items():
            if item.premade_id in self.triggered:
                continue
            damage_obj = item.dealt_damage(damage_obj)
            self.add_triggered(item)
        self.reset_triggered()
        return damage_obj
    
    def gain_exp(self, exp):
        for item in self.items():
            if item.premade_id in self.triggered:
                continue
            exp = item.gain_exp(exp)
            self.add_triggered(item)
        self.reset_triggered()
        return exp
        

#               proposal = ObjectiveCountProposal(OBJECTIVE_TYPES.KILL_X, self.npc_id, 1)
#                owner.quest_manager.propose_objective_count_addition(proposal)
class InventoryManager:
    def __init__(self, owner, limit = 20*1):
        self.owner = owner
        self.triggerable_manager = TriggerableManager(self)
        self.limit = limit
        self.items = {}
        self.can_pick_up_anything = False

    # forward to triggerable manager
    def set_turn(self):
        return self.triggerable_manager.set_turn()
    def finish_turn(self):
        return self.triggerable_manager.finish_turn()
    def take_damage(self, damage_obj: 'Damage'):
        return self.triggerable_manager.take_damage(damage_obj)
    def deal_damage(self, damage_obj: 'Damage'):
        return self.triggerable_manager.deal_damage(damage_obj)
    def dealt_damage(self, damage_obj: 'Damage'):
        return self.triggerable_manager.dealt_damage(damage_obj)
    def gain_exp(self, exp):
        return self.triggerable_manager.gain_exp(exp)

    def get_item_by_id(self, item_id):
        for i in self.items.values():
            #print(i.premade_id)
            if i.premade_id == item_id:
                return i
        return None

    def item_count(self):
        return len(self.items)

    def item_free_space(self):
        return self.limit - len(self.items)

    def is_empty(self):
        if len(self.items) == 0: 
            return True
        return False

    def add_item(self, item, stack_items = True, dont_send_objective_proposal = False):
        if item.can_pick_up or self.can_pick_up_anything:
            pass
        else:
            return False

        if type(self.owner).__name__ == "Room":
            item.new = False

        if stack_items:
            for _i in self.items.values():
                if item.premade_id != _i.premade_id:
                    continue
                if item.item_type != ItemType.MISC:
                    continue
                if _i.item_type != ItemType.MISC:
                    continue
                _i.time_on_ground = 0
                _i.stack += item.stack
                if not dont_send_objective_proposal and type(self.owner).__name__ == 'Player':
                    self.owner.quest_manager.propose_objective_count_addition(
                        ObjectiveCountProposal(OBJECTIVE_TYPES.COLLECT_X, item.premade_id, item.stack)
                    )
                return True
            
        if len(self.items) >= self.limit:
            return False
        
        self.items[item.id] = item

        if type(self.owner).__name__ != 'Room':
            item.new = True
        else:
            item.new = False

        if not dont_send_objective_proposal and type(self.owner).__name__ == 'Player':
            self.owner.quest_manager.propose_objective_count_addition(
                ObjectiveCountProposal(OBJECTIVE_TYPES.COLLECT_X, item.premade_id, item.stack)
            )

        item.inventory_manager = self
        return True

    def remove_item(self, item, stack = 0):
        if stack == 0:
            if type(self.owner).__name__ == 'Player':
                self.owner.quest_manager.propose_objective_count_addition(
                    ObjectiveCountProposal(OBJECTIVE_TYPES.COLLECT_X, item.premade_id, -item.stack)
                )
            del self.items[item.id]
        if stack >= 1:
            if stack <= self.items[item.id].stack:
                if type(self.owner).__name__ == 'Player':
                    self.owner.quest_manager.propose_objective_count_addition(
                        ObjectiveCountProposal(OBJECTIVE_TYPES.COLLECT_X, item.premade_id, stack)
                    )
                self.items[item.id].stack -= stack
                if self.items[item.id].stack <= 0:
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
