from items.consumable import Consumable
class food_that_cannot_leave_tavern(Consumable):
    @classmethod
    def compare_replace(self, item_object):
        if ' tavern_food_item_' not in ' '+item_object.premade_id.lower():
            return False
        return True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('command_go', self.trigger_go)
        self.description += f'\n{self.name} cannot be brought out of the tavern.'

    def trigger_go(self, player, line):
        if player.room.__class__.__name__ == 'tavern_room':
            return False
            
        player.sendLine(f'The bartender takes {self.pretty_name()} away as you leave')
        player.inventory_manager.remove_item(self)

        return False