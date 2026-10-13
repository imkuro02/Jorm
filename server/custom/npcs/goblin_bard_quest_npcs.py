from actors.npcs import Npc
from configuration.constants.room_constant import RoomConstant
import copy
from configuration.config import NPCS
import random

class CustomGoblinBardQuestNpc0(Npc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog_tree = copy.deepcopy(NPCS['goblin_bard_quest_npcs_0']["tree"])
        self.dont_join_fights = True

    def tick(self):
        from scripts.greet_message import greet_message
        greet_message(
            self = self, 
            message = f'{self.id} plays a tune and says "Hello traveler"',
        )

class CustomGoblinBardQuestNpc1(Npc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog_tree = copy.deepcopy(NPCS['goblin_bard_quest_npcs_1']["tree"])
        self.dont_join_fights = True

    def tick(self):
        from scripts.greet_message import greet_message
        greet_message(
            self = self, 
            message = f'{self.id} plays a tune and says "Hello traveler"',
        )
        
