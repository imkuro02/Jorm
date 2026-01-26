"""
import uuid
from configuration.config import ItemType
from items.misc import Item
import random
from systems.utils import get_object_parent
class Scenery(Item):
    def __init__(self):
        super().__init__()
        self.ambience = f'NO AMBIENCE SOUND FROM {self.name}'
        self.ambience_sfx = None
        self.can_pick_up = False
        self.invisible = False
        self.item_type = ItemType.SCENERY
        self.ticks_until_ambience = 100

    def tick(self):
        if self.ambience == None:
            return

        self.ticks_until_ambience -= 1

        if self.ticks_until_ambience <= 0:
            self.ticks_until_ambience = random.randint(30*60,30*120)

            owner = self.inventory_manager.owner
            if get_object_parent(owner) == 'Room':
                owner = owner
            else:
                owner = owner.room

            if len(owner.actors) >= 1:

                ac = random.choice(list(owner.actors.values()))
                ac.simple_broadcast(self.ambience, self.ambience, sound = self.ambience_sfx)
"""
