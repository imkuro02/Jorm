import yaml
from enum import Enum, auto

class ItemType(Enum):
    Misc = auto()
    Equipment = auto()
    Consumable = auto()
    
class AffType(Enum):
    Basic = auto()
    DOT1 = auto()
    DOT2 = auto()
    HealAmp = auto()
    PowerUp = auto()
    Ethereal = auto()
    ReflectDamage = auto()
    Stunned = auto()

class DamageType(Enum):
    Physical = auto()
    Magical = auto()
    Healing = auto()
    Pure = auto()
    Cancelled = auto()

class ActorStatusType(Enum):
    Normal = auto()
    Fighting = auto()
    Dead = auto()

class Config:
    def __init__(self):
        self.ENEMIES = {}
        with open('config/enemies.yaml', 'r') as file:
            ALL_ENEMIES = yaml.safe_load(file)
            for i in ALL_ENEMIES:
                if 'template' not in i:
                    self.ENEMIES[i] = ALL_ENEMIES[i]

        self.SKILLS = {}
        with open('config/skills.yaml', 'r') as file:
            SKILLS_UNFILTERED = yaml.safe_load(file)
            for i in SKILLS_UNFILTERED:
                if 'template' not in i:
                    self.SKILLS[i] = SKILLS_UNFILTERED[i]

        self.ITEMS = {}
        with open("config/items.yaml", "r") as file:
            ITEMS_UNFILTERED = yaml.safe_load(file)
            for i in ITEMS_UNFILTERED:
                if 'template' not in i:
                    self.ITEMS[i] = ITEMS_UNFILTERED[i]

        self.EQUIPMENT_PREFIXES = {}
        with open("config/equipment_prefixes.yaml", "r") as file:
            EQUIPMENT_PREFIXES_UNFILTERED = yaml.safe_load(file)
            for i in EQUIPMENT_PREFIXES_UNFILTERED:
                self.EQUIPMENT_PREFIXES[i] = EQUIPMENT_PREFIXES_UNFILTERED[i]

        self.WORLD = {}
        with open("config/world.yaml", "r") as file:
            WORLD_UNFILTERED = yaml.safe_load(file)
            for i in WORLD_UNFILTERED:
                if 'template' not in i:
                    self.WORLD[i] = WORLD_UNFILTERED[i]

        
        

