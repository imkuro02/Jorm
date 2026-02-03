
from items.misc import Item
from items.manager import load_item
class scenery_tavern_keg(Item):
    @classmethod
    def compare_replace(self, item_object):
        if "scenery_tavern_keg" != item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('fill', self.trigger_fill)
        self.description += '\nYou can "fill" to fill one mug with ale.'

    def trigger_fill(self, player, line):
        _removed_one_mug = player.inventory_manager.remove_items_by_id(self, 'mug', stack=1)
        if not _removed_one_mug:
            player.sendLine('You don\'t have a mug to fill')
            return True
        
        player.simple_broadcast('You fill a mug of ale',f'{player.pretty_name()} fills a mug of ale')
        #player.inventory_manager.remove_item(items[0], 1)
        mug_of_ale = load_item('mug_of_ale')
        player.inventory_manager.add_item(mug_of_ale)
        return True
        
class mug_of_ale(Item):
    @classmethod
    def compare_replace(self, item_object):
        if "mug_of_ale" != item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('drink', self.trigger_drink)
        self.description = self.description + '\nYou can "drink ale".'
        


    def trigger_drink(self, player, line):
        items = player.get_item(line = line.replace('drink','').strip(), search_mode='self')
        if items == None:
            return False
        
        if self == items[0]:
            player.simple_broadcast('You drink from the mug of ale', f'{player.pretty_name()} drinks the mug of ale')
            player.inventory_manager.remove_item(items[0], 1)
            empty_mug = load_item('mug')
            player.inventory_manager.add_item(empty_mug)
            return True

