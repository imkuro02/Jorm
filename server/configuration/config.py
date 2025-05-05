import yaml
from enum import Enum, auto
#import configuration.map.map_loader
import configuration.map.map_loader
import csv
import os
import configuration.read_from_excel as rfe

class StaticRooms:
    LOADING = 'overworld/loading'
    TUTORIAL = 'overworld/tutorial'

SkillScriptValuesToNames = {
    'levels':       'LEVEL',
    'damage':       'DAMAGE',
    # 'chance':       'CHANCE',
    'crit':         'CRIT',
    'hp_cost':      'HP-COST',
    'mp_cost':      'MP-COST',
    'duration':     'DURATION',
    'cooldown':     'COOLDOWN',
    'bonus':        'BONUS'
}

class IndentType:
    NONE = 'none'
    MINOR = 'minor'
    MAJOR = 'major'
    
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

class DamageType:
    PHYSICAL = 'physical'
    MAGICAL = 'magical'
    HEALING = 'healing'
    PURE = 'pure'
    CANCELLED = 'cancelled' # Cancels all damage

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

#data = rfe.load()
ITEMS = {}
ENEMIES = {}
SKILLS = {}
NPCS = {}
WORLD = {}
SPLASH_SCREENS = {}
LORE = {}
QUESTS = {}

def load_lore():
    LORE['enemies'] = {}
    LORE['items'] = {}
    LORE['items_name_to_id'] = {}
    LORE['rooms'] = {}
    LORE['skills'] = {}

    for i in WORLD['world']:
        LORE['rooms'][ WORLD['world'][i]['name'] ] = WORLD['world'][i]

    for i in ITEMS:
        LORE['items'][ITEMS[i]['name']]  = ITEMS[i]
        LORE['items_name_to_id'][ITEMS[i]['premade_id']]  = ITEMS[i]['name']

    for i in ENEMIES:
        LORE['enemies'][ENEMIES[i]['name']]  = ENEMIES[i]

    for i in SKILLS:
        LORE['skills'][SKILLS[i]['name']]  = SKILLS[i]

    return LORE 

def load():
    global QUESTS
    global LORE
    global ITEMS
    global ENEMIES
    global SKILLS  # Declare the global variables here
    data = rfe.load()
    for k in data['items']:
        ITEMS[k] = data['items'][k]
    for k in data['enemies']:
        ENEMIES[k] = data['enemies'][k]
    for k in data['skills']:
        SKILLS[k] = data['skills'][k]


    QUESTS_DIRECTORY = 'configuration/quests/'
    
    for root, dirs, files in os.walk(QUESTS_DIRECTORY):
        for filename in files:
            if filename.endswith('.yaml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    ALL_QUESTS = yaml.safe_load(file)
                    for i in ALL_QUESTS:
                        if 'template' not in i:
                            QUESTS[i] = ALL_QUESTS[i]

    #SKILLS = {}
    NPCS_DIRECTORY = 'configuration/npcs/'
    for root, dirs, files in os.walk(NPCS_DIRECTORY):
        for filename in files:
            if filename.endswith('.yaml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    ALL_NPCS = yaml.safe_load(file)
                    for i in ALL_NPCS:
                        if 'template' not in i:
                            NPCS[i] = ALL_NPCS[i]

    from configuration.splashscreens.splash import splash_screens
    SPLASH_SCREENS['screens'] = splash_screens

    WORLD['world'] = configuration.map.map_loader.load_map()
    #print(len(WORLD['world']))

    LORE = load_lore()

    print('reloaded')


           

