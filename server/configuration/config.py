import yaml
from enum import Enum, auto
#import configuration.map.map_loader
import configuration.map.map_loader
import csv
import os
import configuration.read_from_excel as rfe
import random

class Color:
    NORMAL =                '@normal'
    BACK =                  '@back' 
    ERROR =                 '@bgred'  

    GOOD =                  '@bgreen'
    BAD =                   '@bpurple'
    
    IMPORTANT =             '@yellow'
    TOOLTIP =               '@tip'
    DESCRIPTION =           '@cyan'

    NAME_ADMIN =            '@yellow'
    NAME_PLAYER =           '@bcyan'
    NAME_ENEMY =            '@bpurple'
    NAME_NPC =              '@byellow'

    NAME_ROOM_NORMAL =      '@bwhite'
    NAME_ROOM_SAFE =        '@bgreen'
    NAME_ROOM_INSTANCE =    '@bred'
    DESC_ROOM =             '@cyan'

    NAME_QUEST =            '@bgreen'
    DESC_QUEST =            '@cyan'

    MAP_PLAYER =            NAME_PLAYER
    MAP_IMPORTANT =         NORMAL
    MAP_NORMAL =            NORMAL
    MAP_WALL =              '@wall'
    MAP_ROOM =              '@yellow'
    MAP_PATH =              '@yellow'

    ITEM_KEEP =             '@red'
    ITEM_EQUIPPED =         '@green'
    ITEM_TRADING =          '@yellow'
    ITEM_NEW    =           '@yellow'

    DAMAGE_PURE =           '@byellow'
    DAMAGE_PHY =            '@bred'
    DAMAGE_MAG =            '@bcyan'
    DAMAGE_HEAL =           '@bgreen'

    #STAT_HP =               '@bred'
    #STAT_MP =               '@bcyan'
    #STAT_PHY_ARM =          '@red'
    #STAT_MAG_ARM =          '@bblue'
    #STAT_GRIT =             NORMAL
    #STAT_FLOW =             NORMAL
    #STAT_MIND =             NORMAL
    #STAT_SOUL =             NORMAL
    #STAT_EXPERIENCE =       NORMAL
    #STAT_PRACTICE_POINTS =  NORMAL
    #STAT_BAG_SPACE =        NORMAL

    
class MsgType:
    SAY = 'say'
    SHOUT = 'shout'
    COMBAT = 'combat'
    CHAT = 'chat'
    ALL = 'all'
    DEBUG = 'debug'
    
class Audio:
    PLAYER_DEATH = 'die1.wav'
    ENEMY_DEATH = 'die.wav'
    BUFF = 'buff.wav'
    WALK = 'walk1.wav'
    HURT = 'pot-hit.wav'
    ERROR = 'error.wav'
    ITEM_GET = 'item_get.mp3'
    ITEM_DROP = 'item_drop.mp3'
    FIREPLACE = 'fireplace.wav'
    def walk():
        return random.choice(['walk1.wav','walk2.wav','walk3.wav'])

class StaticRooms:
    LOADING = 'overworld/loading'
    TUTORIAL = 'overworld/tutorial'

SkillScriptValuesToNames = {
    #'levels':       'LEVEL',
    'damage':       'DAMAGE',
    # 'chance':       'CHANCE',
    'crit':         'CRIT',
    'bonus':        'BONUS',
    'duration':     'DURATION',
    'cooldown':     'COOLDOWN',
    'hp_cost':      'HP-COST',
    'mp_cost':      'MP-COST'
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
    SCENERY = 'scenery'
    TRIGGERABLE = 'triggerable'
    name = {
        MISC: 'Misc',
        EQUIPMENT: 'Equipment',
        CONSUMABLE: 'Consumable',
        ERROR: 'Error Item',
        SCENERY : 'Scenery',
        TRIGGERABLE: 'Triggerable'
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
    BAG   =   'bag'
    name = {
        HEAD: 'Head',
        BODY: 'Body',
        WEAPON: 'Weapon',
        TRINKET: 'Trinket',
        RELIC:   'Relic',
        BAG:   'Bag'
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
    PHYARMOR =     'phy_armor'
    MAGARMOR =    'mag_armor'
    PHYARMORMAX =     'phy_armor_max'
    MAGARMORMAX =    'mag_armor_max'
    EXP =       'exp'
    LVL =       'lvl'
    PP =        'pp'
    INVSLOTS = 'inv_slots'
    

    # not saved in db
    THREAT =    'threat'
    INITIATIVE = 'initiative'
    
    name = {
        HPMAX:  'Max Health',
        MPMAX:  'Max Magicka',
        HP:     'Health',
        MP:     'Magicka',
        GRIT:   'Grit',
        FLOW:   'Flow',
        MIND:   'Mind',
        SOUL:   'Soul',
        PHYARMOR:  'Phy Armor',
        MAGARMOR:  'Mag Armor',
        PHYARMORMAX:  'Max Phy Armor',
        MAGARMORMAX: 'Max Mag Armor',
        EXP:    'Experience',
        LVL:    'Level',
        PP:     'Practice Points',

        INVSLOTS: 'Bag Space',

        # not saved in db
        THREAT: 'Threat',
        INITIATIVE: 'Initiative'
    }

PATCH_NOTES = {}
PATCH_NOTES_PATH = 'configuration/patch_notes.yaml'
with open(PATCH_NOTES_PATH, 'r') as file:
    PATCH_NOTES = yaml.safe_load(file)
    
#data = rfe.load()
ITEMS = {}
ENEMIES = {}
SKILLS = {}
NPCS = {}
WORLD = {}
SPLASH_SCREENS = {}
LORE = {}
QUESTS = {}
HELPFILES = {}

def load_lore():
    LORE['enemies'] = {}
    LORE['items'] = {}
    LORE['items_name_to_id'] = {}
    LORE['rooms'] = {}
    LORE['skills'] = {}

    for i in WORLD['world']:
        LORE['rooms'][ WORLD['world'][i]['id'] ] = WORLD['world'][i]

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
    global HELPFILES

    data = rfe.load()
    for k in data['items']:
        ITEMS[k] = data['items'][k]
    for k in data['enemies']:
        ENEMIES[k] = data['enemies'][k]
    for k in data['skills']:
        SKILLS[k] = data['skills'][k]

    with open('configuration/help.yaml', 'r') as file:
        ALL_HELP = yaml.safe_load(file)
        for i in ALL_HELP:
            if 'template' not in i:
                HELPFILES[i] = ALL_HELP[i]

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


           

