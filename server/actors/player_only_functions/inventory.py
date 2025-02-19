from actors.player_only_functions.checks import check_no_empty_line, check_not_in_combat, check_alive, check_not_trading
from configuration.config import ItemType, StatType
import utils


@check_no_empty_line
@check_not_in_combat
@check_alive
def command_trade(self, line):
    self.trade_manager.handle_trade_message(line)

@check_not_trading
@check_no_empty_line
@check_not_in_combat
@check_alive
def command_get(self, line):
    item = self.get_item(line, search_mode = 'room')
    if item == None:
        self.sendLine('Get what?')
        return
    if self.inventory_manager.add_item(item):
        self.room.inventory_manager.remove_item(item)
        self.simple_broadcast(
            f'You get {item.name}',
            f'{self.pretty_name()} gets {item.name}'
            )
    else:
        self.sendLine('Your Inventory is full')
    
@check_not_trading
@check_no_empty_line
@check_not_in_combat
@check_alive
def command_drop(self, line):
    item = self.get_item(line)
    if item == None:
        self.sendLine('Drop what?')
        return
    if item.keep:
        self.sendLine('Can\'t drop kept items')
        return
    if item.item_type == ItemType.EQUIPMENT:
        if item.equiped:
            self.sendLine('Can\'t drop equiped items')
            return
    self.room.inventory_manager.add_item(item)
    self.inventory_manager.remove_item(item)
    self.simple_broadcast(
        f'You drop {item.name}',
        f'{self.pretty_name()} drops {item.name}'
        )

from items.manager import load_item
def command_split(self, line):
    all_words = line.split(' ')
    if len(all_words) <= 0:
        self.sendLine('Command "split" needs an item, and a value')
        return
    
    
    
    value = 0
    for i in [all_words[0], all_words[-1]]:
        if not i.isnumeric():
            continue
        all_words.remove(i)
        value = int(i)
    
    item = self.get_item(' '.join(all_words))

    if item == None:
        self.sendLine('Split what?')
        return

    if item.stack <= 1:
        self.sendLine('Can\'t split this')
        return
    
    new_item = load_item(item.premade_id)
    item.stack -= value
    new_item.stack = value
    self.inventory_manager.add_item(new_item, stack_items = False) 
    

def command_inventory(self, line):

    t = utils.Table(1)

    for i in self.inventory_manager.items:
        output = self.inventory_manager.items[i].pretty_name()
        

        if self.trade_manager.trade != None:
            if i in self.trade_manager.trade.offers1 or i in self.trade_manager.trade.offers2:
                output = output + f' (@yellowT@normal)'

        t.add_data(output)

    self.sendLine(
        f'You carry ({self.inventory_manager.item_count()}/{self.inventory_manager.limit}):\n' +
        t.get_table())

    '''
    for i in self.inventory_manager.items:
        if self.inventory_manager.items[i].item_type == ItemType.EQUIPMENT:     
            output = output + f'{self.inventory_manager.items[i].name}'
            if self.inventory_manager.items[i].equiped:   output = output + f' @green({self.inventory_manager.items[i].slot})@normal'
            if self.inventory_manager.items[i].keep:      output = output + f' @red(K)@normal'
            output = output + '\n'
        else:
            output = output + f'{self.inventory_manager.items[i].name}'
            if self.inventory_manager.items[i].keep:      output = output + f' @red(K)@normal'
            output = output + '\n'

    self.sendLine(output)
    '''
    
@check_not_trading
def command_keep(self, line):
    item = self.get_item(line)
    if item == None:
        self.sendLine('Keep what?')
        return

    self.sendLine(f'Keeping {item.name}' if not item.keep else f'Unkeeping {item.name}')
    item.keep = not item.keep

def command_identify(self, line):
    item = self.get_item(line)
    if item == None:
        self.sendLine('Identify what?')
        return
    output = item.identify(identifier = self)
    self.sendLine(output)

'''
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
        else:
            output = output + f'{self.inventory[i].name}'
            if self.inventory[i].keep:      output = output + f' @red(K)@normal'
            output = output + '\n'
    
    self.sendLine(output)
    return
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
'''