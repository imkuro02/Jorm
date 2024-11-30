import yaml
from enum import Enum, auto

class ItemType:
    MISC = 'Misc'
    EQUIPMENT = 'Equipment'
    CONSUMABLE = 'Consumable'
    
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
    CANCELLED = 5

class ActorStatusType:
    NORMAL = 'Normal'
    FIGHTING = 'Fighting'
    DEAD = 'Dead'

class EquipmentSlotType:
    HEAD =      'Head'
    NECK =      'Neck'
    CHEST =     'Chest'
    HANDS =     'Hands'
    BELT =      'Belt'
    LEGS =      'Legs'
    FEET =      'Feet'
    TRINKET =   'Trinket'
    PRIMARY =   'Primary'
    SECONDARY = 'Secondary'

class StatType:
    HPMAX = 'Max Health'
    MPMAX = 'Max Mana'
    HP = 'Health'
    MP = 'Mana'
    BODY = 'Body'
    MIND = 'Mind'
    SOUL = 'Soul'
    ARMOR = 'Armor'
    MARMOR = 'Marmor'
    EXP = 'Experience'
    LVL = 'Level'
    PP = 'Practice Points'

SKILLS = {}
with open('config/skills.yaml', 'r') as file:
    SKILLS_UNFILTERED = yaml.safe_load(file)
    for i in SKILLS_UNFILTERED:
        if 'template' not in i:
            SKILLS[i] = SKILLS_UNFILTERED[i]

ITEMS = {}
with open("config/items.yaml", "r") as file:
    ITEMS_UNFILTERED = yaml.safe_load(file)
    for i in ITEMS_UNFILTERED:
        if 'template' not in i:
            ITEMS[i] = ITEMS_UNFILTERED[i]

ENEMIES = {}
with open('config/enemies.yaml', 'r') as file:
    ALL_ENEMIES = yaml.safe_load(file)
    for i in ALL_ENEMIES:
        if 'template' not in i:
            ENEMIES[i] = ALL_ENEMIES[i]

WORLD = {}
with open("config/world.yaml", "r") as file:
    WORLD_UNFILTERED = yaml.safe_load(file)
    for i in WORLD_UNFILTERED:
        if 'template' not in i:
            WORLD[i] = WORLD_UNFILTERED[i]

        

        
        

