import copy
import random

import actors.ai
import systems.utils
from actors.actor import Actor
from configuration.config import ENEMIES, ITEMS, NPCS, ActorStatusType, StatType

# from custom import loader as custom_loader
from items.manager import load_item
from systems.dialog import Dialog
from systems.quest import OBJECTIVE_TYPES, ObjectiveCountProposal


def create_npc(room, npc_id, spawn_for_lore=False):
    room = room
    name = "None"
    desc = None
    stats = None
    loot = None
    skills = None
    tree = None
    ai = None
    can_start_fights = False
    dont_join_fights = False
    on_death_skills_use = None
    on_start_skills_use = None

    # if npc_id not in ENEMIES:
    #    return

    if npc_id in ENEMIES:
        # names = 'Auxy Niymiae Tanni Rahji Rahj Rahjii Redpot Kuro Christine Adne Ken Thomas Sandra Erling Viktor Wiktor Sam Dan'
        # old_name_not_used = 'Arr\'zTh-The\'RchEndrough'
        # name = random.choice(names.split())
        name = systems.utils.generate_name() + " The " + ENEMIES[npc_id]["name"]
        desc = ENEMIES[npc_id]["description"]
        stats = ENEMIES[npc_id]["stats"]
        _loot = ENEMIES[npc_id]["loot"]
        skills = ENEMIES[npc_id]["skills"]
        ai = ENEMIES[npc_id]["ai"]
        can_start_fights = ENEMIES[npc_id]["can_start_fights"]
        dont_join_fights = ENEMIES[npc_id]["dont_join_fights"]

        on_death_skills_use = ENEMIES[npc_id]["on_death_skills_use"]
        on_start_skills_use = ENEMIES[npc_id]["on_start_skills_use"]

        loot = _loot  # {}
        """
        for i in ITEMS:
            if 'requirements' in ITEMS[i]:
                match abs(ITEMS[i]['requirements']['lvl'] - stats[StatType.LVL]):
                    case 0:
                        loot[i] = 0.01
                    case 1:
                        loot[i] = 0.009
                    case 2:
                        loot[i] = 0.008
                    case 3:
                        loot[i] = 0.007
                    case 5:
                        loot[i] = 0.006
                    case 6:
                        loot[i] = 0.005
        for i in _loot:
            loot[i] = _loot[i]
        """

    if npc_id in NPCS:
        # name =      NPCS[npc_id]['name']
        # desc =      NPCS[npc_id]['description']
        tree = copy.deepcopy(NPCS[npc_id]["tree"])

    npc_class = Enemy
    if npc_id in ENEMIES:
        npc_class = Enemy
    if npc_id in NPCS:
        npc_class = Npc

    my_npc = npc_class(
        npc_id=npc_id,
        ai=ai,
        name=name,
        description=desc,
        room=room,
        stats=stats,
        loot=loot,
        skills=skills,
        dialog_tree=tree,
        can_start_fights=can_start_fights,
        dont_join_fights=dont_join_fights,
        on_death_skills_use=on_death_skills_use,
        on_start_skills_use=on_start_skills_use,
    )

    """
    npc_class = custom_loader.compare_replace_npcs(my_npc)

    my_npc = npc_class(
        npc_id=npc_id,
        ai=ai,
        name=name,
        description=desc,
        room=room,
        stats=stats,
        loot=loot,
        skills=skills,
        dialog_tree=tree,
        can_start_fights=can_start_fights,
        dont_join_fights=dont_join_fights,
        on_death_skills_use=on_death_skills_use,
        on_start_skills_use=on_start_skills_use,
    )
    """

    return my_npc


