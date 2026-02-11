from items.consumable import Consumable
class rat_cheese(Consumable):
    @classmethod
    def compare_replace(self, item_object):
        if "food_item_cheese" != item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('command_get', self.trigger_get)
        self.heal_value = 15

    def trigger_get(self, player, line):
        items = player.get_item(line = line.replace('command_get','').strip(), search_mode='room')
        if items == None:
            return False
        
        if self in items:
            for i in self.inventory_manager.owner.room.actors.values():
                if 'rat' == i.npc_id:
                    player.sendLine(f'{i.pretty_name()} hisses at you')
                    return True
        else:
            return False