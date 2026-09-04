import random

import systems.utils
from actors.ai import AI
from actors.npcs import create_npc
from configuration.constants.actor_status_type import ActorStatusType
from configuration.constants.room_constant import RoomConstant
from configuration.constants.stat_type import StatType

'''
class SlimeAI(AI):
    def tick(self):
        if not super().tick():
            return

        stats = self.actor.stat_manager.stats
        if (
            stats[StatType.HP] < stats[StatType.HPMAX] * 0.75
            and stats[StatType.HPMAX] > 10
        ):
            stats[StatType.HP] = int(stats[StatType.HP] * 0.5)
            stats[StatType.HPMAX] = stats[StatType.HP]

            # create npc is assigned in actors.npcs script
            clone = create_npc(self.actor.room, self.actor.npc_id)
            clone.stat_manager.stats[StatType.HPMAX] = stats[StatType.HP]
            clone.stat_manager.stats[StatType.HP] = stats[StatType.HP]
            clone.simple_broadcast("", f"{self.actor.pretty_name()} splits!")
            clone.room.join_combat(clone)
            self.actor.finish_turn()
        else:
            self.use_prediction()

    def use_prediction(self, no_checks=False):
        if super().use_prediction(no_checks=no_checks):
            return True
        self.actor.simple_broadcast(
            "You do nothing!", f"{self.actor.pretty_name()} does nothing!"
        )
        # self.predict_use_best_skill()
        self.actor.finish_turn()
        return False
'''

class CowardAI(AI):
    def tick(self):
        if not super().tick():
            return

        if len(self.actor.room.exits) >= 1:
            stats = self.actor.stat_manager.stats
            roll = (100 - (stats[StatType.HP] / stats[StatType.HPMAX] * 100)) / 5
            # systems.utils.debug_print(roll)
            if roll > random.randint(1, 100):
                # random_dir = random.choice(self.actor.room.exits)
                list_pretty_name_objects = [self.actor]
                self.actor.pretty_broadcast(None, f"{self.actor.id} flees!",
                    list_pretty_name_objects = list_pretty_name_objects)
                # new_room = random_dir.get_room_obj().id

                world = self.actor.room.world
                self.actor.status = ActorStatusType.NORMAL

                world.rooms[RoomConstant.LOADING].move_actor(self.actor, silent=True)
                self.die()
                self.actor.finish_turn()
                return

        self.use_prediction()

    def use_prediction(self, no_checks=False):
        if super().use_prediction(no_checks=no_checks):
            return True
        list_pretty_name_objects = [self.actor]
        self.actor.simple_broadcast(
            f"{self.actor.id}", f"{self.actor.id} does nothing!",
            list_pretty_name_objects = list_pretty_name_objects
        )
        # self.predict_use_best_skill()
        self.actor.finish_turn()
        return False


class BossRatAI(AI):
    def __init__(self, actor):
        super().__init__(actor)
        self.turn = 0

    def initiative(self):
        self.predict_use_best_skill()
        self.turn += 1
        match self.turn:
            case 3:
                self.override_prediction("is scheming")
            case 6:
                self.override_prediction("licks their snout in anticipation")
            case _:
                self.override_prediction()

        if self.turn == 7:
            self.turn = 0

    def tick(self):
        if not super().tick():
            return

        if self.turn == 6:
            heal = 0
            to_devour = []
            for par in self.actor.room.combat.participants.values():
                if type(par).__name__ != "Player":
                    if par.npc_id == "rat":
                        to_devour.append(par)

            # if to_devour == []:
            #    self.turn = 0
            #    self.use_prediction()
            #    return

            for par in to_devour:
                par.die()
                heal += 10

            list_pretty_name_objects = [self.actor]
            self.actor.pretty_broadcast(
                None, f"{self.actor.id} Devours the rats! healing for {heal}",
                list_pretty_name_objects = list_pretty_name_objects
            )
            self.actor.heal(value=heal, silent=True)

            self.actor.finish_turn()
            return

        if self.turn == 3:
            list_pretty_name_objects = [self.actor]
            self.actor.pretty_broadcast(None, f"{self.actor.id} roars loudly!",
                list_pretty_name_objects = list_pretty_name_objects)

            for i in range(0, random.randint(1, 3)):
                rat = create_npc(self.actor.room, "rat")
                rat.can_drop_corpse = False
                rat.room.join_combat(rat)
                rat.stat_manager.stats[StatType.EXP] = 0
                rat.loot = {}
            self.actor.finish_turn()
            return

        self.use_prediction()
        return

    def use_prediction(self, no_checks=False):
        if super().use_prediction(no_checks=no_checks):
            return True
        list_pretty_name_objects = [self.actor]
        self.actor.simple_broadcast(
            f"{self.actor.id} do nothing!", f"{self.actor.id} does nothing!",
            list_pretty_name_objects = list_pretty_name_objects
        )
        # self.predict_use_best_skill()
        self.actor.finish_turn()
        return False

