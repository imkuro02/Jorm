from actors.player_only_functions.checks import check_is_admin, check_no_empty_line
import items.manager as items
import yaml
import os
import utils
from config import ItemType, StatType, EquipmentSlotType, SKILLS

def command_help(self, line):
    files = os.listdir('help')
    if line == '':
        output = f'@redNo command found, here are all commands you can use help on@normal\n'
        for i in files:
            output += f'{i}\n'
        self.sendLine(output)
        return

    best_match = utils.match_word(line, files)
    with open(f'help/{best_match}', "r") as file:
        content = file.read() 
        content = content.replace(' "',' @yellow"')
        content = content.replace('" ','"@normal ')

    self.sendLine(content)

def prompt(self):
    output = f'[@red{self.stats[StatType.HP]}@normal/@red{self.stats[StatType.HPMAX]}@normal '
    output += f'@cyan{self.stats[StatType.MP]}@normal/@cyan{self.stats[StatType.MPMAX]}@normal]'
    return utils.add_color(output)

def command_send_prompt(self, line):
    self.sendLine(self.prompt())


@check_is_admin
def command_gain_exp(self, exp):
    try:
        self.stats[StatType.EXP] += int(exp)
    except ValueError:
        print('gain_exp needs a int')
        pass

@check_is_admin
@check_no_empty_line
def command_create_item(self, line):
    if line in 'equipment':
        new_item = items.Equipment()
        new_item.name = 'New item'
        self.inventory_add_item(new_item)

    if line in 'item':
        new_item = items.Item()
        new_item.name = 'New item'
        self.inventory_add_item(new_item)

    if line in 'consumable':
        new_item = items.Consumable()
        new_item.name = 'New item'
        self.inventory_add_item(new_item)

@check_is_admin
@check_no_empty_line
def command_update_item(self, line):
    #print(line)
    try:
        item = self.get_item(line.split()[0])
        item_id = item.id
        stat = line.split()[1] 
        value = " ".join(line.split()[2::])

        if stat in 'name':
            self.inventory[item_id].name = str(value)
            self.sendLine('@greenUpdated@normal')
            return

        if stat in 'description':
            self.inventory[item_id].description = str(value)
            self.sendLine('@greenUpdated@normal')
            return

        if self.inventory[item_id].item_type == ItemType.CONSUMABLE:
            if stat in 'skills':
                if value not in SKILLS:
                    self.sendLine('@redNot a valid skill_id@normal')
                    return
                if str(value).lower() == 'none':
                    self.inventory[item_id].skills = []
                else:
                    self.inventory[item_id].skills.append(value)
                self.sendLine('@greenUpdated@normal')
                return

        if self.inventory[item_id].item_type == ItemType.EQUIPMENT:
            if self.inventory[item_id].equiped:
                self.sendLine(f'command_update_item: dont update items while they are worn!!!')
                return

            if stat in 'slot':
                self.inventory[item_id].slot = getattr(EquipmentSlotType, value)
                self.sendLine('@greenUpdated@normal')
                return
               

            if str(stat) in self.inventory[item_id].stats:
                self.inventory[str(item_id)].stats[str(stat)] = int(value)
                self.sendLine('@greenUpdated@normal')
                return

            if stat[0] == 'r':
                #print(stat, stat[1::])
                if str(stat[1::]) in self.inventory[item_id].requirements:
                    self.inventory[str(item_id)].requirements[str(stat[1::])] = int(value)
                    self.sendLine('@greenUpdated@normal')
                    return

    except Exception as e:
        self.sendLine(f'something went wrong with updating the item: {e}')

@check_is_admin
@check_no_empty_line
def command_load_item(self, line):
    with open("config/items.yaml", "r") as file:
        data = yaml.safe_load(file)

    if line not in data:
        self.sendLine(f'{line} is not a premade item')
        return

    item = items.load_item(data[line])
    self.inventory_add_item(item)

def command_export_item(self, line):
    item = self.get_item(line)
    if item == None:
        self.sendLine('cant find this item to export')
        return

    #if line not in self.inventory:
    #    self.sendLine('Can\'t export this item')
    #    return

    #item = self.inventory[line]
    item_dict = item.to_dict()
    
    del item_dict['id']
    item_dict = {item_dict['name'].lower(): item_dict}
    yaml_text = yaml.dump(item_dict, default_flow_style=False)
    self.sendLine(yaml_text, color = False)
