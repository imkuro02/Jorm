import pandas as pd
from math import isnan
from pandas_ods_reader import read_ods

#SHEET = {}

import time
import json
import hashlib


def str_with_newlines(s):
    if s == None:
        s = 'None'
        return s
    s = s.replace('#END#','\n')
    return s

def read_from_ods_file():
    file_path = 'configuration/config.ods'
    SHEET = {}
    # ORDER MATTERS
    start = time.time()
    SHEET['use_perspectives'] =    read_ods(file_path, 'use_perspectives')
    SHEET['items_consumable'] =    read_ods(file_path, 'items_consumable')
    SHEET['skill_script_values'] = pd.read_excel(file_path, sheet_name = 'skill_script_values').to_dict(orient='dict')
    SHEET['skills'] =              read_ods(file_path, 'skills')
    SHEET['items_equipment'] =     read_ods(file_path, 'items_equipment')
    SHEET['items_misc'] =          read_ods(file_path, 'items_misc')
    SHEET['items_scenery'] =       read_ods(file_path, 'items_scenery')
    SHEET['enemy_skills'] =        read_ods(file_path, 'enemy_skills')
    SHEET['loot'] =                read_ods(file_path, 'loot')
    SHEET['enemies'] =             read_ods(file_path, 'enemies')
    SHEET['crafting_recipes'] =    read_ods(file_path, 'crafting_recipes')
    #SHEET['enemy_combat_loop'] =   read_ods(file_path, 'enemy_combat_loop')
    end = time.time()
    print(end - start,'LOADING OF CONFIG.ODS')

    return SHEET

def configure_skill_script_values(SHEET):
    start = time.time()
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
                if type(i).__name__ == 'float':
                    if isnan(i):
                        continue
                i = str(i)
                if ',' in i:
                    i = float(i.replace(',','.'))
                else:
                    i = float(i)

                if isnan(i):
                    continue
                if x['value_name'][index] in ['crit','bonus']:
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

    end = time.time()
    print(end - start,'SKILL_SCRIPT_VALUES')
    return SKILL_SCRIPT_VALUES

def configure_USE_PERSPECTIVES(SHEET):
    start = time.time()
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
    end = time.time()
    print(end - start,'USE_PERSPECTIVES')   
    return USE_PERSPECTIVES

def configure_SKILLS(SHEET, USE_PERSPECTIVES, SKILL_SCRIPT_VALUES):
    start = time.time()
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
                'target_item_is_valid':     bool(x['target_item_is_valid'][index]),
                'target_self_is_valid':     bool(x['target_self_is_valid'][index]),
                'must_be_fighting':         bool(x['must_be_fighting'][index]),
                'can_be_practiced':         bool(x['can_be_practiced'][index]),
                'practice_cost':            int(x['practice_cost'][index]),
                'level_req':                x['level_req'][index],
                'use_perspectives':         USE_PERSPECTIVES[x['use_perspectives'][index]],
                #'weight_low_hp_ally':       x['weight_low_hp_ally'][index],
                #'weight_high_hp_ally':      x['weight_high_hp_ally'][index],
                #'weight_low_hp_enemy':      x['weight_low_hp_enemy'][index],
                #'weight_high_hp_enemy':     x['weight_high_hp_enemy'][index],
                'is_offensive':             x['is_offensive'][index]
            }

    for skill in SKILLS:
        SKILLS[skill]['script_values'] = SKILL_SCRIPT_VALUES[skill]
    end = time.time()
    print(end - start,'SKILL')
    return SKILLS

