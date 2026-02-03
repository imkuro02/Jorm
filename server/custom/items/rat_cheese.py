
from items.misc import Item
class rat_cheese(Item):
    @classmethod
    def compare_replace(self, item_object):
        if "rat_cheese" != item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('command_get', self.trigger_get)
        self.trigger_manager.trigger_add('eat', self.trigger_eat)


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

    def trigger_eat(self, player, line):
        items = player.get_item(line = line.replace('eat','').strip(), search_mode='self')
        if items == None:
            return False
        
        if self == items[0]:
            player.inventory_manager.remove_item(self)
            player.simple_broadcast('You eat some yummy cheese', f'{player.pretty_name()} eats some yummy cheese')
            return True
        return False
            
