from items.consumable import Consumable
class CustomFoodCannotLeaveTavern(Consumable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('command_go', self.trigger_go)
        self.description += f'\n{self.name} cannot be brought out of the tavern.'

    def trigger_go(self, player, line):
        if player.room.__class__.__name__ == 'tavern_room':
            return False
            
        player.send_line(f'The bartender takes {self.pretty_name(identifier = player)} away as you leave')
        player.inventory_manager.remove_item(self)

        return False