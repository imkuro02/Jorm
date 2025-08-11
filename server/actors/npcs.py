from actors.actor import Actor
from dialog import Dialog
from configuration.config import NPCS, ENEMIES, StatType, ITEMS, ActorStatusType
import copy
import actors.ai
import random
from items.manager import load_item
from quest import ObjectiveCountProposal, OBJECTIVE_TYPES


def create_npc(room, npc_id, spawn_for_lore = False):
    room =          room
    name =          'None'
    desc =          None
    stats =         None
    loot =          None
    skills =        None
    tree =          None
    ai =            None
    can_start_fights = False
    dont_join_fights = False

    #if npc_id not in ENEMIES:
    #    return
    

    if npc_id in ENEMIES:
        names = 'Niymiae Tanni Rahji Rahj Rahjii Redpot Kuro Christine Adne Ken Thomas Sandra Erling Viktor Wiktor Sam Dan'
        old_name_not_used = 'Arr\'zTh-The\'RchEndrough'
        name = random.choice(names.split())
        name = name + ' The ' + ENEMIES[npc_id]['name']
        desc =      ENEMIES[npc_id]['description']
        stats =     ENEMIES[npc_id]['stats']
        _loot =     ENEMIES[npc_id]['loot']
        skills =    ENEMIES[npc_id]['skills']
        ai =        ENEMIES[npc_id]['ai']
        can_start_fights = ENEMIES[npc_id]['can_start_fights']
        dont_join_fights = ENEMIES[npc_id]['dont_join_fights']
        loot = _loot # {}
        '''
        for i in ITEMS:
            if 'requirements' in ITEMS[i]:
                match abs(ITEMS[i]['requirements']['lvl'] - stats[StatType.LVL]):
                    case 0:
                        loot[i] = 0.01
                    case 1:
                        loot[i] = 0.009
                    case 2:
                        loot[i] = 0.008
                    case 3:
                        loot[i] = 0.007
                    case 5:
                        loot[i] = 0.006
                    case 6:
                        loot[i] = 0.005
        for i in _loot:
            loot[i] = _loot[i]
        '''
            
    if npc_id in NPCS:
        #name =      NPCS[npc_id]['name']
        #desc =      NPCS[npc_id]['description']
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
        dialog_tree = tree,
        can_start_fights = can_start_fights,
        dont_join_fights = dont_join_fights
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
        dialog_tree = None,
        can_start_fights = False,
        dont_join_fights = True
    ):
        super().__init__(
            name = name, 

            ai = ai,
            description = description, 
            room = room,
            
        )

        self.dialog_tree = dialog_tree
        self.npc_id = npc_id
        
        self.can_start_fights = can_start_fights
        self.dont_join_fights = dont_join_fights
        

        if stats != None:
            self.stat_manager.stats = {**self.stat_manager.stats, **stats}
            self.stat_manager.stats[StatType.HPMAX] = self.stat_manager.stats[StatType.HP]
            self.stat_manager.stats[StatType.MPMAX] = self.stat_manager.stats[StatType.MP]
            self.stat_manager.stats[StatType.ARMORMAX] = self.stat_manager.stats[StatType.ARMOR]
            self.stat_manager.stats[StatType.MARMORMAX] = self.stat_manager.stats[StatType.MARMOR]

        if loot != None:
            self.loot = copy.deepcopy(loot)
        else:
            self.loot = {}

        if skills != None:
            self.skill_manager.skills = copy.deepcopy(skills)

        #self.ai = EnemyAI(self)

    def talk_to(self, talker):
        if not super().talk_to(talker): 
            return
        # if returned true, start dialog
        talker.simple_broadcast(f'You approach {self.pretty_name()}', f'{talker.pretty_name()} approaches {self.pretty_name()}.')
        talker.current_dialog = Dialog(talker, self, self.dialog_tree)
        talker.current_dialog.print_dialog()
        #return True

    # this function returns whether the npc has a quest to hand out or turn in / both
    # actor_to_compare is the player that is checking 
    def get_important_dialog(self, actor_to_compare, return_dict = False):
        has_quest_to_start = False
        has_quest_to_turn_in = False
        quest_man = actor_to_compare.quest_manager
        output = ''
        
        if self.dialog_tree == None:
            return False
        
        for branch in self.dialog_tree.values():
            
            if 'options' not in branch:
                continue
            #print(branch['options'])
            for option in branch['options']:
                #print('!')
                if 'quest_check' not in option:
                    continue

                if 'quest_start' not in option and 'quest_turn_in' not in option:
                    continue

                #print('checking, ',option['quest_check'])
                check_valid = True
                for quest_to_check in option['quest_check']:
                    not_valid = quest_man.check_quest_state(quest_to_check['id']) != quest_to_check['state']
                    #print(not_valid, quest_man.check_quest_state(quest_to_check['id']) , quest_to_check['state'])
                    if not_valid:    
                        check_valid = False
                        
                        
                    #output = output + quest_to_check['id'] + ': ' + quest_to_check['state'] + ' ### '

                if check_valid:
                    if 'quest_start' in option:
                        has_quest_to_start = True
                    if 'quest_turn_in' in option:
                        has_quest_to_turn_in = True

        if return_dict:
            return {'quest_not_started': has_quest_to_start, 'quest_turn_in': has_quest_to_turn_in}
        
        if has_quest_to_start and has_quest_to_turn_in:
            output = output + '\nHas both a quest to start and a quest to turn in'
        else:
            if has_quest_to_start:
                output = output + '\nHas a quest to start'
            if has_quest_to_turn_in:
                output = output + '\nHas a quest to turn in'

        return output

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

    
    def drop_loot(self, actor, room):
        all_items = ITEMS
        
        for item in self.loot: 
            if self.loot[item] != 1:
                roll = random.randrange(1,self.loot[item])
                if roll != 1:
                    continue

            new_item = load_item(item)

            if actor.inventory_manager.add_item(new_item):   
                actor.sendLine(f'You loot {new_item.name} (1 in {self.loot[item]} chance)')
            else:
                actor.sendLine(f'Your inventory is full, {new_item.name} has been dropped on the ground')
                room.inventory_manager.add_item(new_item)
    

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
        
       
        room = self.room

        participants = room.combat.participants.values()
        super().die()

        
        for actor in participants:
            if type(actor).__name__ == "Player":
                if actor.status == ActorStatusType.DEAD:
                    continue
                actor.gain_exp(self.stat_manager.stats[StatType.EXP])
                self.drop_loot(actor, room)
                #self.drop_loot_on_ground()
                proposal = ObjectiveCountProposal(OBJECTIVE_TYPES.KILL_X, self.npc_id, 1)
                actor.quest_manager.propose_objective_count_addition(proposal)


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
        dialog_tree = None,
        can_start_fights = False,
        dont_join_fights = True
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
            dialog_tree = dialog_tree,
            can_start_fights = can_start_fights,
            dont_join_fights = dont_join_fights
        )


actors.ai.create_npc = create_npc