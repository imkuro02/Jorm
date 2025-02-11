import pandas as pd
from math import isnan
file_path = 'configuration/config.ods'
SHEET = {}

# ORDER MATTERS
SHEET['use_perspectives'] =    pd.read_excel(file_path, sheet_name = 'use_perspectives').to_dict(orient='dict')

SHEET['items_consumable'] =    pd.read_excel(file_path, sheet_name = 'items_consumable').to_dict(orient='dict')

SHEET['skill_script_values'] = pd.read_excel(file_path, sheet_name = 'skill_script_values').to_dict(orient='dict')
SHEET['skills'] =              pd.read_excel(file_path, sheet_name = 'skills').to_dict(orient='dict')


SHEET['items_equipment'] =     pd.read_excel(file_path, sheet_name = 'items_equipment').to_dict(orient='dict')
SHEET['items_misc'] =          pd.read_excel(file_path, sheet_name = 'items_misc').to_dict(orient='dict')


SHEET['enemy_skills'] =        pd.read_excel(file_path, sheet_name = 'enemy_skills').to_dict(orient='dict')
SHEET['loot'] =                pd.read_excel(file_path, sheet_name = 'loot').to_dict(orient='dict')
SHEET['enemies'] =             pd.read_excel(file_path, sheet_name = 'enemies').to_dict(orient='dict')
SHEET['enemy_combat_loop'] =   pd.read_excel(file_path, sheet_name = 'enemy_combat_loop').to_dict(orient='dict')

def str_with_newlines(s):
    s = s.replace('#END#','\n')
    return s

