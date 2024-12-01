from actors.player_only_functions.checks import check_alive, check_no_empty_line
from config import ItemType

def command_equipment(self, line):
    # if you type equip item, it will wear that item
    if line != '':
        item = self.get_item(line, search_mode = 'equipable')
        if item == None:
            return
        if item.equiped:
            self.inventory_unequip(item)
        else:
            self.inventory_equip(item)
        return

    output = 'You are wearing:\n'
    for i in self.slots:
        if None == self.slots[i]:
            output = output + f'{i + ":":<12} ...\n'
        else:
            output = output + f'{i + ":":<12} {self.inventory[self.slots[i]].name}\n'
    self.sendLine(output)

@check_no_empty_line
#@check_your_turn
@check_alive
def command_wear(self, line):

    item = self.get_item(line, search_mode = 'equipable')
    if item == None:
        self.sendLine('Wear what?')
        return

    for req in item.requirements:
        if item.requirements[req] > self.stats[req]:
            self.sendLine(f'@redYou do not meet the requirements to wear@normal {item.name}')
            return

    if item.item_type != ItemType.EQUIPMENT:
        self.sendLine(f'This item is not equipable')
        return

    if item.equiped:
        self.inventory_unequip(item)
        #self.sendLine(f'{item.name} is already equiped')
        return

    #self.inventory_remove_item(item.id)
    #self.inventory_add_item(item)
    #self.raise_item(item.id)
    self.inventory_equip(item)

@check_no_empty_line
#@check_not_in_combat
@check_alive
def command_remove(self, line):
    if line == '':
        self.sendLine(f'Remove what?')
        return

    item = self.get_item(line, search_mode = 'equipment')

    if item == None:
        self.sendLine(f'Remove what?')
        return

    if item.item_type != ItemType.EQUIPMENT:
        self.sendLine(f'This item is not equipable')
        return
    
    if item.equiped == False:
        self.sendLine(f'{item.name} is not equiped yet')
        return
    self.inventory_unequip(item)

def inventory_equip(self, item):
    if item.slot != None:
        if self.slots[item.slot] != None:
            self.inventory_unequip(self.inventory[self.slots[item.slot]])
        
        self.slots[item.slot] = item.id
        
        item.equiped = True 
        for stat_name in item.stats:
            stat_val = item.stats[stat_name]
            #print(stat_name, item.stats[stat_name])
            self.stats[stat_name] += stat_val
            #print(self.stats[stat_name])
        
        self.simple_broadcast(
            f'You equip {item.name}',
            f'{self.pretty_name()} equips {item.name}'
            )

        #self.slots[item.slot] = item.id
        #print(self.slots[item.slot])

def inventory_unequip(self, item):
    if item.equiped:
        self.slots[item.slot] = None
        item.equiped = False

        for stat_name in item.stats:
            stat_val = item.stats[stat_name]
            self.stats[stat_name] -= stat_val

        self.simple_broadcast(
            f'You unequip {item.name}',
            f'{self.pretty_name()} unequips {item.name}'
            )