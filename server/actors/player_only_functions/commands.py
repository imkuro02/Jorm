from actors.player_only_functions.utils import get_actor, get_item
from actors.player_only_functions.movement import command_flee, command_go
from actors.player_only_functions.checks import *
from actors.player_only_functions.emotes import command_say, command_shout, command_roll, command_emote
from actors.player_only_functions.talk import command_talk

from actors.player_only_functions.combat import (
    command_fight, command_pass_turn, 
    command_use, command_use_try, command_rest, rest_set, rest_now, rest_now_request, command_party
)

from actors.player_only_functions.charging_mini_game import (
    command_charging_mini_game_toggle
)

from actors.player_only_functions.look import command_look, command_map, new_room_look, command_scan, get_nearby_rooms

from actors.player_only_functions.equip import (
    command_equipment, inventory_equip, inventory_unequip
)

from actors.player_only_functions.inventory import (
    command_inventory, command_identify, command_keep, command_get, command_drop, command_trade, command_split, command_sort, raise_item, lower_item, command_craft
)

from actors.player_only_functions.character_sheet import (
    command_level_up, command_practice, command_skills, command_stats, 
    command_respec, command_affects, get_exp_needed_to_level
)

from actors.player_only_functions.admin import (
    command_gain_exp, command_teleport, command_online, command_kick, command_grant_admin, command_show_ref_all,
    command_load_item, command_load_npcs, command_export, command_help, command_ranks,
    command_send_prompt, command_reload_config, command_lore, command_quest, command_bonus,
    command_kill, command_sethp, command_history, command_get_time, command_set_time,
)

from actors.player_only_functions.settings import (
    command_settings
)

shortcuts_to_commands = {
    'n':    'go north',
    'e':    'go east',
    's':    'go south',
    'w':    'go west',
    'u':    'go up',
    'd':    'go down'
}

# one letter command mapper
# this sets priority for commands with same starting letter
one_letter_commands = {
    'i':    'inventory',
    'l':    'look',
    #'w':    'wear',
    #'r':    'remove',
    's':    'say',
    'g':    'go',
    'eq':   'equipment',
    'f':    'fight',
    'p':    'prompt',
    'u':    'use',
    't':    'trade',
}

# command mapper
# all commands mapped to ONE word
commands = {
    # da rest
    'talk':     'command_talk',
    'bonus':    'command_bonus',
    
    'quest':    'command_quest',
    'help':     'command_help',
    'history':  'command_history',
    'ranks':    'command_ranks',
    'say':      'command_say',
    'shout':    'command_shout',
    'roll':     'command_roll',
    
    
    'go':       'command_go',
    #'setcall':  'command_recall_set',
    #'gocall':   'command_recall_go',
    'look':     'command_look',
    'scan':     'command_scan',
    'map':      'command_map',
    'lore':     'command_lore',
    'trade':    'command_trade',

    'emote':    'command_emote',
    
    'level':    'command_level_up',
    'practice': 'command_practice',

    #'name':     'command_name_change',
    'stats':    'command_stats',
    'equipment':'command_equipment',
    'inventory':'command_inventory',
    'sort':     'command_sort',
    'split':    'command_split',
    'craft':    'command_craft',
    'skills':   'command_skills',
    'affects':  'command_affects',
    

    'identify': 'command_identify',
    'get':      'command_get',
    'drop':     'command_drop',
    #'wear':     'command_wear',
    'keep':     'command_keep',
    #'remove':   'command_remove',

    'use':      'command_use',
    'try':      'command_use_try',
    'flee':     'command_flee',
    'fight':    'command_fight',
    #'target':   'command_target',
    'pass':     'command_pass_turn',
    'rest':     'command_rest',
    'party':    'command_party',
    
    'respec':   'command_respec',
    'prompt':   'command_send_prompt',

    'settings': 'command_settings',

    'time':     'command_get_time',
    '_timeset': 'command_set_time',

    'pray':     'command_charging_mini_game_toggle',

    '_teleport': 'command_teleport',  
    'online':   'command_online',
    '_kick':     'command_kick',
    '_admin':    'command_grant_admin',
    '_refs':    'command_show_ref_all',

    '_dict':        'command_export',
    '_item':     'command_load_item',
    '_npcs':     'command_load_npcs',
    '_mexp':     'command_gain_exp',
    '_reload':   'command_reload_config',
    '_kill':     'command_kill',
    
    '_sethp':    'command_sethp'

    
}

'''
ALL_COMMANDS = []

for i in commands:
    ALL_COMMANDS.append(i)    
for i in one_letter_commands: 
    ALL_COMMANDS.append(i)  
for i in shortcuts_to_commands:
    ALL_COMMANDS.append(i)  

import actors.player_only_functions.settings
actors.player_only_functions.settings.BANNED_ALIASES = ALL_COMMANDS
'''

translations = {
    'talk to ':          'talk ',
    'talk with':         'talk ',
    'speak':             'talk ',
    'speak to':          'talk ',
    'speak with':        'talk ',
    
    'pick up ':          'get ',
    'pick up item ':     'get ',
    'pick up items ':    'get ',

    'take ':             'get ',
    'take item ':        'get ',
    'take items ':       'get ',

    'get item ':         'get ',
    'get items ':        'get ',

    'leave party':       'party leave',
    'create party':      'party create',

    'wear ':             'equipment ',
    'unwear ':           'equipment ',
    'remove ':           'equipment ',
    'wield':             'equipment ',
    'take off':          'equipment ',

    'go to ':            'go ',
    'go in ':            'go ',
    'enter ':            'go ',
    'recall':            'rest now',
    'recall set':        'rest set',

    'north':             'go north',
    'east':              'go east',
    'south':             'go south',
    'west':              'go west',
    'up':                'go up',
    'down':              'go down',

    # EMOTES
    'wave at ':         'emote wave ',
    'wave':             'emote wave',

    'sing to ':         'emote sing ',
    'sing with ':       'emote sing_with ',
    'sing':             'emote sing',

    'dance with ':      'emote dance ',
    'dance':            'emote dance',

    'laugh at ':        'emote laugh_at ',
    'laugh with ':      'emote laugh_with ',
    'laugh':            'emote laugh',

    'spit on ':         'emote spit ',
    'spit at ':         'emote spit ',
    'spit':             'emote spit',

    'smile at ':        'emote smile ',
    'smile':            'emote smile',

    'hug':              'emote hug',
    
    'nod at ':          'emote nod ',
    'nod':              'emote nod',

    'shrug at ':        'emote shrug ',
    'shrug':            'emote shrug',

    'facepalm at':      'emote facepalm ',
    'facepalm':         'emote facepalm',

    'applaud':          'emote applaud',
    
    'point at ':        'emote point ',
    'point':            'emote point',

    'SEX SFDSFDSFDSF':  'dsdadsad',

    'score': 'stats',
    'who': 'online'
    
    
}