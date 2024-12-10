
#import skills
import copy
from config import ItemType, EquipmentSlotType

from items.misc import Item
from items.consumable import Consumable
from items.equipment import Equipment

def load_item(item):
    item = copy.deepcopy(item)
    item_type = item['item_type']

    if item_type == ItemType.EQUIPMENT:
        new_item = Equipment()

        new_item.name = item['name']
        new_item.description = item['description']

        #new_item.stats = item['stats']
        for key in new_item.stats:
            new_item.stats[key] = item['stats'][key]
        #new_item.requirements = item['requirements']
        for key in new_item.requirements:
            new_item.requirements[key] = item['requirements'][key]

        new_item.slot = item['slot']
        new_item.equiped = item['equiped']
        new_item.tags = item['tags']
        new_item.history = item['history']


    if item_type == ItemType.MISC:
        new_item = Item()

        new_item.name = item['name']
        new_item.description = item['description']
        new_item.tags = item['tags']
        new_item.history = item['history']

    if item_type == ItemType.CONSUMABLE:
        new_item = Consumable()

        new_item.name = item['name']
        new_item.description = item['description']
        new_item.tags = item['tags']
        new_item.history = item['history']
        new_item.skills = item['skills']
        
    

    # on creation of an item object, it receives a uuid
    # if there is no uuid present in the item dict received, then that item is being created for the first time
    # and if there is uuid present, then the item is most likely loaded from the database and should
    # receive its id, and not get a new randomly generated one
    if 'id' in item:
        new_item.id = item['id']
    if 'keep' in item:
        new_item.keep = item['keep']

    return new_item

def save_item(item):
    return item.to_dict()


