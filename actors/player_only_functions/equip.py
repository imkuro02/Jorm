from actors.player_only_functions.checks import check_alive, check_no_empty_line
from config import ItemType, EquipmentSlotType, StatType

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

    output = f'You are wearing:\n{self.get_character_equipment(hide_empty = False)}\n'
    '''
    for i in self.slots_manager.slots:
        if None == self.slots_manager.slots[i]:
            output = output + f'{EquipmentSlotType.name[i] + ":":<12} ...\n'
        else:
            output = output + f'{EquipmentSlotType.name[i] + ":":<12} {self.inventory_manager.items[self.slots_manager.slots[i]].name}\n'
    '''
    self.sendLine(output)

def inventory_equip(self, item, forced = False):
    if item.slot != None:
        if self.slots_manager.slots[item.slot] != None:
            self.inventory_unequip(self.inventory_manager.items[self.slots_manager.slots[item.slot]])
        
        self.slots_manager.slots[item.slot] = item.id
        

        req_not_met = False
        for stat_name in item.requirements:
            if self.stats[stat_name] < item.requirements[stat_name]:
                if not forced: self.sendLine(f'@redYou do not meet the requirements of {item.requirements[stat_name]} {StatType.name[stat_name]}@normal')
                req_not_met = True
        
        if req_not_met and forced == False:
            return
        
        item.equiped = True 
        for stat_name in item.stats:
            stat_val = item.stats[stat_name]
            #print(stat_name, item.stats[stat_name])
            self.stats[stat_name] += stat_val
            #print(self.stats[stat_name])
        
        if not forced: self.simple_broadcast(
            f'You equip {item.name}',
            f'{self.pretty_name()} equips {item.name}'
            )

        #self.slots[item.slot] = item.id
        #print(self.slots[item.slot])

def inventory_unequip(self, item):
    if item.equiped:
        self.slots_manager.slots[item.slot] = None
        item.equiped = False

        for stat_name in item.stats:
            stat_val = item.stats[stat_name]
            self.stats[stat_name] -= stat_val

        self.simple_broadcast(
            f'You unequip {item.name}',
            f'{self.pretty_name()} unequips {item.name}'
            )
