from actors.player_only_functions.checks import check_no_combat_in_room, check_no_empty_line, check_not_in_combat, check_alive, check_not_trading
from configuration.config import ItemType, StatType, Audio, LORE, Color
import utils
import items.manager as items

@check_no_empty_line
@check_not_in_combat
@check_alive
def command_trade(self, line):
    self.trade_manager.handle_trade_message(line)

@check_not_trading
@check_no_empty_line
@check_no_combat_in_room
@check_alive
def command_get(self, line):
    '''
    if line.lower() == 'all':
        items_to_get = []
        for item in self.room.inventory_manager.items.values():
            items_to_get.append(item)

        for item in items_to_get:
            if self.inventory_manager.add_item(item):
                self.room.inventory_manager.remove_item(item)
                self.simple_broadcast(
                    f'You get {item.name}',
                    f'{self.pretty_name()} gets {item.name}'
                    )
            else:
                self.sendLine('Your Inventory is full') 
        return
    '''

    item = self.get_item(line, search_mode = 'room')
    if item == None:
        self.sendLine('Get what?', sound = Audio.ERROR)
        return
    if self.inventory_manager.add_item(item):
        self.room.inventory_manager.remove_item(item)
        self.simple_broadcast(
            f'You get {item.name}',
            f'{self.pretty_name()} gets {item.name}'
            )
    else:
        self.sendLine(f'You can\'t pick up {item.name}', sound = Audio.ERROR)
    
@check_not_trading
@check_no_empty_line
@check_not_in_combat
@check_alive
def command_drop(self, line):
    '''
    if line.lower() == 'all':
        items_to_drop = []
        for item in self.inventory_manager.items.values(): 
            if item.keep:
                #self.sendLine('Can\'t drop kept items')
                continue
            if item.item_type == ItemType.EQUIPMENT:
                if item.equiped:
                    #self.sendLine('Can\'t drop equiped items')
                    continue
            items_to_drop.append(item)

        for item in items_to_drop:
            self.room.inventory_manager.add_item(item)
            self.inventory_manager.remove_item(item)

            self.simple_broadcast(
                f'You drop {item.name}',
                f'{self.pretty_name()} drops {item.name}'
                )
        return
    '''

    item = self.get_item(line)
    if item == None:
        self.sendLine('Drop what?', sound = Audio.ERROR)
        return

    if not item.can_tinker_with():
        self.sendLine('Cannot drop kept or equipped items')
        return

    self.room.inventory_manager.add_item(item)
    self.inventory_manager.remove_item(item)
    self.simple_broadcast(
        f'You drop {item.name}',
        f'{self.pretty_name()} drops {item.name}'
        )

@check_not_trading
def command_split(self, line):
    if self.inventory_manager.get_amount_of_free_item_slots() <= 0:
        self.sendLine('You don\'t have enough inventory space')
        return
    
    all_words = line.split(' ')
    if len(all_words) <= 1:
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
    
    self.inventory_manager.split_stack(item, value)
    
@check_not_trading
def command_sort(self, line):
    def get_name(item):
        return item[1].name.lower()
    
    items = []
    for key in self.inventory_manager.items.keys():
        item = self.inventory_manager.items[key]
        items.append(item)
        
    for item in items:
        self.inventory_manager.remove_item(item)
    for item in items:
        new = item.new 
        self.inventory_manager.add_item(item)
        item.new = new

    
    sorted_items = dict(sorted(self.inventory_manager.items.items(), key=get_name))
    self.inventory_manager.items = sorted_items
    self.sendLine('You sort your inventory')

    # raise kept
    for key in reversed(list(self.inventory_manager.items.keys())):
        if self.inventory_manager.items[key].keep:
            self.raise_item(key)


    # raise equipped
    for key in reversed(list(self.slots_manager.slots.keys())):
        self.raise_item(self.slots_manager.slots[key])



