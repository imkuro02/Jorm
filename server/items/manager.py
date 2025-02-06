
#import skills
import copy
from configuration.config import ItemType, EquipmentSlotType, ITEMS, CONSUMABLE_USE_PERSPECTIVES, StatType

from items.misc import Item
from items.consumable import Consumable
from items.equipment import Equipment
from items.error import ErrorItem

import random
def load_item(item_premade_id, unique_id = None): # unique_id is used for equipment seeds

    premade_id = item_premade_id
    if premade_id not in ITEMS:
        new_item = ErrorItem()
        new_item.name = '@yellowERROR@normal'
        new_item.description = 'id: '+str(premade_id)
        new_item.premade_id = premade_id
        return new_item

    item_type = ITEMS[premade_id]['item_type']

    if item_type == ItemType.EQUIPMENT:
        new_item = Equipment()

        
        

        for key in ITEMS[premade_id]['stats']:
            new_item.stats[key] = ITEMS[premade_id]['stats'][key]

        for key in ITEMS[premade_id]['requirements']:
            new_item.requirements[key] = ITEMS[premade_id]['requirements'][key]

        # set unique ID now for the seed
        rng_seed = str(unique_id)
        myrandom = random.Random(rng_seed)
        for i in range(0,myrandom.randrange(new_item.requirements[StatType.LVL])):
            stat_to_affect = myrandom.choice([key for key in new_item.stats])
            boost = myrandom.choice([-1,1,2])
            if stat_to_affect in [StatType.HPMAX, StatType.MPMAX]:
                boost = boost * 5
            new_item.stats[stat_to_affect] += boost
            new_item.requirements[stat_to_affect] += abs(boost) 
        
            
        

        new_item.slot = ITEMS[premade_id]['slot']

    if item_type == ItemType.MISC:
        new_item = Item()

    if item_type == ItemType.CONSUMABLE:
        new_item = Consumable()

        
        new_item.skills = ITEMS[premade_id]['skills']
        new_item.use_perspectives = CONSUMABLE_USE_PERSPECTIVES[ITEMS[premade_id]['use_perspectives']]


    
    new_item.name = ITEMS[premade_id]['name']
    new_item.description = ITEMS[premade_id]['description']
    new_item.premade_id = ITEMS[premade_id]['premade_id']


    # on creation of an item object, it receives a uuid
    # if there is no uuid present in the item dict received, then that item is being created for the first time
    # and if there is uuid present, then the item is most likely loaded from the database and should
    # receive its id, and not get a new randomly generated one
    

    return new_item
  

def save_item(item):
    return item.to_dict()


