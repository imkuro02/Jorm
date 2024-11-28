from actor import Actor
import utils

from config import DamageType, ItemType, ActorStatusType, StatType

from player_only_functions.commands import one_letter_commands, commands
from player_only_functions.movement import command_flee, command_go
from player_only_functions.checks import *
from player_only_functions.emotes import command_say

from player_only_functions.combat import (
    command_fight, command_pass_turn, 
    command_use, command_rest
)

from player_only_functions.look import command_look, get_entity

from player_only_functions.equip import (
    command_wear, command_remove, command_equipment, 
    inventory_equip, inventory_unequip
)

from player_only_functions.inventory import (
    raise_item, lower_item, inventory_add_item, inventory_remove_item, 
    command_keep, command_get, command_drop, command_inventory, get_item, 
    command_identify
)

from player_only_functions.character_sheet import (
    command_level_up, command_practice, command_skills, command_stats, 
    command_respec, command_affects, get_exp_needed_to_level
)

from player_only_functions.admin import (
    command_gain_exp, command_create_item, command_update_item, 
    command_load_item, command_export_item, command_help, prompt, 
    command_send_prompt
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
    command_help = command_help
    prompt = prompt 
    command_send_prompt = command_send_prompt

    def __init__(self, protocol, name, room):
        self.protocol = protocol
        super().__init__(name, room)
        self.last_line_sent = None

        if self.room != None:
            self.room.move_player(self)

        self.inventory = {}
        
    def sendLine(self, line, color = True):
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

        if command in one_letter_commands:
            script = getattr(self, one_letter_commands[command])
            script(line)
            return

        best_match = utils.match_word(command, commands.keys())
        script = getattr(self, commands[best_match])
        script(line)

        

            
            