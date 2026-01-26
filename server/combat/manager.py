import random

import systems.utils
from combat.combat_event import CombatEvent
from combat.damage_event import Damage
from configuration.config import SKILLS, ActorStatusType, Color, DamageType, StatType
from systems.utils import unload


class Combat:
    def __init__(self, room, participants):
        self.room = room
        self.participants = participants
        self.order = []
        self.current_actor = None
        self.time_since_turn_finished = 0
        self.round = 1
        self.turn = 0
        self.combat_active = True

        # reset threat
        for p in self.participants.values():
            if type(p).__name__ == "Player":
                p.set_base_threat()
                p.stat_manager.stats[StatType.INITIATIVE] = 0
            else:
                p.set_base_threat()
                p.stat_manager.stats[StatType.INITIATIVE] = 0
                for skill_id in p.skill_manager.skills:
                    cool = SKILLS[skill_id]["script_values"]["cooldown"][0] - 1
                    p.cooldown_manager.add_cooldown(skill_id, cool)
                # p.predict_use_best_skill()
            p.ai.clear_prediction()

        for p in self.room.actors.values():
            if type(p).__name__ == "Player":
                p.sendLine("@tipA fight has started!@back")

    def unload(self):
        for p in self.participants.values():
            p.ai.clear_prediction()
        self.room.combat = None
        unload(self)

    def add_participant(self, participant):
        participant.status = ActorStatusType.FIGHTING
        if participant.id in self.participants:
            return  # already participating in combat
        self.participants[participant.id] = participant
        participant.simple_broadcast(
            f"You join the combat",
            f"{participant.pretty_name()} joins the combat",
        )
        # reset threat to 0 at start of combat
        participant.set_base_threat()
        participant.ai.clear_prediction()

    def tick(self):
        if self.current_actor == None:
            return

        self.time_since_turn_finished += 1

        participating_parties = []
        for i in self.participants.values():
            if (
                i.status == ActorStatusType.FIGHTING
                and i.party_manager.get_party_id() not in participating_parties
            ):
                participating_parties.append(i.party_manager.get_party_id())

        if len(participating_parties) <= 1:
            self.combat_over()
            return
        # if len(self.participants) == 0:
        #    self.combat_over()
        #    return

        # systems.utils.debug_print(self.time_since_turn_finished, len(self.participants))
        if self.time_since_turn_finished == 30 * 20:
            if type(self.current_actor).__name__ == "Player":
                self.current_actor.simple_broadcast(
                    "@yellowYour turn is over in 10 seconds.@normal",
                    f"{self.current_actor.name}'s turn is over in 10 seconds.",
                )

        if self.time_since_turn_finished >= 30 * 30:
            if type(self.current_actor).__name__ == "Player":
                self.current_actor.simple_broadcast(
                    "@yellowYou missed your turn.@normal",
                    f"{self.current_actor.name} missed their turn.",
                )

            self.time_since_turn_finished = 0
            self.next_turn()

        """
        team1_died = True
        team2_died = True
        for i in self.participants.values():
            if i.status != 'dead' and type(i).__name__ == "Player":
                team1_died = False
            if i.status != 'dead' and type(i).__name__ == "Enemy":
                team2_died = False
            i.tick()
        """
        participants = []
        for i in self.participants.values():
            if i.room != self.room:
                continue
            participants.append(i)

        for i in participants:
            if i in self.participants.values():
                i.tick()
            else:
                systems.utils.debug_print(
                    f"combat manager cannot find participant: {i} is not here"
                )

        # if team1_died or team2_died:
        #    self.combat_over()

        # if self.current_actor.room != self.room:

        if self.current_actor not in self.participants.values():
            systems.utils.debug_print(self.current_actor, "not here")
            self.next_turn()
            return

        if self.current_actor.status == ActorStatusType.NORMAL:
            systems.utils.debug_print(self.current_actor.name, "removed from combat")
            if self.current_actor.id in self.participants:
                # self.participants[self.current_actor.id].status = ActorStatusType.NORMAL
                del self.participants[self.current_actor.id]
            self.next_turn()
            return

        if self.current_actor.status == ActorStatusType.DEAD:
            self.next_turn()
            return

    def combat_over(self):
        if self.combat_active:
            self.combat_active = False
        else:
            self.combat_active = False
            return

        participants = self.participants.values()
        for i in participants:
            if type(i).__name__ == "Player":
                i.sendLine("@yellowCombat over!@normal")
                # i.heal(value = 99999)
            else:
                if i.status != ActorStatusType.DEAD:
                    i.stat_manager.stats[StatType.HP] = 9999999999999
                    # i.heal(value = 99999)
                    i.cooldown_manager.unload_all_cooldowns()
                    i.affect_manager.unload_all_affects()
                    i.heal(value=99999)

            if i.party_manager.party != None:
                one_alive = False
                for par in i.party_manager.party.participants.values():
                    if par.status != ActorStatusType.DEAD:
                        one_alive = True

                # if one_alive and self.round:
                #    if i.status == ActorStatusType.DEAD:
                #        i.stat_manager.stats[StatType.HP] = 1
                #        i.simple_broadcast(f'You get up again.', f'{i.pretty_name()} gets up again.')
                #        i.status = ActorStatusType.NORMAL
                #        i.affect_manager.unload_all_affects(forced = False)
                #        #i.set_turn()

            if i.status != ActorStatusType.DEAD:
                i.status = ActorStatusType.NORMAL
                # threat = i.stat_manager.stats[StatType.THREAT]
                # threat = int(threat/2)
                # i.heal(value = threat, silent = True)
                # i.heal(heal_hp = False, heal_mp = False, value = 10000, silent = True)

        self.room.combat = None
        systems.utils.debug_print("combat over")
        # self.unload()

    def next_turn(self):
        # systems.utils.debug_print('next turn', self.turn)
        actors = []
        for actor in self.participants.values():
            actors.append(actor)
        for actor in actors:
            if actor.status == ActorStatusType.DEAD:
                continue
            actor.stat_manager.hp_mp_clamp_update()

        participating_parties = []
        for i in self.participants.values():
            if (
                i.status == ActorStatusType.FIGHTING
                and i.party_manager.get_party_id() not in participating_parties
            ):
                participating_parties.append(i.party_manager.get_party_id())

        if len(participating_parties) <= 1:
            self.combat_over()
            return

        # systems.utils.debug_print(participating_parties)
        # if len(participating_parties) <= 1 and self.turn >= 1:
        #   self.combat_over()
        #   return

        self.time_since_turn_finished = 0
        if len(self.order) == 0:
            self.initiative()
            return

        if self.order[0].status == ActorStatusType.DEAD:
            self.order.pop(0)
            self.next_turn()
            return

        self.current_actor = self.order[0]
        self.order.pop(0)

        if self.current_actor.room != self.room:
            self.next_turn()
            return

        self.current_actor.set_turn()
        self.turn += 1

    def initiative(self):
        show_turns_and_stuff = False

        for i in self.participants.values():
            if i.status != ActorStatusType.DEAD:
                self.order.append(i)
        self.order.sort(
            key=lambda x: random.randint(0, x.stat_manager.stats[StatType.FLOW]),
            reverse=True,
        )

        if self.order == []:
            self.combat_over()
            return

        if show_turns_and_stuff:
            for par in self.participants.values():
                if type(par).__name__ != "Player":
                    continue
                order = ""
                for i in self.order:
                    if par == i:
                        order = order + "YOU" + " -> "
                    else:
                        order = order + i.pretty_name() + " -> "

                order = (
                    ("\n" * 1)
                    + f"{Color.COMBAT_TURN}ROUND {self.round}...{Color.NORMAL} "
                    + "".join(order.rsplit(" -> ", 1))
                )
                # par.sendLine(('#'*80)+'\n'+order)
                par.sendLine(order)

        for i in self.order:
            if i.room != self.room:
                continue
            i.status = ActorStatusType.FIGHTING

        # if len(self.order) == 0:
        #    self.combat_over()
        #    return

        # only add predictions at the very first round of combat
        # after that predictions get rolled after turn end
        for par in self.participants.values():
            par.ai.initiative()

            # par.ai.predict_use_best_skill()
        if show_turns_and_stuff:
            for par in self.participants.values():
                par.show_prompts(self.participants.values())
                par.sendLine("")

        self.round += 1
        self.next_turn()
        # self.current_actor = self.order[0]
        # self.current_actor.set_turn()
