from actors.player_only_functions.checks import check_is_admin, check_no_empty_line, check_not_in_combat
import items.manager as items
from items.manager import load_item
import configuration.config as config
import yaml
import os
import utils
from configuration.config import ItemType, StatType, EquipmentSlotType, SKILLS, LORE

def command_help(self, line):
    files = os.listdir('help')
    file_text = [f.replace('.txt', '') for f in files]
    if line == '':
        output = f'@redNo command found, here are all commands you can use help on@normal\n'
        for i in file_text:
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
    limit = 200
    if limit >= 500: limit = 500
    if limit <= 1: limit = 1
    t = utils.Table(6, 3)
    ranks = self.factory.ranks
    #ranks = ranks[::-1]
    
    t.add_data('Rank')
    t.add_data('Level')
    t.add_data('Name')
    t.add_data('EXP')
    #t.add_data('Created')
    t.add_data('Last Login')
    t.add_data('In game time')
    
    length = len(ranks)
    if length >= limit:
        length = limit
    for i in range(0,length):
        #t.add_data(f'{len(ranks)-i}. ')
        t.add_data(f'{i+1}. ')
        t.add_data(ranks[i]['lvl'])
        t.add_data(ranks[i]['name'])
        t.add_data(ranks[i]['exp'])
        #t.add_data(utils.get_datetime_from_unix(ranks[i]['date_of_creation']))
        t.add_data(utils.get_datetime_ago_from_unix(ranks[i]['date_of_last_login']))
        t.add_data(utils.seconds_to_dhms(ranks[i]['time_in_game']))
        
    
    output = t.get_table()
    self.sendLine(output)




def command_send_prompt(self, line):
    self.sendLine(self.prompt())


@check_is_admin
def command_gain_exp(self, exp):
    try:
        self.stat_manager.stats[StatType.EXP] += int(exp)
    except ValueError:
        print('gain_exp needs a int')
        pass

@check_is_admin
def command_bonus(self, line):
    if line == '':
        self.sendLine('check help admin for syntax')
        return

    if len(line.split(',')) != 4:
        self.sendLine('check help admin for syntax')
        return
    
    item_name, type, key, val = line.split(',')
    item = self.get_item(item_name)
    
    if item == None:
        self.sendLine('Bonus what? (cant find item)')
        return
    
    if item.item_type != ItemType.EQUIPMENT:
        self.sendLine('Cant bonus a non equipable item')
        return

    if item.equiped:
        self.sendLine('Cant bonus a currently equipped item')
        return

    try:
        val = int(val)
    except ValueError:
        self.sendLine('Value is not an intiger')
        return

    from items.equipment import EquipmentBonus
    boon = EquipmentBonus(type, key, val)
    item.manager.add_bonus(boon)

    

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
                    self.inventory_manager.items[item_id].skill_manager.skills = []
                else:
                    self.inventory_manager.items[item_id].skill_manager.skills.append(value)
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
               

            if str(stat) in self.inventory_manager.items[item_id].stat_manager.stats:
                self.inventory_manager.items[str(item_id)].stat_manager.stats[str(stat)] = int(value)
                self.sendLine('@greenUpdated@normal')
                return

            if stat[0] == 'r':
                #print(stat, stat[1::])
                if str(stat[1::]) in self.inventory_manager.items[item_id].stat_manager.reqs:
                    self.inventory_manager.items[str(item_id)].stat_manager.reqs[str(stat[1::])] = int(value)
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
    if line == 'boss':
        self.room.world.spawn_boss()
        return
    if line not in data:
        self.sendLine(f'{line} is not a premade npc')
        return
    from actors.enemy import create_enemy
    create_enemy(self.room, line)

def command_kill(self, line):
    actor = self.get_actor(line)
    if actor == None:
        self.sendLine('Kill who?')
        return
    actor.die()

