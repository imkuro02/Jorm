from player_only_functions.checks import check_no_empty_line, check_not_in_combat, check_alive
from config import ItemType
import utils

def inventory_add_item(self, item):
    self.inventory[item.id] = item

def inventory_remove_item(self, item_id):
    del self.inventory[item_id]
    
@check_no_empty_line
def command_identify(self, line):
    item = self.get_item(line)
    if item == None:
        return
    output = item.identify()
    self.sendLine(output)


@check_no_empty_line
@check_not_in_combat
@check_alive
def command_get(self, line):
    item = self.get_item(line, search_mode = 'room')

    if item == None:
        self.sendLine('Get what?')
        return

    self.inventory_add_item(item)
    self.room.inventory_remove_item(item.id)
    self.simple_broadcast(
        f'You get {item.name}', 
        f'{self.pretty_name()} gets {item.name}'
        )

@check_no_empty_line
@check_not_in_combat
@check_alive
def command_drop(self, line):
    item = self.get_item(line, search_mode = 'unkept')
    if item == None:
        self.sendLine(f'Drop what?')
        return

    if item.keep == True:
        self.sendLine(f'{item.name} is keept')
        return

    if item.item_type == ItemType.EQUIPMENT:
        if item.equiped:
            self.sendLine(f'You can\'t drop worn items')
            return

    self.simple_broadcast(
        f'You drop {item.name}',
        f'{self.pretty_name()} dropped {item.name}'
    )
        
    self.room.inventory_add_item(item)
    self.inventory_remove_item(item.id)

def command_inventory(self, line):
    output = ''
    output = output + 'You look through your inventory and see:\n'
    
    for i in self.inventory:
        if self.inventory[i].item_type == ItemType.EQUIPMENT:     
            output = output + f'{self.inventory[i].name}'
            if self.inventory[i].equiped:   output = output + f' @green({self.inventory[i].slot})@normal'
            if self.inventory[i].keep:      output = output + f' @red(K)@normal'
            output = output + '\n'

            # @cyan({self.inventory[i].slot})@normal
        else:
            output = output + f'{self.inventory[i].name}\n'
    
    self.sendLine(output)

@check_no_empty_line
def command_keep(self, line):
    item = self.get_item(line)
    if item == None:
        self.sendLine('Keep what?')
    item.keep = not item.keep
    if item.keep:
        self.sendLine(f'Keeping {item.name}')
        self.raise_item(item.id)
    else:
        self.sendLine(f'Unkeeping {item.name}')
        self.lower_item(item.id)

def raise_item(self, item_id):
    # move the item to the first position
    if item_id in self.inventory:
        value = self.inventory.pop(item_id)             # remove the key value pair
        self.inventory = {item_id: value, **self.inventory}    # reconstruct with the item first

def lower_item(self, item_id):
    # move the item to the first position
    if item_id in self.inventory:
        value = self.inventory.pop(item_id) # remove the keyvalue pair
        self.inventory[item_id] = value     # reconstruct with the item last

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