class Npc(Actor):
    def __init__(
        self,
        npc_id=None,
        ai=None,
        name=None,
        description=None,
        room=None,
        stats=None,
        loot=None,
        skills=None,
        dialog_tree=None,
        can_start_fights=False,
        dont_join_fights=True,
        on_death_skills_use=None,
        on_start_skills_use=None,
    ):
        super().__init__(
            name=name,
            ai=ai,
            description=description,
            room=room,
        )

        self.on_death_skills_use = on_death_skills_use
        self.on_start_skills_use = on_start_skills_use

        # this script is responsible for setting the dialog tree aswell as appending append_to
        # probably should be moved sometime into dialog.py
        self.dialog_tree = dialog_tree
        if self.dialog_tree != None:
            for d in self.dialog_tree:
                if "append_to" in self.dialog_tree[d]:
                    location = self.dialog_tree[d]["append_to"]
                    if "dialog" in self.dialog_tree[d]:
                        if "dialog" not in self.dialog_tree[location]:
                            self.dialog_tree[location]["dialog"] = []
                        for i in self.dialog_tree[d]["dialog"]:
                            self.dialog_tree[location]["dialog"].append(i)

                    if "options" in self.dialog_tree[d]:
                        if "options" not in self.dialog_tree[location]:
                            self.dialog_tree[location]["options"] = []
                        for i in self.dialog_tree[d]["options"]:
                            self.dialog_tree[location]["options"].append(i)

        self.npc_id = npc_id

        self.can_start_fights = can_start_fights
        self.dont_join_fights = dont_join_fights

        if stats != None:
            self.stat_manager.stats = {**self.stat_manager.stats, **stats}
            self.stat_manager.stats[StatType.HPMAX] = self.stat_manager.stats[
                StatType.HP
            ]
            # self.stat_manager.stats[StatType.MPMAX] = self.stat_manager.stats[StatType.MP]
            self.stat_manager.stats[StatType.PHYARMORMAX] = self.stat_manager.stats[
                StatType.PHYARMOR
            ]
            self.stat_manager.stats[StatType.MAGARMORMAX] = self.stat_manager.stats[
                StatType.MAGARMOR
            ]

        if loot != None:
            self.loot = copy.deepcopy(loot)
        else:
            self.loot = {}

        if skills != None:
            self.skill_manager.skills = copy.deepcopy(skills)

    def talk_to(self, talker):
        if not super().talk_to(talker):
            return
        # if returned true, start dialog
        talker.simple_broadcast(
            f"You approach {self.pretty_name()}",
            f"{talker.pretty_name()} approaches {self.pretty_name()}.",
        )
        talker.current_dialog = Dialog(talker, self, self.dialog_tree)
        talker.current_dialog.print_dialog()
        # return True

    # this function returns whether the npc has a quest to hand out or turn in / both
    # actor_to_compare is the player that is checking
    def get_important_dialog(self, actor_to_compare, return_dict=False):
        has_quest_to_start = False
        has_quest_to_turn_in = False
        quest_man = actor_to_compare.quest_manager
        output = ""

        if self.dialog_tree == None:
            return False

        for branch in self.dialog_tree.values():
            if "options" not in branch:
                continue
            # systems.utils.debug_print(branch['options'])
            for option in branch["options"]:
                # systems.utils.debug_print('!')
                if "quest_check" not in option:
                    continue

                if "quest_start" not in option and "quest_turn_in" not in option:
                    continue

                # systems.utils.debug_print('checking, ',option['quest_check'])
                check_valid = True
                for quest_to_check in option["quest_check"]:
                    not_valid = (
                        quest_man.check_quest_state(quest_to_check["id"])
                        != quest_to_check["state"]
                    )
                    # systems.utils.debug_print(not_valid, quest_man.check_quest_state(quest_to_check['id']) , quest_to_check['state'])
                    if not_valid:
                        check_valid = False

                    # output = output + quest_to_check['id'] + ': ' + quest_to_check['state'] + ' ### '

                if check_valid:
                    if "quest_start" in option:
                        has_quest_to_start = True
                    if "quest_turn_in" in option:
                        has_quest_to_turn_in = True

        if return_dict:
            return {
                "quest_not_started": has_quest_to_start,
                "quest_turn_in": has_quest_to_turn_in,
            }

        if has_quest_to_start and has_quest_to_turn_in:
            output = output + "\nHas both a quest to start and a quest to turn in"
        else:
            if has_quest_to_start:
                output = output + "\nHas a quest to start"
            if has_quest_to_turn_in:
                output = output + "\nHas a quest to turn in"

        return output

    def tick(self):
        super().tick()
        # try:
        if self.ai != None:
            self.ai.tick()
        # except Exception as e:
        #    systems.utils.debug_print(self.name, e)

    def drop_loot_on_ground(self):
        for item in self.loot:
            roll = random.random()
            if roll >= self.loot[item]:
                continue

            new_item = load_item(item)
            self.simple_broadcast("", f"{new_item.name} hits the ground with a thud.")
            self.room.inventory_manager.add_item(new_item)

    def drop_loot(self, actor, room):
        all_items = ITEMS

        for item in self.loot:
            if self.loot[item] != 1:
                roll = random.randrange(1, self.loot[item])
                if roll != 1:
                    continue

            new_item = load_item(item)

            if actor.inventory_manager.add_item(new_item):
                actor.sendLine(
                    f"You loot {new_item.name} (1 in {self.loot[item]} chance)"
                )
            else:
                actor.sendLine(
                    f"Your inventory is full, {new_item.name} has been dropped on the ground"
                )
                room.inventory_manager.add_item(new_item)

    def die(self):
        if self.room == None:
            super().die()
            return
        if self.room.combat == None:
            super().die()
            return
        if self not in self.room.combat.participants.values():
            super().die()
            return

        room = self.room
        participants = room.combat.participants.values()

        super().die(unload=False)

        for actor in participants:
            if type(actor).__name__ == "Player":
                if actor.status == ActorStatusType.DEAD:
                    continue
                actor.gain_exp(self.stat_manager.stats[StatType.EXP])
                self.drop_loot(actor, room)
                # self.drop_loot_on_ground()
                proposal = ObjectiveCountProposal(
                    OBJECTIVE_TYPES.KILL_X, self.npc_id, 1
                )
                actor.quest_manager.propose_objective_count_addition(proposal)

        del self.room.actors[self.id]
        if self.room.combat != None:
            if self.id in self.room.combat.participants:
                del self.room.combat.participants[self.id]

        super().unload()

    def set_turn(self):
        super().set_turn()


class Enemy(Npc):
    def __init__(
        self,
        npc_id=None,
        ai=None,
        name=None,
        description=None,
        room=None,
        stats=None,
        loot=None,
        skills=None,
        dialog_tree=None,
        can_start_fights=False,
        dont_join_fights=True,
        on_death_skills_use=None,
        on_start_skills_use=None,
    ):
        super().__init__(
            npc_id=npc_id,
            ai=ai,
            name=name,
            description=description,
            room=room,
            stats=stats,
            loot=loot,
            skills=skills,
            dialog_tree=dialog_tree,
            can_start_fights=can_start_fights,
            dont_join_fights=dont_join_fights,
            on_death_skills_use=on_death_skills_use,
            on_start_skills_use=on_start_skills_use,
        )


actors.ai.create_npc = create_npc
systems.utils.create_npc = create_npc
