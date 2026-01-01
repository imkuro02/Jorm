import utils
from configuration.config import ItemType

def get_actor(self, line):
    return utils.get_match(line, self.room.actors)

    # Return if you cant find a target
    if not isinstance(target, Actor):
        self.sendLine(f'Could not find your target {target}')
        return None

    return target


def get_item(self, line, search_mode = 'self', inventory = None):
    line = line.strip()

    if line == '':
        return

    # you can input custom inventory
    if inventory != None:
        search_mode = None

    # search whole inventory
    if search_mode == 'self':
        inventory = self.inventory_manager.items

    # only search items that are not kept in inventory
    if search_mode == 'kept':
        inventory = {}
        for item in self.inventory_manager.items.values():
            if item.keep == False:
                continue
            inventory[item.id] = self.inventory_manager.items[item.id]

    # only search items that are not kept in inventory
    if search_mode == 'unkept':
        inventory = {}
        for item in self.inventory_manager.items.values():
            if item.keep == True:
                continue
            inventory[item.id] = self.inventory_manager.items[item.id]

    # search the rooms inventory
    if search_mode == 'room':
        inventory = self.room.inventory_manager.items

    if search_mode == 'self_and_room':
        inventory = {**self.inventory_manager.items, **self.room.inventory_manager.items}

    # search only equiped items
    if search_mode == 'equipment':
        inventory = {}
        for item in self.inventory_manager.items.values():
            if item.item_type != ItemType.EQUIPMENT:
                continue
            if item.equiped == False:
                continue
            inventory[item.id] = self.inventory_manager.items[item.id]

    # search equipement that is not yet equiped
    if search_mode == 'equipable':
        inventory = {}
        for item in self.inventory_manager.items.values():
            if item.item_type != ItemType.EQUIPMENT:
                continue
            #if item.equiped == True:
            #    continue
            inventory[item.id] = self.inventory_manager.items[item.id]

    if len(inventory) == 0:
        return

    # let this try and override what you search if you are looking for an item in a equipment slot
    if search_mode not in ['room']:
        for slot in self.slots_manager.slots.keys():
            #utils.debug_print(slot, line)
            if 'slot '+line in 'slot '+slot:
                if self.slots_manager.slots[slot] == None:
                    continue
                return self.inventory_manager.items[self.slots_manager.slots[slot]]

    return utils.get_matches(line, inventory)
