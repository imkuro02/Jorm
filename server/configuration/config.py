import os

import configuration.map.map_loader
import configuration.read_from_excel as rfe
import systems.utils
import yaml


ICONS = {}

ICONS_PATH = "configuration/text_files/icons.txt"

with open(ICONS_PATH, "r") as f:
    lines = f.readlines()

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


def get_icon(icon_id):
    if icon_id not in ICONS:
        return ''
        return "no icon?"
    border = ""  #'@normal|  '
    icon = ICONS[icon_id]
    icon = icon.split("\n")
    icon_art = ""
    for i in icon:
        icon_art += border + i + "\n"

    return icon_art

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
