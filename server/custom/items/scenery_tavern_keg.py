
from items.misc import Item
from items.manager import load_item
class scenery_tavern_keg(Item):
    @classmethod
    def compare_replace(self, item_object):
        if "scenery_tavern_keg" != item_object.premade_id.lower():
            return False
        return True

    def add_volume(self):
        for i in self.ale_volume:
            self.ale_volume[i] += 1
            if self.ale_volume[i] >= 3:
                self.ale_volume[i] = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('fill', self.trigger_fill)
        self.description += '\nYou can "fill" to fill one mug with ale.'
        self.ale_volume = {}
        

    def trigger_fill(self, player, line):
        if player.id not in self.ale_volume:
            #player.sendLine('new player')
            self.ale_volume[player.id] = 3

        if self.ale_volume[player.id] <= 0:
            player.sendLine('The keg seems empty for now')
            return True
            
        _removed_one_mug = player.inventory_manager.remove_items_by_id(item_premade_id = 'mug', stack = 1)
        if not _removed_one_mug:
            player.sendLine('You don\'t have a mug to fill')
            return True
        
        player.simple_broadcast('You fill a mug of ale',f'{player.pretty_name()} fills a mug of ale')
        #player.inventory_manager.remove_item(items[0], 1)
        mug_of_ale = load_item('tavern_food_item_mug_of_ale')
        player.inventory_manager.add_item(mug_of_ale)
        self.ale_volume[player.id] -= 1
        return True

    def tick(self):
        #print(self.inventory_manager.owner.world)
        if self.inventory_manager.owner.world.factory.ticks_passed % (30*60) == 0:
            self.add_volume()



