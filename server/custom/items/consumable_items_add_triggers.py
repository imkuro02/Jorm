from items.consumable import Consumable
from configuration.config import StatType, ActorStatusType
from items.manager import load_item

class consumable_item_class(Consumable):
    @classmethod
    def compare_replace(self, item_object):
        return False
        
        if item_object.__class__.__name__ != 'Consumable':
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_drink =    True
        self.can_eat =      True
        self.can_read =     True

        self.item_to_leave_after_consumed = None

        self.trigger_manager.trigger_add('eat', self.trigger_consume)
        self.trigger_manager.trigger_add('drink', self.trigger_consume)
        self.trigger_manager.trigger_add('read', self.trigger_consume)

        #self.description += f'\n{self.name} is consumable with "eat", "drink" or "read".'

        self.heal_value = 5

    def trigger_consume(self, player, line):
        if len(line.split())<=1:
            return False

        old_line = line
        items = player.get_item(line = line.replace('eat','').replace('drink','').replace('read','').strip(), search_mode='self')
        
        if items == None:
            return False
        
        if self == items[0]:
            attempting = 'can_'+old_line.split()[0]
            if not getattr(self, attempting):
                player.sendLine(f'You can\'t {attempting} {self.name}') 
                return True
            

            if player.status == ActorStatusType.DEAD:
                player.sendLine(f'You can\'t {attempting} {self.name} right now')
                return True

            #player.inventory_manager.remove_item(self, 1)
            attempting = attempting.replace('can_','')
            player.simple_broadcast(f'You {attempting} the {self.name}', f'{player.pretty_name()} {attempting}s the {self.name}')

            player.ai.clear_prediction()

            player.ai.prediction_item = self
            player.ai.prediction_target = player

            if self.item_to_leave_after_consumed != None:
                item_to_leave_after_consumed = load_item(self.item_to_leave_after_consumed)
                player.inventory_manager.add_item(item_to_leave_after_consumed)

            if player.room.combat == None:
                player.ai.use_prediction()
                player.ai.clear_prediction()
                return True

            if player.room.combat.current_actor == player:
                player.ai.use_prediction()
                player.ai.clear_prediction()
                return True

            player.ai.clear_prediction()

            return False
        return False
