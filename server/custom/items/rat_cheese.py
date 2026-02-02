
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


    def trigger_get(self, player, line):
        items = player.get_item(line = line.replace('command_get','').strip(), search_mode='room')
        if items == None:
            return False
        
        if self in items:
            for i in self.inventory_manager.owner.room.actors.values():
                if 'rat' == i.npc_id:
                    player.sendLine('The rat hisses at you')
                    return True
        else:
            return False
