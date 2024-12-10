from actors.player_only_functions.utils import get_entity, get_item
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
    command_name_change,
    command_level_up, command_practice, command_skills, command_stats, 
    command_respec, command_affects, get_exp_needed_to_level
)

from actors.player_only_functions.admin import (
    command_gain_exp, command_create_item, command_update_item, 
    command_load_item, command_export_item, command_help, prompt, 
    command_send_prompt, command_debug
)

# one letter command mapper
# this sets priority for commands with same starting letter
one_letter_commands = {
    'i':    'inventory',
    'l':    'look',
    'w':    'wear',
    'r':    'remove',
    's':    'say',
    'g':    'go',
    'e':    'equipment',
    'f':    'fight',
    'p':    'prompt'
}

# command mapper
# all commands mapped to ONE word
commands = {
    # da rest
    'help':     'command_help',

    'say':      'command_say',
    'go':       'command_go',
    'look':     'command_look',
    
    'level':    'command_level_up',
    'practice': 'command_practice',

    #'name':     'command_name_change',
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
    'pass':     'command_pass_turn',
    'rest':     'command_rest',
    
    'respec':   'command_respec',
    'prompt':   'command_send_prompt',

    'minew':    'command_create_item',
    'miupdate': 'command_update_item',
    'miexport': 'command_export_item',
    'miload':   'command_load_item',
    'mexp':     'command_gain_exp',
    'midebug':  'command_debug'
}

