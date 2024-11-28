from actor import Actor
import items
import copy 
#import skills
import utils
import yaml
import os
from config import DamageType, ItemType, ActorStatusType, StatType
class Player(Actor):
    def __init__(self, protocol, name, room):
        self.protocol = protocol
        super().__init__(name, room)
        self.last_line_sent = None

        if self.room != None:
            self.room.move_player(self)
        
        #self.commands = {}
        #self.create_command_list()
        self.one_letter_commands = {
            'i':    'command_inventory',
            'l':    'command_look',
            'w':    'command_wear',
            'r':    'command_remove',
            's':    'command_say',
            'g':    'command_go',
            'e':    'command_equipment',
            'f':    'command_fight',
            'p':    'command_send_prompt'
        }

        self.commands = {
            # da rest
            'help':     'command_help',

            'say':      'command_say',
            'go':       'command_go',
            'look':     'command_look',
            
            'level':    'command_level_up',
            'practice': 'command_practice',

            'stats':    'command_stats',
            'equipment':'command_equipment',
            'inventory':'command_inventory',
            'skills':   'command_skills',
            'affects':  'command_affects',
            

            'identify': 'command_identify',
            'get':      'command_get',
            'drop':     'command_drop',
            'wear':     'command_wear',
            'keep':     'command_keep',
            'remove':   'command_remove',

            'use':      'command_use',
            'flee':     'command_flee',
            'fight':    'command_fight',
            'pass':     'command_combat_pass_turn',
            'rest':     'command_rest',
            
            #'rename':   'command_rename_item',
            'respec':   'command_respec',

            'minew':    'command_create_item',
            'miupdate': 'command_update_item',
            'miexport': 'command_export_item',
            'miload':   'command_load_item',
            'mexp':     'command_gain_exp'

            
        }
        self.inventory = {}      

    def check_is_admin(func):
        def wrapper(self, line):
            with open('admins.txt', 'r') as file:
                lines = file.readlines()  # Read all lines into a list
            # Check if the target string is in any of the lines
            found = any(self.name in admin for admin in lines)
            if not found:
                self.sendLine('You are not an admin')
                return
            return func(self, line)
        return wrapper
                

    def check_no_empty_line(func):
        def wrapper(self, line):
            if line == '':
                self.sendLine('This command needs arguments')
                return
            else:
                return func(self, line)
        return wrapper

    def check_your_turn(func):
        def wrapper(self, line):
            if self.status != ActorStatusType.FIGHTING:
                return func(self, line)
            if self.room.combat != None:
                if self.room.combat.current_actor != self:
                    self.sendLine('Not your turn to act.')
                    return
            return func(self, line)
        return wrapper

    def check_alive(func):
        def wrapper(self, line):
            if self.status == ActorStatusType.DEAD:
                self.sendLine('@redYou are dead@normal')
                return 
            return func(self, line)
        return wrapper

    def check_not_in_combat(func):
        def wrapper(self, line):
            if self.status == ActorStatusType.FIGHTING:
                self.sendLine('You can\'t do this in combat')
                return
            return func(self, line)
        return wrapper

    def get_exp_needed_to_level(self):
        exp_needed = 2 ** self.stats[StatType.LVL]
        return exp_needed

    def get_entity(self, line):
        return utils.get_match(line, self.room.entities)

        # Return if you cant find a target
        if not isinstance(target, Actor):
            self.sendLine(f'Could not find your target {target}')
            return None

        return target

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

    def inventory_add_item(self, item):
        self.inventory[item.id] = item

    def inventory_remove_item(self, item_id):
        del self.inventory[item_id]

    @check_not_in_combat
    def command_level_up(self, stat):
        stat = stat.lower().capitalize()
        exp_needed = self.get_exp_needed_to_level()
        if self.get_exp_needed_to_level() > self.stats[StatType.EXP]:
            self.sendLine(f'You need {exp_needed-self.stats[StatType.EXP]}EXP to level up')
            return



        match stat.lower():
            case 'body':
                #self.stats[StatType.BODY] += 1
                stat = StatType.BODY
            case 'mind':
                #self.stats[StatType.MIND] += 1
                stat = StatType.MIND
            case 'soul':
                #self.stats[StatType.SOUL] += 1
                stat = StatType.SOUL
            case _:
                self.sendLine('You can only level up Body Mind or Soul')
                return

       
        self.stats[StatType.LVL] += 1
        self.stats[stat] += 1
        self.stats[StatType.PP] += 1

        self.stats[StatType.HPMAX] += 5
        self.stats[StatType.MPMAX] += 5

        self.stats[StatType.HPMAX] += self.stats[StatType.BODY] + round(self.stats[StatType.SOUL]*.5)
        self.stats[StatType.MPMAX] += self.stats[StatType.MIND] + round(self.stats[StatType.SOUL]*.5) 

        #self.stats['armor'] += round(self.stats['dex']*.4)
        #self.stats['marmor'] += round(self.stats['dex']*.4)
        
        self.sendLine(f'@green{stat} {self.stats[stat]-1} -> {self.stats[stat]}. You gained a practice point!@normal')
            
    @check_not_in_combat
    def command_practice(self, line):
        
        #print(name_to_id[skill_name])
        if len(line) <= 1:
            output = f'You have {self.stats[StatType.PP]} practice points left.\n'
            output += f'{"Skill":<20} | {"Learned":<8} | {"Level Req":<5}\n'
            for skill_id in self.factory.config.SKILLS.keys():
                if skill_id not in self.skills.keys():
                    learned = 0
                else:
                    learned = self.skills[skill_id]
                level = self.factory.config.SKILLS[skill_id]['LVL']
                output += (f'{self.factory.config.SKILLS[skill_id]["name"]:<20} | {str(learned) + "":<8} | {str(level):<5} \n')
            self.sendLine(f'{output}')
        else:
            id_to_name, name_to_id = self.use_manager.get_skills()
            skill_name = utils.match_word(line, [name for name in name_to_id.keys()])
            skill_id = name_to_id[skill_name]

            if self.stats[StatType.PP] <= 0:
                self.sendLine('@redYou do not have enough points to practice@normal')
                return

            if skill_id not in self.factory.config.SKILLS.keys():
                self.sendLine('This skill does not exist')
                return

            if skill_id in self.skills:
                # do not level beyond 6
                if self.skills[skill_id] >= 6:
                    self.sendLine(f'@redYou are already a master at "{skill_name}"@normal')
                    return
                if self.skills[skill_id] > self.stats[StatType.PP]:
                    self.sendLine(f'@redYou need {self.skills[skill_id]} practice points to practice this.@normal')
                    return


                self.stats[StatType.PP] -= self.skills[skill_id]
                self.sendLine(f'@greenYou spend {self.skills[skill_id]} practice point on "{skill_name}"@normal')
                self.skills[skill_id] += 1
                
            else:
                if self.stats[StatType.LVL] < self.factory.config.SKILLS[skill_id]['LVL']:
                    self.sendLine('@redYou are not high enough level to practice this skill@normal')
                    return
                self.skills[skill_id] = 1
                self.sendLine(f'@greenYou learned the skill "{skill_name}"@normal')
                self.stats[StatType.PP] -= 1

            
    def command_skills(self, line):
        id_to_name, name_to_id = self.use_manager.get_skills()
        if len(line) > 0:
            skill_name = utils.match_word(line, [name for name in name_to_id.keys()])
            skill_id = name_to_id[skill_name]
            skill = self.factory.config.SKILLS[skill_id]
            output = ''
            output += f'{skill["name"]}\n'
            output += f'{skill["description"]}\n'
            self.sendLine(output)
        else:
            if len(self.skills) == 0:
                self.sendLine('You do not know any skills...')
                return

            output = 'SKILLS:\n'
            max_length = max(len(skill) for skill in self.skills) + 1
            for skill_id in self.skills:
                output = output + f'{id_to_name[skill_id] + ":":<{max_length}} {self.skills[skill_id]}\n'
            self.sendLine(output)

    @check_not_in_combat
    @check_alive
    def command_respec(self, line):
        for i in self.slots.values():
            if i != None:
                self.sendLine('@redYou must unequip everything to respec@normal')
                return

        exp = self.stats[StatType.EXP]
        temp_player = Player(None, self.name, None)
        self.stats = temp_player.stats
        self.skills = temp_player.skills
        #print(temp_player)
        del temp_player

        #self.stats = self.create_new_stats()
        #self.skills = self.create_new_skills()
        self.stats[StatType.EXP] = exp
        self.sendLine('@greenYou have reset your stats, experience is kept.@normal')

    def command_stats(self, line):
        output = f'You are {self.get_character_sheet()}'
        output += f'\n'
        exp_needed = self.get_exp_needed_to_level() - self.stats[StatType.EXP]
        output += f'Level: {self.stats[StatType.LVL]}\n'
        if exp_needed > 0:
            output += f'@redYou need {exp_needed} exp to level up@normal\n'
        else:
            output += f'@greenYou have enough exp to level up@normal\n'
        output += f'Experience:      {self.stats[StatType.EXP]}\n'
        output += f'Practice Points: {self.stats[StatType.PP]}\n'
        self.sendLine(output)

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

    def command_equipment(self, line):
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

        for req in item.requirements:
            if item.requirements[req] > self.stats[req]:
                self.sendLine(f'@redYou do not meet the requirements to wear@normal {item.name}')
                return

        if item.item_type != ItemType.EQUIPMENT:
            self.sendLine(f'This item is not equipable')
            return

        if item.equiped:
            self.sendLine(f'{item.name} is already equiped')
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
    
    @check_no_empty_line
    def command_say(self, line):
        self.simple_broadcast(
            f'You say "{line}"',
            f'{self.pretty_name()} says "{line}"'
            )

    def command_look(self, line):
        def look_room(self, room_id):
            room = self.factory.world.rooms[room_id]

            if room_id == self.room.uid:
                see = f'You are in @yellow{room.name}@normal\n'
            else:
                see = f'You look at @yellow{room.name}@normal\n'
            see = see + f'@cyan{room.description}@normal\n'


            if len(room.entities) == 1:
                see = see + 'You are alone.\n'
            else:
                see = see + 'there are others here:\n'
                for i in room.entities.values():
                    if i == self:
                        pass
                    else:
                        see = see + i.pretty_name() 
                        if i.status == ActorStatusType.DEAD:
                            see = see + f' @yellow(DEAD)@normal'
                        if i.status == ActorStatusType.FIGHTING:
                            see = see + f' @yellow(FIGHTING)@normal'
                        see = see + '\n'

            exits = self.protocol.factory.world.rooms[room.uid].exits
            see = see + f'You can go: @yellow{"@normal, @yellow".join([name for name in exits])}@normal.'
            see = see + '\n'

            index = 0
            if room.inventory != {}:
                
                see = see + 'On the ground you see:\n'
                for i in room.inventory.values():
                    index += 1
                    see = see + f'{index}. {i.name}' + '\n'

            self.sendLine(see)

        if line == '':
            look_room(self, self.room.uid)
            return

        if line != '':
            #exits = self.protocol.factory.world.rooms[self.room.uid].exits
            
            #for _exit in exits:
            #    if line in _exit:
            #        room_id = self.protocol.factory.world.rooms[exits[_exit]].uid
            #        look_room(self, room_id)
            #        return

            entity = self.get_entity(line)
            if entity == None:
                return
            sheet = entity.get_character_sheet()
            self.sendLine(f'You are looking at {sheet}')

            

    @check_no_empty_line
    @check_not_in_combat
    @check_alive
    def command_go(self, line):
        world = self.protocol.factory.world
        direction = None
        for _exit in self.room.exits:
            if ' '+line.lower() in ' '+_exit.lower():
                direction = _exit
                break

        if direction == None:
            self.simple_broadcast(
                f'You walk into a wall',
                f'{self.pretty_name()} walks into a wall'
                ) 
            return

        new_room = self.room.exits[direction]

        self.simple_broadcast(
            None,
            f'{self.pretty_name()} went {direction}'
            )

        world.rooms[new_room].move_player(self)

        self.simple_broadcast(
            None,
            f'{self.pretty_name()} arrived'
            )
        self.finish_turn()

    # --------------------------------------------- ACTIONS

    # skill
    @check_no_empty_line
    @check_your_turn
    @check_alive
    def command_use(self, line):

        if line.endswith((' on', ' at')):
            self.sendLine('Use on who?')
            return

        id_to_name, name_to_id = self.use_manager.get_skills()
        list_of_skill_names = [skill for skill in name_to_id.keys()]
        list_of_consumables = [utils.remove_color(item.name) for item in self.inventory.values() if item.item_type == ItemType.CONSUMABLE]
        whole_list = list_of_consumables + list_of_skill_names

        action = None
        target = self

        # target yourself if not trying to target anything else
        if ' on ' not in line and ' at ' not in line:
            action = line
            target = self
        # if you are targetting something else set target to that
        else:
            action, target = line.replace(' on ',' | ').replace(' at ',' | ').split(' | ')
            target = self.get_entity(target)
            # if no target is found then return
            if target == None:
                return

        best_match = utils.match_word(action, whole_list)

        # if you are trying to use an item
        #print(best_match)
        if best_match in list_of_consumables:
            item = self.get_item(action)

            def use_item(item, user, target):
                self.use_manager.use_broadcast(self, target, item.use_perspectives)
                for skill in item.skills:
                    script = getattr(self.use_manager, self.use_manager.SKILLS[skill]['script_to_run']['name_of_script'])
                    arguments = self.use_manager.SKILLS[skill]['script_to_run']['arguments']
                    script(user, target, arguments)
                self.inventory_remove_item(item.id)
                return

            if target == self:
                use_item(item, self, target)
                self.finish_turn()
                return

            elif target != self:
                if self.room.combat == None:
                    self.sendLine('You can\'t use items on others out of combat')
                    return

                if self not in self.room.combat.participants.values():
                    self.sendLine(f'You can\'t use items on others while you are not in combat')
                    return

                if target not in self.room.combat.participants.values():
                    self.sendLine(f'You can\'t use items on others while they are not fighting')
                    return

                use_item(item, self, target)
                self.finish_turn()


        elif best_match in list_of_skill_names:
            skill_id = name_to_id[best_match]
            # if skills.use finished with True statement and there were no errors
            if self.use_manager.use_skill(self, target, skill_id):
                self.finish_turn()


    # potion
    @check_no_empty_line
    def command_quaff(self, line):
        self.simple_broadcast(
            f'You quaff {line}',
            f'{self.pretty_name()} quaffs {line}'
            )

    # potion on other
    @check_no_empty_line
    def command_throw(self, line):
        self.simple_broadcast(
            f'You throw {line}',
            f'{self.pretty_name()} throw {line}'
            )

    # scrolls
    @check_no_empty_line
    def command_recite(self, line):
        self.simple_broadcast(
            f'You recite {line}',
            f'{self.pretty_name()} recites {line}'
            )

    @check_not_in_combat
    def command_rest(self, line):
        if self.status == ActorStatusType.DEAD:
            self.status = ActorStatusType.NORMAL

            self.stats[StatType.HP] = self.stats[StatType.HPMAX]
            self.stats[StatType.MP] = self.stats[StatType.MPMAX]

            self.simple_broadcast(
                'You ressurect',
                f'{self.pretty_name()} ressurects')
            self.protocol.factory.world.rooms['home'].move_player(self)
            self.simple_broadcast(
                None,
                f'{self.pretty_name()} has ressurected')
        else:

            self.stats[StatType.HP] = self.stats[StatType.HPMAX]
            self.stats[StatType.MP] = self.stats[StatType.MPMAX]

            if self.room.uid == 'home':
                self.simple_broadcast(
                    f'You rest',
                    f'{self.pretty_name()} rests'
                    )
            else:
                self.simple_broadcast(
                    f'You return to town to rest',
                    f'{self.pretty_name()} returns back to town to rest'
                    )
                self.protocol.factory.world.rooms['home'].move_player(self)
                self.simple_broadcast(
                    None,
                    f'{self.pretty_name()} has returned to town to rest'
                    )
            
        

    # --------------------------------------------- MOD COMMANDS

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
                print(stat, value)
                if stat in 'skills':
                    if value not in self.factory.config.SKILLS:
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
                    if str(value) in self.slots:
                        self.inventory[item_id].slot = EquipmentSlotType(stat)
                        self.sendLine('@greenUpdated@normal')
                        return
                    if str(value).lower() == 'none':
                        self.inventory[item_id].slot = None
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

    '''
    def command_syntax(self, line):
        output = ''
        for func_name in HELPFILE:
            output = output + f'The syntax for "@red{func_name}@normal" is "@red{HELPFILE[func_name]}@normal"\n'
        self.sendLine(output)

    def command_explore(self, line):
        self.room.explore()
        
    def command_next(self, line):
        if self.room.combat != None:
            self.sendLine('You can\'t venture forth while in combat!')
        self.room.next()
    '''
    @check_alive
    @check_your_turn
    def command_flee(self, line):
        if self.room.combat == None:
            self.sendLine('You are not in combat, you don\'t need to flee')
            return
        self.simple_broadcast(
            f'You have fled back to town',
            f'{self.pretty_name()} flees!'
        )
        self.protocol.factory.world.rooms['home'].move_player(self, silent = True)
        self.status = ActorStatusType.NORMAL
        self.simple_broadcast(
            None,
            f'{self.pretty_name()} comes running in a panic!'
        )

    @check_alive
    def command_fight(self, line):
        error_output = self.room.new_combat()
        if isinstance(error_output, str):
            self.sendLine(error_output)

    @check_alive
    #@check_your_turn
    def command_combat_pass_turn(self, line):
        if self.room.combat == None:
            self.finish_turn()
            return
        if self.status != ActorStatusType.FIGHTING:
            self.finish_turn()
            return
        if self.room.combat.current_actor != self:
            return
        self.simple_broadcast(
            'You pass your turn',
            f'{self.pretty_name()} passes their turn.'
        )
        self.finish_turn()

    def command_affects(self, line):
        output = ''
        if line == '':
            if len(self.affect_manager.affects) == 0:
                output = 'You are not affected by anything'
            else:
                output = 'You are affected by:\n' 
                output += f'{"Affliction":<15} {"For":<3} {"Info"}\n'
                for aff in self.affect_manager.affects.values():
                    output += f'{aff.info()}'
        else:
            output = self.affect_manager.load_affect(line)
            if output == None:
                self.sendLine('Could not load affect')
                return
            self.affect_manager.set_affect(output)
        self.sendLine(output)

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

    def sendLine(self, line, color = True):
        #self.sendLine()
        if color:
            line = utils.add_color(f'{line}\n')
        self.protocol.transport.write(line.encode('utf-8'))

    def handle(self, line):
        
        # empty lines are handled as resend last line
        if not line: 
            line = self.last_line_sent
            if not line:
                return

        self.last_line_sent = line

        command = line.split()[0]
        line = " ".join(line.split()[1::]).strip()

        if command in self.one_letter_commands:
            script = getattr(self, self.one_letter_commands[command])
            script(line)
            return

        best_match = utils.match_word(command, self.commands.keys())
        script = getattr(self, self.commands[best_match])
        script(line)

        

            
            