def command_inventory(self, line):

    columns = 1
    items = self.inventory_manager.item_count()
    if self.inventory_manager.limit >= 21:
        columns = 2
    if self.inventory_manager.limit >= 41:
        columns = 3
    columns = 2
    t = utils.Table(columns)
    

    num = 1
    for i in self.inventory_manager.items:
        output = f'{num:2}. ' +self.inventory_manager.items[i].pretty_name()
        num += 1
        

        if self.trade_manager.trade != None:
            if i in self.trade_manager.trade.offers1 or i in self.trade_manager.trade.offers2:
                output =  output + f' ({Color.ITEM_TRADING}T{Color.NORMAL})'

        
        t.add_data(output)
    
    '''
    free_slot_amount = self.inventory_manager.limit - len(self.inventory_manager.items)
    if free_slot_amount > 0:
        for i in range(0, free_slot_amount):
            t.add_data(f'{num:2}. ---')
            num+=1
    '''


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
    #output += f'{StatType.name[StatType.MONEY]}: {self.stat_manager.stats[StatType.MONEY]}\n'
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
'''

def raise_item(self, item_id):
    # move the item to the first position
    if item_id in self.inventory_manager.items:
        value = self.inventory_manager.items.pop(item_id)             # remove the key value pair
        self.inventory_manager.items = {item_id: value, **self.inventory_manager.items}    # reconstruct with the item first

def lower_item(self, item_id):
    # move the item to the first position
    if item_id in self.inventory_manager.items:
        value = self.inventory_manager.items.pop(item_id) # remove the keyvalue pair
        self.inventory_manager.items[item_id] = value     # reconstruct with the item last

@check_not_trading
def command_craft(self, line):

    if self.inventory_manager.get_amount_of_free_item_slots() < 1:
        self.sendLine('You need atleast one empty inventory space to craft')
        return
        
    line = line.replace('from',',').replace('and',',')
    line = line.split(',')
    item_to_craft = line[0]
    ingredients = line[1:]

    list_of_items = [item for item in LORE['items']]
    to_find = utils.match_word(item_to_craft, list_of_items)
    
    if to_find not in list_of_items:
        self.sendLine('Can\'t craft that')
        return

    item_id = LORE['items'][to_find]['premade_id']
    item_crafting_recipes = LORE['items'][to_find]['crafting_recipe_ingredients']
        
    recipe_to_use = None
    ingredients_to_use = []
    for item in range(0,len(ingredients)):
        ingredients_to_use.append(self.get_item(ingredients[item]))

    if None in ingredients_to_use:
        self.sendLine('You are lacking some materials')
        return

    for recipe in item_crafting_recipes:
        recipe_failed = False

        if len(ingredients_to_use) != len(recipe):
            continue

        #print(ingredients_to_use, len(ingredients_to_use))
        #print(recipe, len(recipe))
        for index in range(0,len(recipe)):
            if ingredients_to_use[index].premade_id != list(recipe)[index]:
                recipe_failed = True

        if recipe_failed:
            continue

        recipe_to_use = recipe


    if recipe_to_use == None:
        self.sendLine('Recipe not found, maybe ingredients were in the wrong order?')
        return
    
    for index in range(0,len(recipe)):
        if ingredients_to_use[index].stack < list(recipe.values())[index]: 
            self.sendLine(f'Not enough {ingredients_to_use[index].name}')
            return

        if not ingredients_to_use[index].can_tinker_with():
            self.sendLine('Cannot craft with kept or equipped items')
            return
        
    
    
    output = ''
            
    for index in range(0,len(recipe_to_use)):
        output = output + f"{list(recipe_to_use.values())[index]} {ingredients_to_use[index].name}, "
        #print(':::', ingredients_to_use[index], list(recipe_to_use.values())[index])
        self.inventory_manager.remove_item(item = ingredients_to_use[index], stack = list(recipe_to_use.values())[index])
            
        

    item = items.load_item(item_id)
    self.inventory_manager.add_item(item)

    output = f'You craft {item.name} using: ' + output[:-2]
    self.sendLine(output)

    

        

