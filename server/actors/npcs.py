from actors.actor import Actor
from dialog import Dialog
from configuration.config import NPCS, ENEMIES
from actors.enemy import Enemy

from actors.ai import EnemyAI
'''
def create_npc(room, npc_id):
    npc = Npc(npc_id, room)
    _npc = NPCS[npc_id]
    npc.name = _npc['name']
    npc.npc_id = npc_id
    npc.description = _npc['description']
    npc.dialog_tree = _npc['tree']
    return npc
'''
def create_npc(room, npc_id, spawn_for_lore = False):
    room =          room
    name =          None
    desc =          None
    stats =         None
    loot =          None
    skills =        None
    tree =          None


    if npc_id in ENEMIES:
        name =      ENEMIES[npc_id]['name']
        desc =      ENEMIES[npc_id]['description']
        stats =     ENEMIES[npc_id]['stats']
        loot =      ENEMIES[npc_id]['loot']
        skills =    ENEMIES[npc_id]['skills']
    
    if npc_id in NPCS:
        name =      NPCS[npc_id]['name']
        desc =      NPCS[npc_id]['description']
        tree =      NPCS[npc_id]['tree']


    npc_class = Npc
    if npc_id in NPCS and npc_id in ENEMIES:
        npc_class = Npc
    if npc_id not in NPCS and npc_id in ENEMIES:
        npc_class = Enemy


    my_npc = npc_class(
        npc_id = npc_id, 
        name = name,
        description = desc,
        room = room, 
        stats = stats, 
        loot = loot, 
        skills = skills,
        dialog_tree = tree
    )  
    return my_npc


class Npc(Enemy):
    def __init__(
        self, 
        npc_id = None, 
        name = None,
        description = None, 
        room = None, 
        stats = None, 
        loot = None, 
        skills = None,
        dialog_tree = None
    ):
        super().__init__(
            npc_id = npc_id, 
            name = name, 
            description = description, 
            room = room,
            stats = stats,
            loot = loot,
            skills = skills,
            dialog_tree = dialog_tree
        )

    
    def tick(self):
        super().tick()
        self.ai.tick()


