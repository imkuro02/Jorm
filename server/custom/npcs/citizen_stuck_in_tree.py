from actors.npcs import Npc
from configuration.constants.room_constant import RoomConstant
import copy
from configuration.config import NPCS
import random

class citizen_stuck_in_tree(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        # return False
        if "citizen" not in npc_object.npc_id.lower():
            return False
        if npc_object.room.id != 'overworld/445f4046-5383-4158-83e9-c9a911432ef0':
            return False 
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog_0 = copy.deepcopy(NPCS['event_stuck_in_tree_citizen_dialog_0']["tree"])
        self.dialog_1 = copy.deepcopy(NPCS['event_stuck_in_tree_citizen_dialog_1']["tree"])
        self.dialog_tree = self.dialog_0
        self.original_desc = self.description
        self.original_name = self.name
        self.dont_join_fights = True

    def stuck_in_tree(self):
        is_stuck = False
        for i in self.room.actors.values():
            if i.npc_id not in [self.npc_id, 'player']:
                is_stuck = True

        if is_stuck:
            self.dialog_tree = self.dialog_0
            self.description = self.original_desc + '\nThey have climbed up a tree to get away from the monsters below.'
            self.name = self.original_name.replace('Citizen','Tree Stuck Citizen')
        else:
            self.name = self.original_name.replace('Tree Stuck Citizen','Citizen')
            self.dialog_tree = self.dialog_1
            self.description = self.original_desc
        return is_stuck

    def tick(self):
        from custom.npcs import _utils
        if self.stuck_in_tree():
            _utils.greet_message(
                self = self, 
                message = f'{self.id} yells "hey over here! im stuck in the tree!"',
            )
        else:
            _utils.greet_message(
                self = self, 
                message = f'{self.id} nods at you',
            )

    def talk_to(self, talker):
        self.stuck_in_tree()
            
        super().talk_to(talker)

#event_stuck_in_tree_citizen_dialog_1
#tree = copy.deepcopy(NPCS[npc_id]["tree"])