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
        #print(self.__dict__)
        self.time_exisiting = 0
        self.actors = len(self.room.actors.values())

    def tick(self):
        super().tick()
        self.time_exisiting += 1
        if self.time_exisiting % (30 * 4) == 0:
            if self.actors != len(self.room.actors.values()):
                self.actors = len(self.room.actors.values())
                self.simple_broadcast(
                    "", f'"Good to be alive or something" says {self.pretty_name()}'
                )

        if self.room.combat != None:
            self.simple_broadcast(
                "", f'"Cut that out at once!" yells {self.pretty_name()}'
            )
            self.room.combat.combat_over()
