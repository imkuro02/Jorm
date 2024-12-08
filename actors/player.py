from actors.actor import Actor
import utils

from config import DamageType, ItemType, ActorStatusType, StatType

from actors.player_only_functions.utils import get_entity, get_item
from actors.player_only_functions.commands import one_letter_commands, commands
from actors.player_only_functions.movement import command_flee, command_go
from actors.player_only_functions.checks import *
from actors.player_only_functions.emotes import command_say

from actors.player_only_functions.combat import (
    command_fight, command_pass_turn, 
    command_use, command_rest
)

from actors.player_only_functions.look import command_look

from actors.player_only_functions.equip import (
    command_wear, command_remove, command_equipment, 
    inventory_equip, inventory_unequip
)

from actors.player_only_functions.inventory import (
    raise_item, lower_item, inventory_add_item, inventory_remove_item, 
    command_keep, command_get, command_drop, command_inventory, 
    command_identify
)

from actors.player_only_functions.character_sheet import (
    command_level_up, command_practice, command_skills, command_stats, 
    command_respec, command_affects, get_exp_needed_to_level
)

from actors.player_only_functions.admin import (
    command_gain_exp, command_create_item, command_update_item, 
    command_load_item, command_export_item, command_help, prompt, 
    command_send_prompt, command_debug
)

class Player(Actor):
    command_say = command_say

    command_look = command_look
    get_entity = get_entity

    command_flee = command_flee
    command_go = command_go

    command_fight = command_fight
    command_pass_turn = command_pass_turn 
    command_use = command_use
    command_rest = command_rest

    command_wear = command_wear
    command_remove = command_remove
    command_equipment = command_equipment
    inventory_equip = inventory_equip
    inventory_unequip = inventory_unequip

    inventory_add_item = inventory_add_item
    inventory_remove_item = inventory_remove_item
    command_keep = command_keep
    command_get = command_get
    command_drop = command_drop
    command_inventory = command_inventory
    get_item = get_item
    raise_item = raise_item
    lower_item = lower_item 
    command_identify = command_identify

    command_level_up = command_level_up
    command_practice = command_practice
    command_skills = command_skills
    command_stats = command_stats
    command_respec = command_respec
    command_affects = command_affects
    get_exp_needed_to_level = get_exp_needed_to_level

    command_gain_exp = command_gain_exp
    command_create_item = command_create_item
    command_update_item = command_update_item
    command_load_item = command_load_item
    command_export_item = command_export_item
    command_debug = command_debug
    command_help = command_help
    prompt = prompt 
    command_send_prompt = command_send_prompt

    def __init__(self, protocol, name, room, _id = None):
        self.protocol = protocol
        super().__init__(name, room, _id)
        self.last_line_sent = None
        self.last_command_used = None
        self.send_line_buffer = []

        if self.room != None:
            self.room.move_player(self, silent = True)

        self.inventory = {}
        
    def tick(self):
        # send buffer
        if self.factory.ticks_passed % 1 != 0:
            return
        if self.send_line_buffer == []:
            return
        line = self.send_line_buffer[0]
        self.protocol.transport.write(line.encode('utf-8'))
        self.send_line_buffer.pop(0)
        

    def sendLine(self, line, color = True):
        if color:
            line = utils.add_color(f'{line}\n')
        #lines = [char for char in line]
        lines = line.replace('\n','#SPLIT#\n').split('#SPLIT#')
        #lines = line.replace(' ','#SPLIT# ').split('#SPLIT#')
        for l in lines:
            self.send_line_buffer.append(l)
        

    def handle(self, line):
        # empty lines are handled as resend last line
        if not line: 
            line = self.last_line_sent
            if not line:
                return

        self.last_line_sent = line

        command = line.split()[0]
        line = " ".join(line.split()[1::]).strip()

        if command in one_letter_commands:
            script = getattr(self, commands[one_letter_commands[command]])
            self.last_command_used = one_letter_commands[command]
            script(line)
            return
        
        best_match, best_score = utils.match_word(command, commands.keys(), get_score = True)
        if best_score < 75:
            self.sendLine(f'You wrote "{command}" did you mean "{best_match}"?\nUse "help {best_match}" to learn more about this command.')
            return

        
        script = getattr(self, commands[best_match])
        self.last_command_used = best_match
        script(line)

        

            
            