import yaml
from enum import Enum, auto
import configuration.map.map_loader
import csv
import os

class ItemType:
    MISC = 'misc'
    EQUIPMENT = 'equipment'
    CONSUMABLE = 'consumable'
    ERROR = 'error_item'
    name = {
        MISC: 'Misc',
        EQUIPMENT: 'Equipment',
        CONSUMABLE: 'Consumable',
        ERROR: 'Error Item'
    }
    
class AffType:
    BASIC = 1
    DOT1 = 2
    DOT2 = 3
    HEALAMP = 4
    POWERUP = 5
    ETHEREAL = 6
    REFLECTDAMAGE = 7
    STUNNED = 8

class DamageType:
    PHYSICAL = 1
    MAGICAL = 2
    HEALING = 3
    PURE = 4
    CANCELLED = 5 # Cancels all damage

class ActorStatusType:
    NORMAL = 'Normal'
    FIGHTING = 'Fighting'
    DEAD = 'Dead'

class EquipmentSlotType:
    HEAD =      'head'
    BODY =      'body'
    WEAPON =    'weapon'
    TRINKET =   'trinket'
    RELIC   =   'relic'
    name = {
        HEAD: 'Head',
        BODY: 'Body',
        WEAPON: 'Weapon',
        TRINKET: 'Trinket',
        RELIC:   'Relic'
    }
    '''
    NECK =      'neck'
    CHEST =     'chest'
    HANDS =     'hands'
    BELT =      'belt'
    LEGS =      'legs'
    FEET =      'feet'
    TRINKET =   'trinket'
    PRIMARY =   'primary'
    SECONDARY = 'secondary'
    name = {
        HEAD:      'Head',
        NECK:      'Neck',
        CHEST:     'Chest',
        HANDS:     'Hands',
        BELT:      'Belt',
        LEGS:      'Legs',
        FEET:      'Feet',
        TRINKET:   'Trinket',
        PRIMARY:   'Primary',
        SECONDARY: 'Secondary'
    }
    '''

class StatType:
    HPMAX =     'hp_max'
    MPMAX =     'mp_max'
    HP =        'hp'
    MP =        'mp'
    GRIT =      'grit'
    FLOW =      'flow'
    MIND =      'mind'
    SOUL =      'soul'
    ARMOR =     'armor'
    MARMOR =    'marmor'
    EXP =       'exp'
    LVL =       'lvl'
    PP =        'pp'

    # not saved in db
    THREAT =    'threat'
    
    name = {
        HPMAX:  'Max Health',
        MPMAX:  'Max Magicka',
        HP:     'Health',
        MP:     'Magicka',
        GRIT:   'Grit',
        FLOW:   'Flow',
        MIND:   'Mind',
        SOUL:   'Soul',
        ARMOR:  'Armor',
        MARMOR: 'Marmor',
        EXP:    'Experience',
        LVL:    'Level',
        PP:     'Practice Points',

        # not saved in db
        THREAT: 'Threat'
    }

SKILLS = {}
ITEMS = {}
ENEMIES = {}
WORLD = {}
LOOT = {}
CONSUMABLE_USE_PERSPECTIVES = {}
SPLASH_SCREENS = {}

def load():
    from configuration.splashscreens.splash import splash_screens
    SPLASH_SCREENS['screens'] = splash_screens

    #SKILLS = {}
    SKILLS_DIRECTORY = 'configuration/skills/'
    for root, dirs, files in os.walk(SKILLS_DIRECTORY):
        for filename in files:
            if filename.endswith('.yaml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    ALL_SKILLS = yaml.safe_load(file)
                    for i in ALL_SKILLS:
                        if 'template' not in i:
                            SKILLS[i] = ALL_SKILLS[i]

    #SKILLS = {}
    LOOT_DIRECTORY = 'configuration/loot_tables/'
    for root, dirs, files in os.walk(LOOT_DIRECTORY):
        for filename in files:
            if filename.endswith('.yaml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    ALL_LOOT = yaml.safe_load(file)
                    for i in ALL_LOOT:
                        if 'template' not in i:
                            LOOT[i] = ALL_LOOT[i]

    #ITEMS = {}
    with open("configuration/items/items.yaml", "r") as file:
        ITEMS_UNFILTERED = yaml.safe_load(file)
        for i in ITEMS_UNFILTERED:
            if 'template' not in i:
                ITEMS[i] = ITEMS_UNFILTERED[i]

    # Open and read the CSV file
    with open('configuration/items/equipment.csv', mode="r") as file:
        reader = csv.DictReader(file)  # Reads data as dictionaries
        items = [row for row in reader]  # Store all rows in a list


    # Print the parsed data
    for _item in items:
        #print(item)
        if _item['premade_id'] == '': 
            continue

        item = {
            'premade_id': _item['premade_id'],
            'name': _item['name'],
            'description': _item['desc'],
            'item_type': 'equipment',
            'slot': _item['slot'],
            'stats': {
                'grit':     int(_item['grit']),
                'hp_max':   int(_item['hp_max']),
                'mp_max':   int(_item['mp_max']),
                'armor':    int(_item['armor']),
                'marmor':   int(_item['marmor']),
                'flow':     int(_item['flow']),
                'mind':     int(_item['mind']),
                'soul':     int(_item['soul'])
            },
            'requirements': {
                'lvl':      int(_item['lvl']),
                'hp_max':   int(_item['rhp_max']),
                'mp_max':   int(_item['rmp_max']),
                'armor':    int(_item['rarmor']),
                'marmor':   int(_item['rmarmor']),
                'grit':     int(_item['rgrit']),
                'flow':     int(_item['rflow']),
                'mind':     int(_item['rmind']),
                'soul':     int(_item['rsoul'])
            }
        }
        ITEMS[_item['premade_id']] = item

    #ENEMIES = {}
    ENEMIES_DIRECTORY = 'configuration/enemies/'
    for root, dirs, files in os.walk(ENEMIES_DIRECTORY):
        for filename in files:
            if filename.endswith('.yaml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    ALL_ENEMIES = yaml.safe_load(file)
                    for i in ALL_ENEMIES:
                        if 'template' not in i:
                            ENEMIES[i] = ALL_ENEMIES[i]

    '''
    #WORLD = {}
    with open("configuration/world.yaml", "r") as file:
        WORLD_UNFILTERED = yaml.safe_load(file)
        for i in WORLD_UNFILTERED:
            if 'template' not in i:
                WORLD[i] = WORLD_UNFILTERED[i]
    '''
    WORLD['world'] = configuration.map.map_loader.load_map()
    #print(WORLD)

    with open("configuration/items/consumable_use_perspectives.yaml", "r") as file:
        CONSUMABLE_USE_PERSPECTIVES_UNFILTERED = yaml.safe_load(file)
        for i in CONSUMABLE_USE_PERSPECTIVES_UNFILTERED:
            if 'template' not in i:
                CONSUMABLE_USE_PERSPECTIVES[i] = CONSUMABLE_USE_PERSPECTIVES_UNFILTERED[i]


    print('reloaded')

           

