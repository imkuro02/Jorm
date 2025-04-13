from actors.actor import Actor
from dialog import Dialog
from configuration.config import NPCS, ENEMIES, StatType, ITEMS
import copy
import actors.ai
import random
from items.manager import load_item
from quest import ObjectiveCountProposal, OBJECTIVE_TYPES


def create_npc(room, npc_id, spawn_for_lore = False):
    room =          room
    name =          'actors.npcs.create_npc could not assign name'
    desc =          None
    stats =         None
    loot =          None
    skills =        None
    tree =          None
    ai =            None

    if npc_id in ENEMIES:
        names = 'Redpot Kuro Christine Adne Ken Thomas Sandra Erling Viktor Wiktor Sam Dan Arr\'zTh-The\'RchEndrough'
        name = random.choice(names.split())
        name = name + ' The ' + ENEMIES[npc_id]['name']
        desc =      ENEMIES[npc_id]['description']
        stats =     ENEMIES[npc_id]['stats']
        loot =      ENEMIES[npc_id]['loot']
        skills =    ENEMIES[npc_id]['skills']
        ai =        ENEMIES[npc_id]['ai']
    
    if npc_id in NPCS:
        name =      NPCS[npc_id]['name']
        desc =      NPCS[npc_id]['description']
        tree =      NPCS[npc_id]['tree']


    npc_class = Enemy
    if npc_id in ENEMIES:
        npc_class = Enemy
    if npc_id in NPCS:
        npc_class = Npc

    my_npc = npc_class(
        npc_id = npc_id, 
        ai = ai,
        name = name,
        description = desc,
        room = room, 
        stats = stats, 
        loot = loot, 
        skills = skills,
        dialog_tree = tree
    )  

    return my_npc


        
class Npc(Actor):
    def __init__(
        self, 
        npc_id = None, 
        ai = None,
        name = None,
        description = None, 
        room = None, 
        stats = None, 
        loot = None, 
        skills = None,
        dialog_tree = None
    ):
        super().__init__(
            name = name, 

            ai = ai,
            description = description, 
            room = room,
            
        )

        self.dialog_tree = dialog_tree
        self.npc_id = npc_id
        

        

        if stats != None:
            self.stat_manager.stats = {**self.stat_manager.stats, **stats}
            self.stat_manager.stats[StatType.HPMAX] = self.stat_manager.stats[StatType.HP]
            self.stat_manager.stats[StatType.MPMAX] = self.stat_manager.stats[StatType.MP]

        if loot != None:
            self.loot = copy.deepcopy(loot)
        else:
            self.loot = {}

        if skills != None:
            self.skill_manager.skills = copy.deepcopy(skills)

        #self.ai = EnemyAI(self)


    def sendLine(self, line):
        print(f'sendLine called in a object class Npc function? line: {line}')

    

    def tick(self):
        super().tick()
        self.ai.tick()

    def drop_loot_on_ground(self):
        for item in self.loot: 
            roll = random.random()
            if roll >= self.loot[item]:
                continue

            new_item = load_item(item)
            self.simple_broadcast('',f'{new_item.name} hits the ground with a thud.')
            self.room.inventory_manager.add_item(new_item)

    '''
    def drop_loot(self,actor):
        all_items = ITEMS
        
        for item in self.loot: 
            roll = random.random()
            if roll >= self.loot[item]:
                continue

            new_item = load_item(item)

            if actor.inventory_manager.add_item(new_item):   
                actor.sendLine(f'You loot {new_item.name}')
            else:
                actor.sendLine(f'Your inventory is full and you missed out on {new_item.name}')
    '''

    def die(self):
        
        if self.room == None:
            super().die()
            return
        if self.room.combat == None:
            super().die()
            return
        if self not in self.room.combat.participants.values():
            super().die()
            return
        
        for actor in self.room.combat.participants.values():
            if type(actor).__name__ == "Player":
                actor.stat_manager.stats[StatType.EXP] += self.stat_manager.stats[StatType.EXP]
                #self.drop_loot(actor)
                self.drop_loot_on_ground()
                proposal = ObjectiveCountProposal(OBJECTIVE_TYPES.KILL_X, self.npc_id, 1)
                actor.quest_manager.propose_objective_count_addition(proposal)
                
        super().die()


    def set_turn(self):
        super().set_turn()

class Enemy(Npc):
    def __init__(
        self, 
        npc_id = None, 
        ai = None,
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
            ai = ai,
            name = name,
            description = description, 
            room = room, 
            stats = stats, 
            loot = loot, 
            skills = skills,
            dialog_tree = dialog_tree
        )


actors.ai.create_npc = create_npc