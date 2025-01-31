from actors.player_only_functions.checks import check_is_admin, check_no_empty_line, check_not_in_combat
import items.manager as items
import configuration.config as config
import yaml
import os
import utils
from configuration.config import ItemType, StatType, EquipmentSlotType, SKILLS

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

def command_ranks(self, line):
    limit = 20
    if limit >= 50: limit = 50
    if limit <= 1: limit = 1
    t = utils.Table(4, 3)
    ranks = self.factory.ranks
    print(ranks)

    t.add_data('Rank')
    t.add_data('Level')
    t.add_data('Name')
    t.add_data('EXP')
    
    length = len(ranks)
    if length >= limit:
        length = limit
    for i in range(0,length):
        t.add_data(f'{i+1}. ')
        t.add_data(ranks[i]['lvl'])
        t.add_data(ranks[i]['name'])
        t.add_data(ranks[i]['exp'])
        
    
    output = t.get_table()
    self.sendLine(output)


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
'''
@check_is_admin
@check_no_empty_line
def command_create_item(self, line):
    if line in 'equipment':
        new_item = items.Equipment()
        new_item.name = 'New item'
        self.inventory_manager.add_item(new_item)

    if line in 'item':
        new_item = items.Item()
        new_item.name = 'New item'
        self.inventory_manager.add_item(new_item)

    if line in 'consumable':
        new_item = items.Consumable()
        new_item.name = 'New item'
        self.inventory_manager.add_item(new_item)
'''
'''
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
            self.inventory_manager.items[item_id].name = str(value)
            self.sendLine('@greenUpdated@normal')
            return

        if stat in 'description':
            self.inventory_manager.items[item_id].description = str(value)
            self.sendLine('@greenUpdated@normal')
            return

        if self.inventory_manager.items[item_id].item_type == ItemType.CONSUMABLE:
            if stat in 'skills':
                if value not in SKILLS:
                    self.sendLine('@redNot a valid skill_id@normal')
                    return
                if str(value).lower() == 'none':
                    self.inventory_manager.items[item_id].skills = []
                else:
                    self.inventory_manager.items[item_id].skills.append(value)
                self.sendLine('@greenUpdated@normal')
                return

        if self.inventory_manager.items[item_id].item_type == ItemType.EQUIPMENT:
            if self.inventory_manager.items[item_id].equiped:
                self.sendLine(f'command_update_item: dont update items while they are worn!!!')
                return

            if stat in 'slot':
                self.inventory_manager.items[item_id].slot = getattr(EquipmentSlotType, value)
                self.sendLine('@greenUpdated@normal')
                return
               

            if str(stat) in self.inventory_manager.items[item_id].stats:
                self.inventory_manager.items[str(item_id)].stats[str(stat)] = int(value)
                self.sendLine('@greenUpdated@normal')
                return

            if stat[0] == 'r':
                #print(stat, stat[1::])
                if str(stat[1::]) in self.inventory_manager.items[item_id].requirements:
                    self.inventory_manager.items[str(item_id)].requirements[str(stat[1::])] = int(value)
                    self.sendLine('@greenUpdated@normal')
                    return

    except Exception as e:
        self.sendLine(f'something went wrong with updating the item: {e}')
'''
@check_is_admin
@check_no_empty_line
def command_load_item(self, line):
    data = config.ITEMS
    if line not in data:
        self.sendLine(f'{line} is not a premade item')
        return
    item = items.load_item(line)
    self.inventory_manager.add_item(item)

@check_is_admin
@check_no_empty_line
def command_load_npcs(self, line):
    data = config.ENEMIES
    if line not in data:
        self.sendLine(f'{line} is not a premade npc')
        return
    from actors.npcs import create_enemy
    create_enemy(self.room, line)

def command_export(self, line):
    list_of_entities = [entity.name for entity in self.room.entities.values()]
    list_of_inventory = [utils.remove_color(item.name) for item in self.inventory_manager.items.values()]
    whole_list = list_of_entities + list_of_inventory

    best_match = utils.match_word(line, whole_list)

    # export item
    if best_match in list_of_inventory:
        item = self.get_item(best_match)
        if item == None:
            self.sendLine('cant find this item to export')
            return

        item_dict = item.to_dict()
        
        del item_dict['id']
        item_dict = {item_dict['name'].lower(): item_dict}
        yaml_text = yaml.dump(item_dict, default_flow_style=False)
        self.sendLine(yaml_text, color = False)

    # export entity
    if best_match in list_of_entities:
        entity = self.get_entity(best_match)
        entity_dict = entity.__dict__
        self.sendLine(entity_dict)


@check_is_admin
def command_reload_config(self, line):
    import configuration.config as config
    config.load()

@check_not_in_combat
@check_is_admin
def command_teleport(self, line):
    user = None
    for proto in self.protocol.factory.protocols:
        if line == proto.actor.name:
            user = proto.actor
            break
    if user != None:
        user.room.move_player(self)
        self.sendLine(f'You teleport to {user.pretty_name()}')
    else:
        self.sendLine(f'Cant find "{line}"')

@check_not_in_combat
@check_is_admin
def command_kick(self, line):
    user = None
    for proto in self.protocol.factory.protocols:
        if line == proto.actor.name:
            user = proto.actor
            break
    if user != None:
        user.protocol.disconnect()
        self.sendLine(f'{user.pretty_name()} kicked')

def command_online(self, line):
    output = ''
    t = utils.Table(4,3)
    for proto in self.protocol.factory.protocols:
        # ignore protocols that have not yet signed in
        if proto.actor == None:
            continue
        user = proto.actor
        t.add_data(user.pretty_name())
    output = t.get_table()
    self.sendLine(output)

# sql to create first admin
# sqlite> insert into admins (actor_id, admin_level) values ("a0cb51d7-4e93-49a2-b3bb-d201cbdfb10b", 100);
@check_is_admin
def command_grant_admin(self, line):
    try: 
        name, admin_level = [item.strip('"') for item in line.split()]
        admin_level = int(admin_level)
    except ValueError:
        self.sendLine('Wrong syntax (admin "username" "admin_level")')
        return

    for proto in self.protocol.factory.protocols:
        if name == proto.actor.name:
            proto.actor.admin = admin_level


