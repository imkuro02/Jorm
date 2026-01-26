"""
from actors.npcs import Npc


class town_guard_npc(Npc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_exisiting = 0

    def tick(self):
        super().tick()

        self.time_exisiting += 1

        if self.time_exisiting % (30 * 2):
            self.simple_broadcast("", "Good to be alive or something")
"""
