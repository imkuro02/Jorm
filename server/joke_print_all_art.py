import json
from configuration.config import (
    SKILLS,
    get_icon,
)
from systems.utils import add_color
import systems.utils

with open("configuration/config.json", "r") as f:
    data = json.load(f)

enemies = data["enemies"]

class FAKE:
    def __init__(self,_id):
        self.npc_id = _id
        self.status = 'Normal'

icons = []
see = ''
for enemy_id, enemy in enemies.items():
    #print(enemy_id)
    object = FAKE(enemy_id)
    icon = get_icon(object)
    
    icons.append(icon.split("\n"))

    max_height = 0
    for i in icons:
        if len(i) >= max_height:
            max_height = len(i)

    for i in icons:
        while len(i) < max_height:
            i.insert(0,' ')

    amount = len(icons)
    if amount == 10:
        t = systems.utils.Table(amount)
        # column = 0
        row = 0
        for row in range(0, max_height):
            for column in range(0, amount):
                try:
                    t.add_data(icons[column][row])

                except Exception as e:
                    t.add_data("XD")

        see = see + "\n" + t.get_table() + '\n'
        print(add_color(see))
        icons = []
        see = ''

t = systems.utils.Table(amount)
# column = 0
row = 0
for row in range(0, max_height):
    for column in range(0, amount):
        try:
            t.add_data(icons[column][row])

        except Exception as e:
            t.add_data("XD")

see = see + "\n" + t.get_table() + '\n'
print(add_color(see))
icons = []
see = ''