def command_export(self, line):
    list_of_actors = [actor.name for actor in self.room.actors.values()]
    list_of_inventory = [utils.remove_color(item.name) for item in self.inventory_manager.items.values()]
    whole_list = list_of_actors + list_of_inventory

    best_match = utils.match_word(line, whole_list)

    # export item
    if best_match in list_of_inventory:
        item = self.get_item(best_match)
        if item == None:
            self.sendLine('cant find this item to export')
            return

        self.sendLine(item.__dict__)
        '''
        item_dict = item.to_dict()
        
        del item_dict['id']
        item_dict = {item_dict['name'].lower(): item_dict}
        yaml_text = yaml.dump(item_dict, default_flow_style=False)
        self.sendLine(yaml_text, color = False)
        '''

    # export actor
    if best_match in list_of_actors:
        actor = self.get_actor(best_match)
        actor_dict = str(actor.__dict__)
        self.sendLine(actor_dict)


@check_is_admin
def command_reload_config(self, line):
    self.sendLine('Reloading config')
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
        user.room.move_actor(self)
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

from quest import OBJECTIVE_TYPES, QUEST_STATE_TYPES
def command_quest(self, line = 'list'):
    lines = line.split(' ')
    command = lines[0]
    

    if command.lower() in 'list':
        count = 0
        t = utils.Table(3,3)
        t.add_data('Quest')
        t.add_data('State')
        t.add_data('')
        for quest in self.quest_manager.quests.values():
            if quest.get_state() == QUEST_STATE_TYPES.TURNED_IN:
                continue
            count += 1
            t.add_data(quest.name)
            t.add_data(quest.get_state(as_string = True))
            if quest.get_state() == QUEST_STATE_TYPES.IN_PROGRESS:
                t.add_data(f'{quest.get_progress_percentage()}%')
            else:
                t.add_data('')
        if count == 0:
            self.sendLine('You got no quests')
            return
        self.sendLine(t.get_table())
        return # show all quests
        
    if command.lower() in 'all':
        count = 0
        t = utils.Table(3,3)
        t.add_data('Quest')
        t.add_data('State')
        t.add_data('')
        for quest in self.quest_manager.quests.values():
            t.add_data(quest.name)
            t.add_data(quest.get_state(as_string = True))
            if quest.get_state() == QUEST_STATE_TYPES.IN_PROGRESS:
                #print('WHART')
                t.add_data(f'{quest.get_progress_percentage()}%')
            else:
                t.add_data('')
            count += 1
        if count == 0:
            self.sendLine('You got no quests')
            return
        self.sendLine(t.get_table())
        return 
    
    if len(lines) < 2:
        self.sendLine('Too few arguments')
        return
    quest_name = ' '.join(lines[1:])

    #if command.lower() in 'add':
    #    self.quest_manager.start_quest(quest_name)
    #    return
    if command.lower() in 'view':
        self.quest_manager.view(quest_name)
        return
    if command.lower() in 'drop':
        self.quest_manager.drop(quest_name)
        return
    
    



