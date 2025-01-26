from actors.player_only_functions.utils import get_entity, get_item
from actors.player_only_functions.movement import command_flee, command_go
from actors.player_only_functions.checks import *
from actors.player_only_functions.emotes import command_say, command_shout

from actors.player_only_functions.combat import (
    command_fight, command_pass_turn, 
    command_use, command_rest, command_party
)

from actors.player_only_functions.look import command_look

from actors.player_only_functions.equip import (
    command_equipment, inventory_equip, inventory_unequip
)

from actors.player_only_functions.inventory import (
    command_inventory, command_identify, command_keep, command_get, command_drop, command_trade
)

from actors.player_only_functions.character_sheet import (
    command_name_change,
    command_level_up, command_practice, command_skills, command_stats, 
    command_respec, command_affects, get_exp_needed_to_level
)

from actors.player_only_functions.admin import (
    command_gain_exp, command_teleport, command_online, command_kick, command_grant_admin,
    command_load_item, command_load_npcs, command_export, command_help, prompt, 
    command_send_prompt, command_reload_config
)

# one letter command mapper
# this sets priority for commands with same starting letter
one_letter_commands = {
    'i':    'inventory',
    'l':    'look',
    #'w':    'wear',
    #'r':    'remove',
    's':    'say',
    'g':    'go',
    'e':    'equipment',
    'f':    'fight',
    'p':    'prompt',
    'u':    'use',
    't':    'trade'
}

# command mapper
# all commands mapped to ONE word
commands = {
    # da rest
    'help':     'command_help',

    'say':      'command_say',
    'shout':    'command_shout',
    'go':       'command_go',
    #'setcall':  'command_recall_set',
    #'gocall':   'command_recall_go',
    'look':     'command_look',
    'trade':    'command_trade',
    
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
    #'wear':     'command_wear',
    'keep':     'command_keep',
    #'remove':   'command_remove',

    'use':      'command_use',
    'flee':     'command_flee',
    'fight':    'command_fight',
    'pass':     'command_pass_turn',
    'rest':     'command_rest',
    'party':    'command_party',
    
    'respec':   'command_respec',
    'prompt':   'command_send_prompt',

    'teleport': 'command_teleport',  
    'online':   'command_online',
    'kick':     'command_kick',
    'admin':    'command_grant_admin',

    'export': 'command_export',
    'item':   'command_load_item',
    'npcs':   'command_load_npcs',
    'mexp':    'command_gain_exp',
    'reload':   'command_reload_config'
}

