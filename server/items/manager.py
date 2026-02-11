# import skills
import copy
import random
import uuid

import systems.utils
from configuration.config import ITEMS, EquipmentSlotType, ItemType, StatType

random = random.Random()

from custom import loader as custom_loader

def load_item(item_premade_id, unique_id = None, max_stats = False):
    premade_id = item_premade_id
    if premade_id not in ITEMS:
        new_item = ErrorItem()
        new_item.name = "ERROR"
        new_item.description = "id: " + str(premade_id)
        new_item.description_room = None
        new_item.premade_id = premade_id
        return new_item

    item_type = ITEMS[premade_id]["item_type"]
    item_override_class = Item
    match item_type:
        case ItemType.MISC:
            item_override_class = Item
        case ItemType.EQUIPMENT:
            item_override_class = Equipment
        case ItemType.CONSUMABLE:
            item_override_class = Consumable
    
    _item_class_to_check = item_override_class()
    _item_class_to_check.premade_id = item_premade_id

    item_class = custom_loader.compare_replace_items(_item_class_to_check)
    if item_class != False:
        item_override_class = item_class 

    systems.utils.unload(_item_class_to_check)
    new_item = item_override_class()

    premade_id = item_premade_id


    if item_type == ItemType.EQUIPMENT:
        new_item.new = True

        for key in ITEMS[premade_id]:
            if ' stat_' not in ' '+key:
                continue
            if 'hp' in key:
                continue

            _key = key.replace('stat_','')
            new_item.stat_manager.stats[_key] += ITEMS[premade_id][key]

        for key in ITEMS[premade_id]:
            if ' req_' not in ' '+key:
                continue
            if 'hp' in key:
                continue

            _key = key.replace('req_','')
            new_item.stat_manager.reqs[_key] += ITEMS[premade_id][key]

        if not max_stats:
            if unique_id == None:
                roll = random.randint(0,2)
                if roll == 1:
                    new_item.reforge()
                
        if unique_id == None:
            unique_id = new_item.id
        else:
            new_item.id = unique_id

        try:
            if ITEMS[premade_id]["bonuses"] != 0:
                for b in ITEMS[premade_id]["bonuses"].split(","):
                    _type = b.split(":")[0]
                    _key = b.split(":")[1].split("=")[0]
                    _val = int(b.split("=")[1])
                    val = _val
                    boon = EquipmentBonus(
                        type=_type, key=_key, val=val, premade_bonus=True
                    )
                    new_item.manager.add_bonus(boon)

        except Exception as e:
            systems.utils.debug_print(f"{premade_id} error on creation {e}")

        new_item.new = False
        new_item.slot = ITEMS[premade_id]["slot"]

    if item_type == ItemType.CONSUMABLE:

        #new_item.skill_id = ITEMS[premade_id]["skill"]
        #new_item.skill_level = ITEMS[premade_id]["skill_level"]

        for skills in ITEMS[premade_id]["skills"].split(';'):
            _skill_id, _skill_lv = skills.split('=')
            new_item.skills[_skill_id] = {'skill_id': str(_skill_id), 'skill_lv': int(_skill_lv)}

        new_item.item_del_on_use = ITEMS[premade_id]["del_on_use"]
        new_item.item_add_on_use = ITEMS[premade_id]["add_on_use"]

        new_item.trigger_manager.trigger_add(ITEMS[premade_id]['triggers'],     new_item.trigger_consume)
      

    new_item.name = ITEMS[premade_id]["name"]
    new_item.description = ITEMS[premade_id]["description"]
    new_item.description_room = ITEMS[premade_id]["description_room"]
    new_item.invisible = ITEMS[premade_id]["invisible"]
    new_item.ambience = ITEMS[premade_id]["ambience"]
    new_item.ambience_sfx = ITEMS[premade_id]["ambience_sfx"]
    new_item.can_pick_up = ITEMS[premade_id]["can_pick_up"]
    if "stack_max_amount" in ITEMS[premade_id]:
        new_item.stack_max = ITEMS[premade_id]["stack_max_amount"]

    new_item.premade_id = ITEMS[premade_id]["premade_id"]

    new_item.crafting_recipe_ingredients = ITEMS[premade_id][
        "crafting_recipe_ingredients"
    ]
    new_item.crafting_ingredient_for = ITEMS[premade_id]["crafting_ingredient_for"]

    
    
    
    new_item.__init__()
    
    
    return new_item

    




