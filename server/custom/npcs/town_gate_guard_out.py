from actors.npcs import Npc


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
        if self.factory.ticks_passed % (30 * 4) == 0:
            if not hasattr(self,'actors_in_room_count'):
                self.actors_in_room_count = 0
            if self.actors_in_room_count != len(self.room.actors.values()):
                self.actors_in_room_count = len(self.room.actors.values())
                self.simple_broadcast(
                    "", f'"Good to be alive or something" says {self.pretty_name()}'
                )

        if self.room.combat != None:
            self.simple_broadcast(
                "", f'"Cut that out at once!" yells {self.pretty_name()}'
            )
            self.room.combat.combat_over()
