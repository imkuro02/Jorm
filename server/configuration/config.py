import os

import configuration.map.map_loader
import configuration.read_from_excel as rfe
import systems.utils
import yaml


ICONS = {}

ICONS_PATH = "configuration/text_files/icons.txt"
ICONS_EQ_PATH = "configuration/text_files/icons_eq.txt"

with open(ICONS_PATH, "r") as f:
    lines = f.readlines()
with open(ICONS_EQ_PATH, "r") as f:
    lines += f.readlines()

current_id = None
buffer = []

for line in lines:
    line = line.rstrip("\n")

    if line.startswith("[id:"):
        # extract id inside brackets
        current_id = line[4:-1]  # removes "[id:" and "]"
        buffer = []
        continue

    if line == "[end]":
        if current_id:
            ICONS[current_id] = "\n".join(buffer)
            current_id = None
        continue

    # inside a block
    if current_id:
        buffer.append(line)

def get_icon_player(obj, head = None, body = None, weapon = None):
    from configuration.constants.equipment_slot_type import EquipmentSlotType

    if obj == None:
        icon_head =     ICONS['eq_head']    if head == None else ICONS[head]
        icon_body =     ICONS['eq_body']    if body == None else ICONS[body]
        icon_weapon =   ICONS['eq_weapon']  if weapon == None else ICONS[weapon]

        icon_head += '\nscheme @normal @normal @normal'
        icon_body += '\nscheme @normal @normal @normal'
        icon_weapon += '\nscheme @normal @normal @normal'
    else:
        slots = obj.slots_manager.slots
        inv = obj.inventory_manager.items

        if slots[EquipmentSlotType.HEAD] != None and inv[slots[EquipmentSlotType.HEAD]].icon_id in ICONS:
            icon_head = ICONS[inv[slots[EquipmentSlotType.HEAD]].icon_id]
            icon_head += '\nscheme '+inv[slots[EquipmentSlotType.HEAD]].icon_scheme
        else:
            icon_head =  ICONS['eq_head']    
            icon_head += '\nscheme @normal @normal @normal'

        
        if slots[EquipmentSlotType.BODY] != None and inv[slots[EquipmentSlotType.BODY]].icon_id in ICONS:
            icon_body = ICONS[inv[slots[EquipmentSlotType.BODY]].icon_id]
            icon_body += '\nscheme '+inv[slots[EquipmentSlotType.BODY]].icon_scheme
        else:
            icon_body =  ICONS['eq_body']    
            icon_body += '\nscheme @normal @normal @normal'
        

        if slots[EquipmentSlotType.WEAPON] != None and inv[slots[EquipmentSlotType.WEAPON]].icon_id in ICONS:
            icon_weapon = ICONS[inv[slots[EquipmentSlotType.WEAPON]].icon_id]
            icon_weapon += '\nscheme '+inv[slots[EquipmentSlotType.WEAPON]].icon_scheme
        else:
            icon_weapon =  ICONS['eq_weapon']  
            icon_weapon += '\nscheme @normal @red @red'


    index = 1
    if icon_head.split('\n')[-1].startswith('scheme'):
        colors = icon_head.split('\n')[-1].split(' ')
        for color in colors:
            if color == 'scheme':
                continue
            icon_head = icon_head.replace(f'@c{index}', color)
            index += 1
        icon_head = "\n".join(icon_head.split("\n")[:-1])

    index = 1
    if icon_body.split('\n')[-1].startswith('scheme'):
        colors = icon_body.split('\n')[-1].split(' ')
        for color in colors:
            if color == 'scheme':
                continue
            icon_body = icon_body.replace(f'@c{index}', color)
            index += 1
        icon_body = "\n".join(icon_body.split("\n")[:-1])

    index = 1
    if icon_weapon.split('\n')[-1].startswith('scheme'):
        colors = icon_weapon.split('\n')[-1].split(' ')
        for color in colors:
            if color == 'scheme':
                continue
            icon_weapon = icon_weapon.replace(f'@c{index}', color)
            index += 1
        icon_weapon = "\n".join(icon_weapon.split("\n")[:-1])
    

    icon_body_head = icon_head +'\n'+ icon_body
    list_body_head = icon_body_head.split('\n')
    
    list_weapon = icon_weapon.split('\n')

    icon = []
    for i, _ in enumerate(list_weapon):
        icon.append(list_body_head[i])
        icon.append(list_weapon[i])
        icon.append('\n')

    icon_compiled = ''.join(icon)
    return icon_compiled

from itertools import product
def create_equipment_combinations(items):
    heads = [x for x in items if x.startswith("eq_head")]
    bodies = [x for x in items if x.startswith("eq_body")]
    weapons = [x for x in items if x.startswith("eq_weapon")]

    combinations = [
        {
            "head": head,
            "body": body,
            "weapon": weapon,
        }
        for head, body, weapon in product(heads, bodies, weapons)
    ]

    return {
        "heads": heads,
        "bodies": bodies,
        "weapons": weapons,
        "combinations": combinations,
    }
result = create_equipment_combinations(ICONS)
print(result['combinations'])
for i in result['combinations']:
    print(systems.utils.add_color(get_icon_player(None, i['head'], i['body'], i['weapon'])))

