import random

from actors.npcs import create_npc
from combat.manager import Combat
from configuration.config import ActorStatusType, StatType
from items.manager import load_item
from systems.inventory import InventoryManager
from systems.room import Room
from systems.utils import unload


class tavern_combat_manager(Combat):
    def combat_over(self):
        super().combat_over()
        to_unload = []
        for i in self.room.goons:
            if i not in self.room.actors.values():
                continue
            self.room.world.rooms["overworld/loading"].move_actor(i)
            to_unload.append(i)

        for i in to_unload:
            i.unload()

        self.room.goons = []
        


class tavern_inventory(InventoryManager):
    def add_item(self, item):
        #print(self.owner.can_pick_up_anything)
        if type(item).__name__ == "Equipment":
            if len(self.owner.actors) >= 1:
                output = (
                    f"The moment you let go of {item.name}, someone grabs it and runs"
                )

                first_actor = next(iter(self.owner.actors.values()))
                first_actor.simple_broadcast(output, output)
            return True
        super().add_item(item)


#from types import MethodType

class tavern_room(Room):
    @classmethod
    def compare_replace(self, room_object):
        # return False
        if "tavern" not in room_object.name.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        
        self.inventory_manager_class = tavern_inventory

        super().__init__(*args, **kwargs)
        
        self.combat_manager_class = tavern_combat_manager
        self.goons = []

        self.inventory_manager = tavern_inventory(self, 20)
        self.inventory_manager.can_pick_up_anything = True

        

    def join_combat(self, player_participant):
        super().join_combat(player_participant)
        if self.combat == None:
            return

        actors = []
        for i in self.actors.values():
            actors.append(i)
        output = ""
        for i in actors:
            if type(i).__name__ != "Player":
                if i.npc_id == "bartender":
                    output = "AAAAAAAAAAAAAAAAH!!!! goons! get em! "
                    e = create_npc(self, "thief")
                    self.combat.add_participant(e)
                    self.goons.append(e)
                    e = create_npc(self, "thief")
                    self.combat.add_participant(e)
                    self.goons.append(e)

        _broadcaster = player_participant
        output += "The patrons cheer on a good fight!"
        _broadcaster.simple_broadcast(output, output)

    def tick(self):
        super().tick()
        return
        if self.world.factory.ticks_passed % (30 * 150) == 0:
            output = f"You hear a loud thud"
            if len(self.actors.values()) <= 0:
                return
            first_actor = next(iter(self.actors.values()))
            first_actor.simple_broadcast(output, output)
        if self.world.factory.ticks_passed % (30 * 1) == 0:
            for i in self.actors.values():
                if i.status == ActorStatusType.DEAD and self.combat == None:
                    i.sendLine(
                        "A patron helps you back up on your feet, and hey!\nThey hand you a Mug"
                    )
                    i.inventory_manager.add_item(load_item("mug"))
                    i.stat_manager.stats[StatType.HP] = 1
                    i.status = ActorStatusType.NORMAL
