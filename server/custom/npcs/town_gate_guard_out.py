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
        from custom.npcs import _utils
        send_to = [i for i in self.room.actors.values() if type(i).__name__ == 'Player' and 
                    i.recall_site != RoomConstant.TAVERN]
        _utils.greet_message(
            self = self, 
            message = f'{self.id} says "You should check out the tavern, if you have not yet"',
            send_to = send_to
            )
        send_to = [i for i in self.room.actors.values() if type(i).__name__ == 'Player' and 
                    i.quest_manager.check_quest_state('blacksmith_reforge') == 'not_started']
        _utils.greet_message(
            self = self, 
            message = f'{self.id} says "The blacksmith recently reforged my spear, nice fella just west of town square"',
            send_to = send_to
            )
        _utils.greet_message(
            self = self, 
            message = f'{self.id} nods at you',
            )

        if self.room.combat != None:
            self.simple_broadcast(
                "", f'"Cut that out at once!" yells {self.pretty_name()}'
            )
            self.room.combat.combat_over()
