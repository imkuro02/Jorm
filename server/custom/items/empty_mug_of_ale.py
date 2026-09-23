from items.misc import Item
class CustomEmptyMugForFilling(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('fill', self.trigger_fill)

    def trigger_fill(self, player, line):
        item_name_or_id = line.replace('fill ','')
        item_found = player.get_item(item_name_or_id)
        if item_found != [self]:
            return False

        for i in player.room.inventory_manager.items.values():
            if i.premade_id == 'scenery_tavern_keg':
                i.trigger_fill(player, line)
                return True
        
        return False