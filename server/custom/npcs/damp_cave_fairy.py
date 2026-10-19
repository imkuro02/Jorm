
from actors.npcs import Npc
from configuration.constants.room_constant import RoomConstant

class CustomDampCaveFairy(Npc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_start_fights = False
        self.dont_join_fights = True

    def tick(self):
        if self.room == None:
            return
        from scripts.greet_message import greet_message
        send_to = [i for i in self.room.actors.values() if type(i).__name__ == 'Player' and 
                    i.quest_manager.check_quest_state('damp_cave_fairy_quest') != 'turned_in']
        greet_message(
            self = self, 
            message = f'{self.id} shivers and hides',
            send_to = send_to
            )
        send_to = [i for i in self.room.actors.values() if type(i).__name__ == 'Player' and 
                    i.quest_manager.check_quest_state('damp_cave_fairy_quest') == 'turned_in']
        greet_message(
            self = self, 
            message = f'{self.id} circles around in joy',
            send_to = send_to
            )