from actors.enemy import create_enemy
@check_no_empty_line
def command_lore(self, line):
    

    list_of_enemies = [enemy for enemy in LORE['enemies']]
    list_of_items = [item for item in LORE['items']]
    list_of_rooms = [room for room in LORE['rooms']]
    list_of_skills = [skill for skill in LORE['skills']]
    
    whole_list = list_of_enemies + list_of_items + list_of_rooms + list_of_skills

    to_find = utils.match_word(line, whole_list)
    
    #self.sendLine(to_find)
    
    if to_find in list_of_enemies:
        e_id = LORE['enemies'][to_find]['enemy_id']
        e = create_enemy(self.room.world.rooms['overworld#loading'], e_id, spawn_for_lore = True)
        
        
        all_rooms_e_spawns_in = []
        for room in LORE['rooms'].values():
            for spawn_points in room['enemies']:
                if e_id in spawn_points:
                    all_rooms_e_spawns_in.append(room['name'])

        t = utils.Table(3,3)
        for room in all_rooms_e_spawns_in:
            t.add_data(room)
        output_room_spawns = t.get_table()
        


        all_loot_they_drop = {}
        for loot in e.loot:
            all_loot_they_drop[LORE['items_name_to_id'][loot]] = str(float(e.loot[loot])*100)+'%'

        
        t = utils.Table(4,3)
        for loot in all_loot_they_drop:
            t.add_data(loot)
            t.add_data(all_loot_they_drop[loot])
        output_loot_drops = t.get_table()

        # IF THE AMOUNT OF ROOMS DOES NOT COMPLETELY COVER THE GRID
        # THEN THE TABLE WILL HAVE TWO \n INSTEAD OF ONE

        # THIS IS AN ISSUE WIT DA GUUUUH WID DA GUUUH
        # WIT DA utils.Table CODE
        output = '@yellowYou are pondering@normal: '
        output += e.get_character_sheet()+'\n'
        output += '@yellowRoaming area@normal:\n'
        output += output_room_spawns+'\n'+'\n'
        output += '@yellowPotential drops@normal:\n'
        output += output_loot_drops+'\n'+'\n'

        self.sendLine(output)

        e.die()
        return
    
    if to_find in list_of_items:
        #print(LORE['items'][to_find])
        output = '@yellowYou are pondering@normal: '
        if to_find in LORE['items']:
            item_id = LORE['items'][to_find]['premade_id']
            i = load_item(item_id)
            i.new = False
            output += i.identify(self) + '\n'
            output += '@yellowLooted from@normal: '
            for e in LORE['enemies']:
                if item_id in LORE['enemies'][e]['loot']:
                    output += f'{e}: {float(LORE["enemies"][e]["loot"][item_id]*100)}%, '
            output[-2] == '.'
        self.sendLine(output)
        return
    
    if to_find in list_of_rooms:
        return

    if to_find in list_of_skills:
        self.command_skills(to_find)
        output = '@tipItems with this skill@back:\n'
        t = utils.Table(6,1)
        t.add_data('Lvl')
        t.add_data('Name')
        t.add_data('Lvl')
        t.add_data('Name')
        t.add_data('Lvl')
        t.add_data('Name')

        sorted_items = {}
        for i in LORE['items'].values():
            if i['item_type'] != ItemType.EQUIPMENT:
                continue
            if LORE['skills'][to_find]['skill_id'] in str(i['bonuses']):
                t.add_data(f"{i['requirements']['lvl']}.")
                t.add_data(f"{i['name']}")

        output += t.get_table()
        self.sendLine(output)

    
    return


    # target yourself if not trying to target anything else
    if ' on ' not in line and ' at ' not in line:
        action = line
        action = utils.match_word(action, list_of_items + list_of_skill_names)
        target = self

    # if you are targetting something else set target to that
    else:
        action, target = line.replace(' on ',' | ').replace(' at ',' | ').split(' | ')
        action = utils.match_word(action, list_of_items + list_of_skill_names)
        #target = utils.match_word(target, list_of_items + list_of_actors)


    _action = None
    _target = None

    if action in list_of_items:
        _action = self.get_item(action)
    if action in list_of_skill_names:
        _action = name_to_id[action]
    
@check_is_admin
def command_edit_room(self, line):
    output = 'no changes'
    try:
        line = line.split()
        #self.sendLine(str(line))
        world = self.factory.world
        

    
        match line[0]:
            case 'view':
                output = self.room.id
            case 'room':
                output = world.edit_new_room(room = self.room, direction = line[1])
            case 'uroom':
                output = world.edit_del_room(room_id = line[1])
            case 'uexit':
                output = world.edit_del_exit(room = self.room, direction = line[1])
            case 'goto':
                output = world.edit_goto_room(user = self, room_id = line[1])
            case 'name':
                output = world.edit_name_room(room = self.room, name = ' '.join(line[1:]))
            case 'desc':
                output = world.edit_desc_room(room = self.room, desc = ' '.join(line[1:]))
            case 'exit':
                output = world.edit_room_new_exit(room = self.room, direction = line[1], other_room_id = line[2])
    except Exception as e:
        output = e

    self.sendLine(output)
