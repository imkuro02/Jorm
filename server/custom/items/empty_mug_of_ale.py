from items.misc import Item
class empty_mug_for_filling(Item):
    @classmethod
    def compare_replace(self, item_object):
        if 'mug' != item_object.premade_id.lower():
            return False
        return True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('fill', self.trigger_fill)

    def trigger_fill(self, player, line):
        item_found = player.get_item(line.replace('fill ',''))
        if item_found != [self]:
            return False

        for i in player.room.inventory_manager.items.values():
            if i.premade_id == 'scenery_tavern_keg':
                i.trigger_fill(player, line)
                return True
        
        return False