def load_item2(
    item_premade_id, unique_id=None, max_stats=False
):  # unique_id is used for equipment seeds
    premade_id = item_premade_id
    if premade_id not in ITEMS:
        new_item = ErrorItem()
        new_item.name = "ERROR"
        new_item.description = "id: " + str(premade_id)
        new_item.description_room = None
        new_item.premade_id = premade_id
        return new_item

    item_type = ITEMS[premade_id]["item_type"]

    if item_type == ItemType.EQUIPMENT:
        new_item = Equipment()
        new_item.new = True

        for key in ITEMS[premade_id]["stats"]:
            if "hp" in key:
                continue
            new_item.stat_manager.stats[key] += ITEMS[premade_id]["stats"][key]

        for key in ITEMS[premade_id]["requirements"]:
            new_item.stat_manager.reqs[key] += ITEMS[premade_id]["requirements"][key]

        if unique_id == None:
            unique_id = new_item.id
        else:
            new_item.id = unique_id

        try:
            if ITEMS[premade_id]["bonuses"] != 0:
                for b in ITEMS[premade_id]["bonuses"].split(","):
                    _type = b.split(":")[0]
                    _key = b.split(":")[1].split("=")[0]
                    _val = int(b.split("=")[1])
                    val = _val
                    boon = EquipmentBonus(
                        type=_type, key=_key, val=val, premade_bonus=True
                    )
                    new_item.manager.add_bonus(boon)
        except Exception as e:
            systems.utils.debug_print(f"{premade_id} error on creation {e}")

        # if not max_stats:
        #    random.seed(new_item.id)
        #    for stat in new_item.stat_manager.stats:
        #        if new_item.stat_manager.stats[stat] <= 0:
        #            continue
        #        new_val = -random.randrange(0,new_item.stat_manager.stats[stat])
        #        if new_val >= 0:
        #            continue

        #         boon = EquipmentBonus(
        #                                 type = 'stat',
        #                                 key = stat,
        #                                 val = new_val,
        #                                 premade_bonus = True
        #                             )
        #         new_item.manager.add_bonus(boon)

        new_item.new = False
        new_item.slot = ITEMS[premade_id]["slot"]

        # if unique_id == None:
        #    roll = random.randint(0,100)
        #    if roll <= new_item.stat_manager.reqs[StatType.LVL]:
        #        new_item.reforge()

    if item_type == ItemType.MISC:
        new_item = Item()

    #if item_type == ItemType.SCENERY:
    #    new_item = Scenery()

    if item_type == ItemType.CONSUMABLE:
        new_item = Consumable()

        new_item.skill_manager.skills = ITEMS[premade_id]["skills"]
        new_item.use_perspectives = ITEMS[premade_id]["use_perspectives"]

    new_item.name = ITEMS[premade_id]["name"]
    new_item.description = ITEMS[premade_id]["description"]
    new_item.description_room = ITEMS[premade_id]["description_room"]
    new_item.invisible = ITEMS[premade_id]["invisible"]
    new_item.ambience = ITEMS[premade_id]["ambience"]
    new_item.ambience_sfx = ITEMS[premade_id]["ambience_sfx"]
    new_item.can_pick_up = ITEMS[premade_id]["can_pick_up"]
    if "stack_max_amount" in ITEMS[premade_id]:
        new_item.stack_max = ITEMS[premade_id]["stack_max_amount"]

    new_item.premade_id = ITEMS[premade_id]["premade_id"]

    new_item.crafting_recipe_ingredients = ITEMS[premade_id][
        "crafting_recipe_ingredients"
    ]
    new_item.crafting_ingredient_for = ITEMS[premade_id]["crafting_ingredient_for"]

    # on creation of an item object, it receives a uuid
    # if there is no uuid present in the item dict received, then that item is being created for the first time
    # and if there is uuid present, then the item is most likely loaded from the database and should
    # receive its id, and not get a new randomly generated one

    item_class = custom_loader.compare_replace_items(new_item)

    #print(item_class == new_item.__class__, new_item.name)
    #if item_class == new_item.__class__:
    #    return new_item
    
    systems.utils.unload(new_item)

    premade_id = item_premade_id
    if premade_id not in ITEMS:
        new_item = ErrorItem()
        new_item.name = "ERROR"
        new_item.description = "id: " + str(premade_id)
        new_item.description_room = None
        new_item.premade_id = premade_id
        return new_item

    item_type = ITEMS[premade_id]["item_type"]

    if item_type == ItemType.EQUIPMENT:
        new_item = item_class()
        new_item.new = True

        for key in ITEMS[premade_id]["stats"]:
            if "hp" in key:
                continue
            new_item.stat_manager.stats[key] += ITEMS[premade_id]["stats"][key]

        for key in ITEMS[premade_id]["requirements"]:
            new_item.stat_manager.reqs[key] += ITEMS[premade_id]["requirements"][key]

        if unique_id == None:
            unique_id = new_item.id
        else:
            new_item.id = unique_id

        try:
            if ITEMS[premade_id]["bonuses"] != 0:
                for b in ITEMS[premade_id]["bonuses"].split(","):
                    _type = b.split(":")[0]
                    _key = b.split(":")[1].split("=")[0]
                    _val = int(b.split("=")[1])
                    val = _val
                    boon = EquipmentBonus(
                        type=_type, key=_key, val=val, premade_bonus=True
                    )
                    new_item.manager.add_bonus(boon)
        except Exception as e:
            systems.utils.debug_print(f"{premade_id} error on creation {e}")

        # if not max_stats:
        #    random.seed(new_item.id)
        #    for stat in new_item.stat_manager.stats:
        #        if new_item.stat_manager.stats[stat] <= 0:
        #            continue
        #        new_val = -random.randrange(0,new_item.stat_manager.stats[stat])
        #        if new_val >= 0:
        #            continue

        #         boon = EquipmentBonus(
        #                                 type = 'stat',
        #                                 key = stat,
        #                                 val = new_val,
        #                                 premade_bonus = True
        #                             )
        #         new_item.manager.add_bonus(boon)

        new_item.new = False
        new_item.slot = ITEMS[premade_id]["slot"]

        if unique_id == None:
            roll = random.randint(0,2)
            if roll == 1:
                new_item.reforge()

    if item_type == ItemType.MISC:
        new_item = item_class()

    #if item_type == ItemType.SCENERY:
    #    new_item = item_class()

    if item_type == ItemType.CONSUMABLE:
        new_item = item_class()

        new_item.skill_manager.skills = ITEMS[premade_id]["skills"]
        new_item.use_perspectives = ITEMS[premade_id]["use_perspectives"]

    new_item.name = ITEMS[premade_id]["name"]
    new_item.description = ITEMS[premade_id]["description"]
    new_item.description_room = ITEMS[premade_id]["description_room"]
    new_item.invisible = ITEMS[premade_id]["invisible"]
    new_item.ambience = ITEMS[premade_id]["ambience"]
    new_item.ambience_sfx = ITEMS[premade_id]["ambience_sfx"]
    new_item.can_pick_up = ITEMS[premade_id]["can_pick_up"]
    if "stack_max_amount" in ITEMS[premade_id]:
        new_item.stack_max = ITEMS[premade_id]["stack_max_amount"]

    new_item.premade_id = ITEMS[premade_id]["premade_id"]

    new_item.crafting_recipe_ingredients = ITEMS[premade_id][
        "crafting_recipe_ingredients"
    ]
    new_item.crafting_ingredient_for = ITEMS[premade_id]["crafting_ingredient_for"]

    
    
    
    new_item.__init__()
    
    
    return new_item


def save_item(item):
    return item.to_dict()

from items.consumable import Consumable
from items.equipment import Equipment, EquipmentBonus
from items.error import ErrorItem
from items.misc import Item