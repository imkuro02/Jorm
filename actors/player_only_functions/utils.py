import utils
from config import ItemType

def get_entity(self, line):
    return utils.get_match(line, self.room.entities)

    # Return if you cant find a target
    if not isinstance(target, Actor):
        self.sendLine(f'Could not find your target {target}')
        return None

    return target


def get_item(self, line, search_mode = 'self'):
    line = line.strip()

    if line == '':
        return 

    # search whole inventory
    if search_mode == 'self':
        inventory = self.inventory

    # only search items that are not kept in inventory
    if search_mode == 'unkept':
        inventory = {}
        for item in self.inventory.values():
            if item.keep == True:
                continue 
            inventory[item.id] = self.inventory[item.id] 

    # search the rooms inventory
    if search_mode == 'room':
        inventory = self.room.inventory

    # search only equiped items
    if search_mode == 'equipment':
        inventory = {}
        for item in self.inventory.values():
            if item.item_type != ItemType.EQUIPMENT:
                continue 
            if item.equiped == False:
                continue 
            inventory[item.id] = self.inventory[item.id] 

    # search equipement that is not yet equiped
    if search_mode == 'equipable':
        inventory = {}
        for item in self.inventory.values():
            if item.item_type != ItemType.EQUIPMENT:
                continue 
            if item.equiped == True:
                continue 
            inventory[item.id] = self.inventory[item.id] 

    if len(inventory) == 0:
        return

    # let this try and override what you search if you are looking for an item in a equipment slot
    if search_mode not in ['room']:
        for slot in self.slots.keys():
            #print(slot, line)
            if 'slot '+line in 'slot '+slot:
                if self.slots[slot] == None:
                    continue
                return self.inventory[self.slots[slot]]

    return utils.get_match(line, inventory)