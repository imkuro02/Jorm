import yaml
from enum import Enum, auto
import configuration.map_loader

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
    BODY =  'body'
    WEAPON =    'weapon'
    TRINKET =   'trinket'
    name = {
        HEAD: 'Head',
        BODY: 'Body',
        WEAPON: 'Weapon',
        TRINKET: 'Trinket'
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
    MIND =      'mind'
    SOUL =      'soul'
    ARMOR =     'armor'
    MARMOR =    'marmor'
    EXP =       'exp'
    LVL =       'lvl'
    PP =        'pp'
   # MONEY =     'money'
    name = {
        HPMAX:  'Max Health',
        MPMAX:  'Max Magicka',
        HP:     'Health',
        MP:     'Magicka',
        GRIT:   'Grit',
        MIND:   'Mind',
        SOUL:   'Soul',
        ARMOR:  'Armor',
        MARMOR: 'Marmor',
        EXP:    'Experience',
        LVL:    'Level',
        PP:     'Practice Points',
        #MONEY:  'Gold Pieces'
    }

SKILLS = {}
ITEMS = {}
ENEMIES = {}
WORLD = {}
CONSUMABLE_USE_PERSPECTIVES = {}

def load():
    #SKILLS = {}
    with open('configuration/skills.yaml', 'r') as file:
        SKILLS_UNFILTERED = yaml.safe_load(file)
        for i in SKILLS_UNFILTERED:
            if 'template' not in i:
                SKILLS[i] = SKILLS_UNFILTERED[i]

    #ITEMS = {}
    with open("configuration/items.yaml", "r") as file:
        ITEMS_UNFILTERED = yaml.safe_load(file)
        for i in ITEMS_UNFILTERED:
            if 'template' not in i:
                ITEMS[i] = ITEMS_UNFILTERED[i]

    #ENEMIES = {}
    with open('configuration/enemies.yaml', 'r') as file:
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
    WORLD['world'] = configuration.map_loader.load_map()
    #print(WORLD)

    with open("configuration/consumable_use_perspectives.yaml", "r") as file:
        CONSUMABLE_USE_PERSPECTIVES_UNFILTERED = yaml.safe_load(file)
        for i in CONSUMABLE_USE_PERSPECTIVES_UNFILTERED:
            if 'template' not in i:
                CONSUMABLE_USE_PERSPECTIVES[i] = CONSUMABLE_USE_PERSPECTIVES_UNFILTERED[i]


    print('reloaded')

           