def load():
    SKILL_SCRIPT_VALUES = {}
    for row in SHEET['skill_script_values']:
        x = SHEET['skill_script_values']
        for index in range(0,len(x[row])):
            d_vals = {
                x['value_name'][index]: [
                    x['value0'][index],
                    x['value1'][index], 
                    x['value2'][index], 
                    x['value3'][index], 
                    x['value4'][index], 
                    x['value5'][index], 
                    x['value6'][index], 
                    x['value7'][index], 
                    x['value8'][index], 
                    x['value9'][index]
                ]
            }

            tmp = d_vals[x['value_name'][index]]
            d_vals = { x['value_name'][index]: [] }
            # convert values that are supposed to be displayed as % to float
            # also remove any "NaN" values
            for i in tmp:
                if isnan(i):
                    continue
                if x['value_name'][index] in ['chance','damage',]:
                    i = float(i)
                else:
                    i = int(i)
                d_vals[x['value_name'][index]].append(i)

            if x['skill_id'][index] in SKILL_SCRIPT_VALUES:
                # concate the previous dict with new a new value
                SKILL_SCRIPT_VALUES[x['skill_id'][index]] = SKILL_SCRIPT_VALUES[x['skill_id'][index]] | d_vals
            else:
                # create a fresh dict
                SKILL_SCRIPT_VALUES[x['skill_id'][index]] = {
                    x['value_name'][index]:        d_vals
                }

    

    
    USE_PERSPECTIVES = {}
    for row in SHEET['use_perspectives']:
        x = SHEET['use_perspectives']
        for index in range(0,len(x[row])):
            if x['use_case_id'][index] in USE_PERSPECTIVES:
                # concate the previous dict with new a new value
                USE_PERSPECTIVES[x['use_case_id'][index]] = USE_PERSPECTIVES[x['use_case_id'][index]] | {x['key'][index]: x['value'][index] }
            else:
                # create a fresh dict
                USE_PERSPECTIVES[x['use_case_id'][index]] = {
                    'use_case_name':        x['use_case_name'][index],
                    x['key'][index]:        x['value'][index] 
                }

    SKILLS = {}
    for row in SHEET['skills']:
        x = SHEET['skills']
        for index in range(0, len(x[row])):

            SKILLS[x['skill_id'][index]] = {
                'skill_id':                 x['skill_id'][index],
                'name':                     x['name'][index],
                'description':              str_with_newlines(x['description'][index]),
                'script_to_run':            x['script_to_run'][index],
                'target_others_is_valid':   bool(x['target_others_is_valid'][index]),
                'target_self_is_valid':     bool(x['target_self_is_valid'][index]),
                'must_be_fighting':         bool(x['must_be_fighting'][index]),
                'can_be_practiced':         bool(x['can_be_practiced'][index]),
                'level_req':                x['level_req'][index],
                'use_perspectives':         USE_PERSPECTIVES[x['use_perspectives'][index]]
            }

    for skill in SKILLS:
        SKILLS[skill]['script_values'] = SKILL_SCRIPT_VALUES[skill]
    

    ITEMS = {}
    for row in SHEET['items_misc']:
        x = SHEET['items_misc']
        for index in range(0, len(x[row])):
            ITEMS[x['premade_id'][index]] = {
                'premade_id':       x['premade_id'][index],
                'name':             x['name'][index],
                'description':      str_with_newlines(x['description'][index]),
                'item_type':        'misc'
            }


    for row in SHEET['items_consumable']:
        x = SHEET['items_consumable']
        for index in range(0, len(x[row])):

            ITEMS[x['premade_id'][index]] = {
                'premade_id':       x['premade_id'][index],
                'name':             x['name'][index],
                'description':      str_with_newlines(x['description'][index]),
                'skills':           [x['skill'][index]],
                'use_perspectives': USE_PERSPECTIVES[x['use_perspectives'][index]],
                'item_type':        'consumable'
            }
    
    for row in SHEET['items_equipment']:
        x = SHEET['items_equipment']
        for index in range(0, len(x[row])):

            ITEMS[x['premade_id'][index]] = {
                'premade_id':   x['premade_id'][index],
                'name':         x['name'][index],
                'description':  str_with_newlines(x['description'][index]),
                'item_type':    'equipment',
                'slot':         x['slot'][index],
                'stats': {
                    'grit':     int(x['grit'][index]),
                    'hp_max':   int(x['hp_max'][index]),
                    'mp_max':   int(x['mp_max'][index]),
                    'armor':    int(x['armor'][index]),
                    'marmor':   int(x['marmor'][index]),
                    'flow':     int(x['flow'][index]),
                    'mind':     int(x['mind'][index]),
                    'soul':     int(x['soul'][index])
                },
                'requirements': {
                    'lvl':      int(x['lvl'][index]),
                    'hp_max':   int(x['rhp_max'][index]),
                    'mp_max':   int(x['rmp_max'][index]),
                    'armor':    int(x['rarmor'][index]),
                    'marmor':   int(x['rmarmor'][index]),
                    'grit':     int(x['rgrit'][index]),
                    'flow':     int(x['rflow'][index]),
                    'mind':     int(x['rmind'][index]),
                    'soul':     int(x['rsoul'][index])
                }
            }
        
        ENEMIES = {}
        for row in SHEET['enemies']:
            x = SHEET['enemies']
            for index in range(0, len(x[row])):
                ENEMIES[x['enemy_id'][index]] = {
                    'enemy_id':     x['enemy_id'][index],
                    'name':         x['name'][index],
                    'description':  x['description'][index],
                    'stats': {
                        'grit':     int(x['grit'][index]),
                        'hp':       int(x['hp_max'][index]),
                        'mp':       int(x['mp_max'][index]),
                        'armor':    int(x['armor'][index]),
                        'marmor':   int(x['marmor'][index]),
                        'flow':     int(x['flow'][index]),
                        'mind':     int(x['mind'][index]),
                        'soul':     int(x['soul'][index]),
                        'exp':      int(x['exp'][index]),
                        'lvl':      int(x['lvl'][index])
                    },
                    'skills': {},       # EMPTY DICT TO STORE SKILLS
                    'loot': {},         # EMPTY DICT TO STORE LOOT
                    'combat_loop': {}   # EMPTY DICT TO STORE COMBAT LOOP
                }

        # ADD ENEMY LOOT
        LOOT = {}
        for row in SHEET['loot']:
            x = SHEET['loot']
            for index in range(0,len(x[row])):
                d_vals = {
                    x['item_id'][index]: float(x['drop_rate'][index])
                }

                if x['enemy_id'][index] in LOOT:
                    # concate the previous dict with new a new value
                    LOOT[x['enemy_id'][index]] = LOOT[x['enemy_id'][index]] | d_vals
                else:
                    # create a fresh dict
                    LOOT[x['enemy_id'][index]] = {
                        x['item_id'][index]: d_vals
                    }

        for loot_table in LOOT:
            ENEMIES[loot_table]['loot'] = LOOT[loot_table]

        # ADD ENEMY SKILLS
        ENEMY_SKILLS = {}
        for row in SHEET['enemy_skills']:
            x = SHEET['enemy_skills']
            for index in range(0,len(x[row])):
                d_vals = {
                    x['skill_id'][index]: int(x['practice'][index])
                }

                if x['enemy_id'][index] in ENEMY_SKILLS:
                    # concate the previous dict with new a new value
                    ENEMY_SKILLS[x['enemy_id'][index]] = ENEMY_SKILLS[x['enemy_id'][index]] | d_vals
                else:
                    # create a fresh dict
                    ENEMY_SKILLS[x['enemy_id'][index]] = {
                        x['skill_id'][index]: d_vals
                    }

        for enemy_id in ENEMY_SKILLS:
            ENEMIES[enemy_id]['skills'] = ENEMY_SKILLS[enemy_id]

        # ADD ENEMY COMBAT LOOP
        TEMP_ENEMY_COMBAT_LOOP = {}
        for row in SHEET['enemy_combat_loop']:
            x = SHEET['enemy_combat_loop']
            for index in range(0,len(x[row])):
                d_vals = { 
                    x['order'][index]: {
                        'target':   str(x['target'][index]),
                        'skill':    str(x['skill_id'][index])
                    }
                }

                if x['enemy_id'][index] in TEMP_ENEMY_COMBAT_LOOP:
                    # concate the previous dict with new a new value
                    TEMP_ENEMY_COMBAT_LOOP[x['enemy_id'][index]] = TEMP_ENEMY_COMBAT_LOOP[x['enemy_id'][index]] | d_vals
                else:
                    # create a fresh dict
                    TEMP_ENEMY_COMBAT_LOOP[x['enemy_id'][index]] = {
                        x['order'][index]: d_vals
                    }

        ENEMY_COMBAT_LOOP = {}
        for loop in TEMP_ENEMY_COMBAT_LOOP:
            ENEMY_COMBAT_LOOP[loop] = []
            for i in dict(sorted(TEMP_ENEMY_COMBAT_LOOP[loop].items())):
                ENEMY_COMBAT_LOOP[loop].append(TEMP_ENEMY_COMBAT_LOOP[loop][i])

        for enemy_id in ENEMY_COMBAT_LOOP:
            ENEMIES[enemy_id]['combat_loop'] = ENEMY_COMBAT_LOOP[enemy_id]

        # PACK IT ALL UP
        whole_dict = {
            'enemies': ENEMIES,
            'skills': SKILLS,
            'items': ITEMS,
        }
        return whole_dict
    
if __name__ == '__main__':
    print(load())
    