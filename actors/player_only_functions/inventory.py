from actors.player_only_functions.checks import check_no_empty_line, check_not_in_combat, check_alive
from config import ItemType, StatType
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
    #output += f'{StatType.name[StatType.MONEY]}: {self.stats[StatType.MONEY]}\n'
    if line != 'all': 
        inv = {}
        for i in self.inventory.values():
            if i.name not in inv:
                inv[i.name] = 1
            else:
                inv[i.name] += 1

        for i in inv:
            output += f'{inv[i]} x {i}\n'

        self.sendLine(output)
        return
    else:
        for i in self.inventory:
            if self.inventory[i].item_type == ItemType.EQUIPMENT:     
                output = output + f'{self.inventory[i].name}'
                if self.inventory[i].equiped:   output = output + f' @green({self.inventory[i].slot})@normal'
                if self.inventory[i].keep:      output = output + f' @red(K)@normal'
                output = output + '\n'
            else:
                output = output + f'{self.inventory[i].name}'
                if self.inventory[i].keep:      output = output + f' @red(K)@normal'
                output = output + '\n'
        
        self.sendLine(output)
        return

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