def configure_ITEMS(SHEET, USE_PERSPECTIVES):
    start = time.time()
    ITEMS = {}
    for row in SHEET['items_misc']:
        x = SHEET['items_misc']
        for index in range(0, len(x[row])):
            ITEMS[x['premade_id'][index]] = {
                'premade_id':       x['premade_id'][index],
                'name':             x['name'][index],
                'description':      str_with_newlines(x['description'][index]),
                'description_room': None if str(x['description_room'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['description_room'][index],
                'invisible':        x['invisible'][index],
                'ambience':          None if str(x['ambience'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['ambience'][index],
                'ambience_sfx':     None if str(x['ambience_sfx'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['ambience_sfx'][index],
                'can_pick_up':  bool(x['can_pick_up'][index]),
                'item_type':        'misc'
            }

    '''
    for row in SHEET['items_scenery']:
        x = SHEET['items_scenery']
        for index in range(0, len(x[row])):
            ITEMS[x['premade_id'][index]] = {
                'premade_id':       x['premade_id'][index],
                'name':             x['name'][index],
                'description':      str_with_newlines(x['description'][index]),
                'description_room': None if str(x['description_room'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['description_room'][index],
                'invisible':        x['invisible'][index],
                'item_type':        'scenery',
                'ambience':          None if str(x['ambience'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['ambience'][index],
                'ambience_sfx':     None if str(x['ambience_sfx'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['ambience_sfx'][index],
                'can_pick_up':      bool(x['can_pick_up'][index]),
                'random_drop_lvl': int(x['random_drop_lvl'][index])
            }
    '''


    for row in SHEET['items_consumable']:
        x = SHEET['items_consumable']
        for index in range(0, len(x[row])):

            ITEMS[x['premade_id'][index]] = {
                'premade_id':       x['premade_id'][index],
                'name':             x['name'][index],
                'description':      str_with_newlines(x['description'][index]),
                'description_room': None if str(x['description_room'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['description_room'][index],
                'invisible':        x['invisible'][index],
                'skills':           [x['skill'][index]],
                'use_perspectives': USE_PERSPECTIVES[x['use_perspectives'][index]],
                'item_type':        'consumable',
                'ambience':          None if str(x['ambience'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['ambience'][index],
                'ambience_sfx':     None if str(x['ambience_sfx'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['ambience_sfx'][index],
                'can_pick_up':  bool(x['can_pick_up'][index]),
                'random_drop_lvl': int(x['random_drop_lvl'][index])
                
            }
    
    for row in SHEET['items_equipment']:
        x = SHEET['items_equipment']
        for index in range(0, len(x[row])):
            ITEMS[x['premade_id'][index]] = {
                'premade_id':   x['premade_id'][index],
                'name':         x['name'][index],
                'description':  str_with_newlines(x['description'][index]),
                'description_room': None if str(x['description_room'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['description_room'][index],
                'invisible':        x['invisible'][index],
                'item_type':    'equipment',
                'ambience':          None if str(x['ambience'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['ambience'][index],
                'ambience_sfx':     None if str(x['ambience_sfx'][index]).strip() in ['0', '0.0', '', 'False', 'false'] else x['ambience_sfx'][index],
                'can_pick_up':  bool(x['can_pick_up'][index]),
                'slot':         x['slot'][index],
                'bonuses':      x['bonuses'][index],
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
                },
                'random_drop_lvl': int(x['random_drop_lvl'][index])
            }


    for i in ITEMS:
        ITEMS[i]['crafting_recipe_ingredients'] = []
        ITEMS[i]['crafting_ingredient_for'] = []

    for row in SHEET['crafting_recipes']:
        x = SHEET['crafting_recipes']
        
        for index in range(0, len(x[row])):

            ingredients = {}
            premade_id = x['premade_id'][index]
            
            for i in range(0,4):
                i += 1
                #print(i)
                
                ingredient = str(x[f'ingredient_{i}'][index])
                quantity = int(x[f'quantity_{i}'][index])

                if ingredient in '0.0 0'.split(' '):
                    continue

                ingredients[ingredient] = quantity
                #print(f'ingredient_{i}',ingredient)
                if premade_id not in ITEMS[ingredient]['crafting_ingredient_for']:
                    ITEMS[ingredient]['crafting_ingredient_for'].append(premade_id)
                
            
            if ingredients not in ITEMS[premade_id]['crafting_recipe_ingredients']:
                ITEMS[premade_id]['crafting_recipe_ingredients'].append(ingredients)
                #print(f'craft {premade_id} ingredients: ',ingredients)

    


    end = time.time()
    print(end - start,'ITEMS')
    return ITEMS

def configure_ENEMIES(SHEET, ITEMS):
    start = time.time()
    ENEMIES = {}
    for row in SHEET['enemies']:
        x = SHEET['enemies']
        
        for index in range(0, len(x[row])):
            
            ENEMIES[x['npc_id'][index]] = {
                'npc_id':       x['npc_id'][index],
                'ai':           x['ai'][index],
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
                'include_in_daily_quests': bool(x['include_in_daily_quests'][index]),
                'skills': {},       # EMPTY DICT TO STORE SKILLS
                'loot': {},         # EMPTY DICT TO STORE LOOT
                'combat_loop': {},  # EMPTY DICT TO STORE COMBAT LOOP
                'can_start_fights': bool(x['can_start_fights'][index]),
                'dont_join_fights':  bool(x['dont_join_fights'][index]),  
            }

    end = time.time()
    print(end - start,'ENEMIES')

    start = time.time()
    # ADD ENEMY LOOT
    LOOT = {}
    for row in SHEET['loot']:
        x = SHEET['loot']
        for index in range(0,len(x[row])):
            d_vals = {
                x['item_id'][index]: int(x['drop_rate'][index])
            }

            if x['npc_id'][index] in LOOT:
                # concate the previous dict with new a new value
                LOOT[x['npc_id'][index]] = LOOT[x['npc_id'][index]] | d_vals
            else:
                # create a fresh dict
                LOOT[x['npc_id'][index]] = {
                    x['item_id'][index]: d_vals
                }

    for loot_table in LOOT:
        ENEMIES[loot_table]['loot'] = LOOT[loot_table]

    for e in ENEMIES:
        loot = {}
        for i in ITEMS:
            if 'random_drop_lvl' in ITEMS[i]:
                if ITEMS[i]['random_drop_lvl'] == 0:
                    continue

                highest_enemy_stat = {'stat':'grit','val':-10000}
                for s in ['grit','flow','mind','soul']:
                    if ENEMIES[e]['stats'][s] > highest_enemy_stat['val']:
                        highest_enemy_stat = {'stat':s,'val':ENEMIES[e]['stats'][s]}
                    
                if 'stats' in ITEMS[i]:
                    highest_item_stat = {'stat':'grit','val':-10000}
                    for s in ['grit','flow','mind','soul']:
                        if ITEMS[i]['stats'][s] + ITEMS[i]['requirements'][s] > highest_item_stat['val']:
                            highest_item_stat = {'stat':s,'val': ITEMS[i]['stats'][s] + ITEMS[i]['requirements'][s]} 
                    if highest_item_stat['stat'] != highest_enemy_stat['stat']:
                        
                        continue
                #if 'stats' in ITEMS[i]: 
                #   print(e, highest_item_stat['stat'],i , highest_enemy_stat['stat'])
                match abs(ITEMS[i]['random_drop_lvl'] - ENEMIES[e]['stats']['lvl']):
                    case 0:
                        loot[i] = 10
                    case 1:
                        loot[i] = 20
                    case 2:
                        loot[i] = 30
                    case 3:
                        loot[i] = 100
                    case 5:
                        loot[i] = 200
                    case 6:
                        loot[i] = 300
                    case _:
                        continue

                loot[i] = int(loot[i] * (1+ITEMS[i]['random_drop_lvl']*1+ENEMIES[e]['stats']['lvl']))

                if i not in ENEMIES[e]['loot']:
                    ENEMIES[e]['loot'][i] = int(loot[i])

    end = time.time()
    print(end - start,'LOOT')


    start = time.time()
    # ADD ENEMY SKILLS
    ENEMY_SKILLS = {}
    for row in SHEET['enemy_skills']:
        x = SHEET['enemy_skills']
        for index in range(0,len(x[row])):
            d_vals = {
                x['skill_id'][index]: int(x['practice'][index])
            }

            if x['npc_id'][index] in ENEMY_SKILLS:
                # concate the previous dict with new a new value
                ENEMY_SKILLS[x['npc_id'][index]] = ENEMY_SKILLS[x['npc_id'][index]] | d_vals
            else:
                # create a fresh dict
                ENEMY_SKILLS[x['npc_id'][index]] = {
                    x['skill_id'][index]: d_vals
                }

    for npc_id in ENEMY_SKILLS:
        ENEMIES[npc_id]['skills'] = ENEMY_SKILLS[npc_id]
    
    end = time.time()
    print(end - start,'ENEMY_SKILLS')

    '''
    start = time.time()
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

            if x['npc_id'][index] in TEMP_ENEMY_COMBAT_LOOP:
                # concate the previous dict with new a new value
                TEMP_ENEMY_COMBAT_LOOP[x['npc_id'][index]] = TEMP_ENEMY_COMBAT_LOOP[x['npc_id'][index]] | d_vals
            else:
                # create a fresh dict
                TEMP_ENEMY_COMBAT_LOOP[x['npc_id'][index]] = {
                    x['order'][index]: d_vals
                }

    ENEMY_COMBAT_LOOP = {}
    for loop in TEMP_ENEMY_COMBAT_LOOP:
        ENEMY_COMBAT_LOOP[loop] = []
        for i in dict(sorted(TEMP_ENEMY_COMBAT_LOOP[loop].items())):
            ENEMY_COMBAT_LOOP[loop].append(TEMP_ENEMY_COMBAT_LOOP[loop][i])

    for npc_id in ENEMY_COMBAT_LOOP:
        ENEMIES[npc_id]['combat_loop'] = ENEMY_COMBAT_LOOP[npc_id]

    end = time.time()
    print(end - start,'ENEMY_COMBAT_LOOP')
    '''
    return ENEMIES

def load_from_excel():
    SHEET = read_from_ods_file()
    SKILL_SCRIPT_VALUES =     configure_skill_script_values(SHEET)
    USE_PERSPECTIVES =        configure_USE_PERSPECTIVES(SHEET)
    SKILLS =                  configure_SKILLS(SHEET, USE_PERSPECTIVES, SKILL_SCRIPT_VALUES)
    ITEMS =                   configure_ITEMS(SHEET, USE_PERSPECTIVES)
    ENEMIES =                 configure_ENEMIES(SHEET, ITEMS)
    
    # PACK IT ALL UP
    whole_dict = {
        'enemies': ENEMIES,
        'skills': SKILLS,
        'items': ITEMS,
    }

    return whole_dict

from pathlib import Path

def is_checksum_same():
    excel_checksum = get_checksum('configuration/config.ods', "sha256")
    json_checksum = None
    file_json = Path('configuration/config.json')
    print(f"Excel SHA-256: {excel_checksum}")

    data = {}
    if file_json.exists() and file_json.is_file():
        try:
            with open(file_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            print("JSON data successfully loaded")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    else:
        print("Json config file does not exist.")

    if data != {}:
        json_checksum = data['SHA-256']

    return json_checksum == excel_checksum
    


def load():
    data = {}
    file_json = 'configuration/config.json'
    if is_checksum_same():
        with open(file_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        excel_checksum = get_checksum('configuration/config.ods', "sha256")
        whole_dict = load_from_excel()
        data = {
            'SHA-256': excel_checksum,
            'enemies': whole_dict['enemies'],
            'skills': whole_dict['skills'],
            'items': whole_dict['items']
        }
        with open(file_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    return data

def get_checksum(file_path, algorithm='sha256'):
    hash_func = getattr(hashlib, algorithm)()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()

if __name__ == '__main__':
    load()
    