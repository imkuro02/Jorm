import random

import systems.utils
from actors.ai import AI
from actors.npcs import create_npc
from configuration.config import ActorStatusType, StaticRooms, StatType


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
                self.actor.simple_broadcast("", f"{self.actor.pretty_name()} flees!")
                # new_room = random_dir.get_room_obj().id

                world = self.actor.room.world
                self.actor.status = ActorStatusType.NORMAL

                world.rooms[StaticRooms.LOADING].move_actor(self.actor, silent=True)
                self.die()
                self.actor.finish_turn()
                return

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

            self.actor.simple_broadcast(
                "", f"{self.actor.pretty_name()} Devours the rats! healing for {heal}"
            )
            self.actor.heal(value=heal, silent=True)

            self.actor.finish_turn()
            return

        if self.turn == 3:
            self.actor.simple_broadcast("", f"{self.actor.pretty_name()} roars loudly!")
            for i in range(0, random.randint(1, 3)):
                rat = create_npc(self.actor.room, "rat")
                rat.room.join_combat(rat)
            self.actor.finish_turn()
            return

        self.use_prediction()
        return

    def use_prediction(self, no_checks=False):
        if super().use_prediction(no_checks=no_checks):
            return True
        self.actor.simple_broadcast(
            "You do nothing!", f"{self.actor.pretty_name()} does nothing!"
        )
        # self.predict_use_best_skill()
        self.actor.finish_turn()
        return False


class VoreAI(AI):
    def __init__(self, actor):
        super().__init__(actor)
        self.rooms = self.actor.room.world.rooms
        self.vore_room_id = f"{self.actor.room.id}-vored-by-{self.actor.id}"
        self.vore_room = None
        self.original_room = self.actor.room
        self.turn = 0
        # self.vore_room_open()

        self.vore_room_name = "Vore room name"
        self.vore_room_description = "Vore room description"
        self.vore_room_spawns = ""

        self.turn_max = 7
        self.turn_vore = 6
        self.turn_vore_text = "Looks hungry"

    def initiative(self):
        self.predict_use_best_skill()
        self.turn += 1
        match self.turn:
            case self.turn_vore:
                self.override_prediction(self.turn_vore_text)
            case _:
                self.override_prediction()
        if self.turn == self.turn_max:
            self.turn = 0

    def tick(self):
        if not super().tick():
            return

        if self.turn == self.turn_vore:
            if self.vore_room == None:
                self.vore_room_open()
            self.vore_room_grab_party()
            self.actor.finish_turn()
            return

        self.use_prediction()
        return

    def create_vore_room_from_template(self):
        return Room(
            self.actor.room.world,
            self.vore_room_id,
            name=self.vore_room_name,  # 'Vore room name',
            description=self.vore_room_description,  # 'Vore room description',
            from_file="vore_room",
            exits=[],
            can_be_recall_site=False,
            doorway=False,
            instanced=False,
            no_spawner=True,
        )

    # create new vore room
    def vore_room_open(self):
        vore_room = self.create_vore_room_from_template()
        self.rooms[self.vore_room_id] = vore_room
        self.vore_room = vore_room
        vore_room_exit = Exit(
            self.vore_room, "out", self.original_room.id, blocked=True
        )
        self.vore_room.exits.append(vore_room_exit)

        for line in self.vore_room_spawns.split("\n"):
            for val in line.split(","):
                to_spawn = create_npc(self.vore_room, val)
                # to_spawn.room.join_combat(val)

    # close vore room, kick all player parties back into the room
    def vore_room_close(self):
        if self.vore_room == None:
            return
        # systems.utils.debug_print(self.vore_room.__dict__)
        self.actor.room.world.rooms_to_unload.append(self.vore_room.id)
        # del self.rooms[self.vore_room_id]

    # grab a party and add it to vore room
    def vore_room_grab_party(self):
        systems.utils.debug_print("grabbing party")
        to_move = []
        for i in self.original_room.actors.values():
            if type(i).__name__ != "Player":
                systems.utils.debug_print("not player", i.name)
                continue
            if i.status != ActorStatusType.FIGHTING:
                systems.utils.debug_print("not fighting", i.name)
                continue
            to_move.append(i)

        for i in to_move:
            i.simple_broadcast(
                f"{self.actor.pretty_name()} vores you!",
                f"{self.actor.pretty_name()} vores {i.pretty_name()}!",
            )
        for i in to_move:
            self.vore_room.move_actor(i, silent=True, dont_unload_instanced=True)
            i.status = ActorStatusType.NORMAL

        # for i in to_move:
        #    i.command_look('')

    def vore_room_kick_all_parties(self):
        if self.vore_room == None:
            return

        to_move = []
        for i in self.vore_room.actors.values():
            if type(i).__name__ != "Player":
                continue
            to_move.append(i)

        for i in to_move:
            i.simple_broadcast(
                f"{self.actor.pretty_name()} spits you out!",
                f"{self.actor.pretty_name()} spits out {i.pretty_name()}!",
            )
        for i in to_move:
            self.original_room.move_actor(i, silent=True, dont_unload_instanced=True)
            i.status = ActorStatusType.NORMAL

    def die(self):
        self.vore_room_kick_all_parties()
        self.vore_room_close()


class VoreDragonLesserAI(VoreAI):
    def __init__(self, actor):
        super().__init__(actor)
        self.turn_max = 7
        self.turn_vore = 2

        self.turn_vore_text = "Looks hungry"
        self.vore_room_name = "Mouth of the dragon"
        self.vore_room_description = "The smell of charcoal mixed with burnt flesh overwhelms you\nIt is hot, wet, and dark here."
        self.vore_room_spawns = "dragon_tongue_0\ndragon_tooth_0\ndragon_tooth_0\ndragon_tooth_0\ndragon_tooth_0"
