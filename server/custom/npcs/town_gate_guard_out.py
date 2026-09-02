from actors.npcs import Npc
from configuration.constants.room_constant import RoomConstant

class town_guard_npc(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        # return False
        if "town_gate_guard_out" not in npc_object.npc_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self):
        if self.room == None:
            return
        from scripts.greet_message import greet_message
        send_to = [i for i in self.room.actors.values() if type(i).__name__ == 'Player' and 
                    i.recall_site != RoomConstant.TAVERN]
        greet_message(
            self = self, 
            message = f'{self.id} says "You should check out the tavern, if you have not yet"',
            send_to = send_to
            )
        send_to = [i for i in self.room.actors.values() if type(i).__name__ == 'Player' and 
                    i.quest_manager.check_quest_state('blacksmith_reforge') == 'not_started']
        greet_message(
            self = self, 
            message = f'{self.id} says "The blacksmith recently reforged my spear, nice fella just west of town square"',
            send_to = send_to
            )
        greet_message(
            self = self, 
            message = f'{self.id} nods at you',
            )

        if self.room.combat != None:
            list_pretty_name_objects = [self]
            self.pretty_broadcast(
                None, f'"Cut that out at once!" yells {self.id}',
                list_pretty_name_objects = list_pretty_name_objects
            )
            self.room.combat.combat_over()