def get_icon(obj):
    if type(obj).__name__ == 'Player':
        return get_icon_player(obj)
    #icon_id = obj.npc_id
    icon_id = obj.icon_id
    icon_style = obj.status

    icon_to_get = icon_id+'/'+icon_style

    if icon_to_get in ICONS:
        border = ""  #'@normal|  '
        icon = ICONS[icon_to_get]
        icon = icon.split("\n")
        icon_art = ""
        for i in icon:
            icon_art += border + i + "\n"
        return icon_art
        
        
    icon_to_get = icon_id

    if icon_to_get in ICONS:
        border = ""  #'@normal|  '
        icon = ICONS[icon_to_get]
        icon = icon.split("\n")
        icon_art = ""
        for i in icon:
            icon_art += border + i + "\n"
        return icon_art

    return ''

def check_for_broken_icons():
    _e = ENEMIES
    _i = ICONS

    for i in _i:
        if i not in _e:
            systems.utils.debug_print(f'"{i}" not in ENEMIES')

    for e in _e:
        if e not in _i:
            systems.utils.debug_print(f'"{e}" not in ICONS')

def check_for_not_spawnable_enemies():
    _e = ENEMIES 
    for e in _e:
        #print(e)
        enemy_not_spawnable = True
        for spawner in WORLD['world'].values():
            for spawn_spot in spawner["spawner"]:
                #print(spawn_spot)
                if e in spawn_spot:
                    enemy_not_spawnable = False
        if enemy_not_spawnable:
            systems.utils.debug_print(f'"{e}" does not spawn anywhere on map')

def check_for_not_droppable_or_spawnable_items():
    _e = ENEMIES
    _i = ITEMS
    for i in _i:
        loot_not_droppable = True
        for e in _e:
            if i in _e[e]['loot']:
                loot_not_droppable = False

        for spawner in WORLD['world'].values():
            for spawn_spot in spawner["spawner"]:
                if i in spawn_spot:
                    loot_not_droppable = False

        if loot_not_droppable:
            systems.utils.debug_print(f'"{i}" is not droppable from any enemies, nor spawns in any rooms')


PATCH_NOTES = {}
PATCH_NOTES_PATH = "configuration/text_files/patch_notes.yaml"
with open(PATCH_NOTES_PATH, "r") as file:
    PATCH_NOTES = yaml.safe_load(file)

# data = rfe.load()
ITEMS = {}
ENEMIES = {}
SKILLS = {}
EQUIPMENT_REFORGES = {}
NPCS = {}
WORLD = {}
SPLASH_SCREENS = {}
LORE = {}
QUESTS = {}
HELPFILES = {}


def load_lore():
    LORE["enemies"] = {}
    LORE["items"] = {}
    LORE["items_name_to_id"] = {}
    LORE["rooms"] = {}
    LORE["skills"] = {}

    for i in WORLD["world"]:
        LORE["rooms"][WORLD["world"][i]["id"]] = WORLD["world"][i]

    for i in ITEMS:
        LORE["items"][ITEMS[i]["name"]] = ITEMS[i]
        LORE["items_name_to_id"][ITEMS[i]["premade_id"]] = ITEMS[i]["name"]

    for i in ENEMIES:
        LORE["enemies"][ENEMIES[i]["name"]] = ENEMIES[i]

    for i in SKILLS:
        LORE["skills"][SKILLS[i]["name"]] = SKILLS[i]

    return LORE


def load():
    global QUESTS
    global LORE
    global ITEMS
    global ENEMIES
    global SKILLS  # Declare the global variables here
    global EQUIPMENT_REFORGES
    global HELPFILES

    data = rfe.load()
    for k in data["items"]:
        ITEMS[k] = data["items"][k]
    for k in data["enemies"]:
        ENEMIES[k] = data["enemies"][k]
    for k in data["skills"]:
        SKILLS[k] = data["skills"][k]
    for k in data["equipment_reforges"]:
        EQUIPMENT_REFORGES[k] = data["equipment_reforges"][k]

    with open("configuration/text_files/help.yaml", "r") as file:
        ALL_HELP = yaml.safe_load(file)
        for i in ALL_HELP:
            if "template" not in i:
                HELPFILES[i] = ALL_HELP[i]

    QUESTS_DIRECTORY = "configuration/quests/"

    for root, dirs, files in os.walk(QUESTS_DIRECTORY):
        for filename in files:
            if filename.endswith(".yaml"):
                file_path = os.path.join(root, filename)
                with open(file_path, "r") as file:
                    ALL_QUESTS = yaml.safe_load(file)
                    for i in ALL_QUESTS:
                        if "template" not in i:
                            QUESTS[i] = ALL_QUESTS[i]

    # SKILLS = {}
    NPCS_DIRECTORY = "configuration/npcs/"
    for root, dirs, files in os.walk(NPCS_DIRECTORY):
        for filename in files:
            if filename.endswith(".yaml"):
                file_path = os.path.join(root, filename)
                with open(file_path, "r") as file:
                    ALL_NPCS = yaml.safe_load(file)
                    for i in ALL_NPCS:
                        if "template" not in i:
                            NPCS[i] = ALL_NPCS[i]

    from configuration.splashscreens.splash import splash_screens

    SPLASH_SCREENS["screens"] = splash_screens

    WORLD["world"] = configuration.map.map_loader.load_map()
    # systems.utils.debug_print(len(WORLD['world']))

    LORE = load_lore()

    systems.utils.debug_print("reloaded")
