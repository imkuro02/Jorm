import random

import systems.utils
from affects.affects import Affect
from configuration.config import SKILLS, ActorStatusType, MsgType, StaticRooms, StatType
from custom import loader
from skills.manager import get_user_skill_level_as_index, use_skill
from systems.utils import REFTRACKER


class AI:
    def __init__(self, actor):
        self.actor = actor
        # self.target = None
        self.prediction_target = None
        self.prediction_skill = None
        self.prediction_item = None
        self.prediction_override = ""

        # some skills can be used without ending your turn, for example most buffs
        # if this value is true, then you are allowed to use multiple skills per turn
        # if its false then your turn ends regardless
        self.can_use_skills_without_ending_turn = False
        # all AI is set to false, except player AI'

        REFTRACKER.add_ref(self)

    def initiative(self):
        if self.actor.room.combat.round == 1:
            if self.actor.on_start_skills_use != None:
                skill, lvl = self.actor.on_start_skills_use.split("=")
                skill = str(skill).strip("")
                lvl = int(lvl)
                self.actor.skill_manager.learn(skill_id=skill, amount=lvl)
                self.predict_use_best_skill(skill_override=skill)
                self.use_prediction(no_checks=True)
                self.actor.skill_manager.unlearn(skill_id=skill, amount=lvl)
                self.clear_prediction()

        
        
        self.predict_use_best_skill()

        #roll = random.choice([0,1])
        #if roll == 0:
        #    self.clear_prediction()
        
        # debug = f'{self.actor.name}, {self.prediction_skill}, {self.prediction_target}'
        # self.actor.simple_broadcast(debug,debug)

    def die(self):
        if self.actor.on_death_skills_use != None:
            skill, lvl = self.actor.on_death_skills_use.split("=")
            skill = str(skill).strip("")
            lvl = int(lvl)
            self.actor.skill_manager.learn(skill_id=skill, amount=lvl)
            self.predict_use_best_skill(skill_override=skill)
            self.use_prediction(no_checks=True)
            self.actor.skill_manager.unlearn(skill_id=skill, amount=lvl)
            self.clear_prediction()
            
        pass

    def has_prediction(self):
        if self.prediction_target == None:
            return False
        if self.prediction_skill == None and self.prediction_item == None:
            return False
        return True

    def override_prediction(self, prediction_string=""):
        self.prediction_override = prediction_string

    def get_prediction_string(self, who_checks):
        # return ''
        if self.prediction_override != "":
            return self.prediction_override

        aff_appends = []
        include_prediction = True
        for aff in self.actor.affect_manager.affects.values():
            # affects like stun when at 0 will not do anything but display
            # the aff is over, so when something is at 0 it wont trigger on actor turn
            # and therefor should not display
            # if aff.turns == 0:
            #    continue
            if aff.get_prediction_string_append != None:
                aff_appends.append(aff.get_prediction_string_append)
            if aff.get_prediction_string_clear == True:
                include_prediction = False

        prediction_string = ""
        if include_prediction:
            if type(self.actor).__name__ == "Player":
                # if self.actor.status == ActorStatusType.DEAD:
                #    line = random.choice(['is cooked','wont get up anytime soon','rests in peace'])
                # else:
                #    line = random.choice(['is angry','will do something maybe','will win probably','wont lose','is ready to kill'])
                # prediction_string = line
                prediction_string = ""
            else:
                if not self.has_prediction():
                    prediction_string = ""
                else:
                    prediction_string = (
                        f"(will use {SKILLS[self.prediction_skill]['name']})"
                    )

                    # if self.prediction_target == self.actor:
                    #    prediction_string = f'will use {SKILLS[self.prediction_skill]["name"]}'
                    # elif self.prediction_target == who_checks:
                    #    prediction_string = f'will use {SKILLS[self.prediction_skill]["name"]} on you'
                    # else:
                    #    prediction_string = f'will use {SKILLS[self.prediction_skill]["name"]} on {self.prediction_target.pretty_name()}'
            #
            prediction_string = prediction_string + " "

        return prediction_string + f"{' '.join(aff_appends)}"

    def get_targets(self):
        actors = self.actor.room.combat.participants.values()
        enemies = [
            actor
            for actor in actors
            if actor.party_manager.get_party_id()
            != self.actor.party_manager.get_party_id()
            and actor.status == ActorStatusType.FIGHTING
        ]

        allies = [
            actor
            for actor in actors
            if actor.party_manager.get_party_id()
            == self.actor.party_manager.get_party_id()
            and actor.status == ActorStatusType.FIGHTING
        ]
        return allies, enemies

    def get_skills(self, for_prediction=False, combat_only_skills=True):
        skills = []
        # if for prediction is true, be able to pick skills that are available NEXT TURN
        for skill_id in self.actor.skill_manager.skills:
            if combat_only_skills and not SKILLS[skill_id]["can_use_in_combat"]:
                continue
            if skill_id in self.actor.cooldown_manager.cooldowns:
                if (
                    for_prediction
                    and self.actor.cooldown_manager.cooldowns[skill_id] > 1
                ):
                    # systems.utils.debug_print('WHAT,,',self.actor.cooldown_manager.cooldowns[skill_id])
                    continue
                if not for_prediction:
                    # systems.utils.debug_print('not for prediction!_')
                    continue
            if self.actor.skill_manager.skills[skill_id] <= 0:
                # systems.utils.debug_print('WHAT')
                continue
            skills.append(skill_id)
        return skills

    def clear_prediction(self):
        # systems.utils.debug_print(self.actor.name, 'prediction cleared')
        self.prediction_target = None
        self.prediction_skill = None
        self.prediction_item = None

    def use_prediction(self, no_checks=False):
        target = self.prediction_target

        # if self.prediction_target == self.actor and self.target != None and self.target in self.actor.room.actors.values():
        #    target = self.target
        # else:
        #    self.target = None

        if self.prediction_item != None:
            if self.prediction_item.use(self.actor, target):
                self.clear_prediction()
                # self.predict_use_best_skill()
                self.actor.finish_turn()
                return True

        if self.prediction_skill != None:
            if use_skill(
                self.actor, target, self.prediction_skill, no_checks=no_checks
            ):
                used_skill = self.prediction_skill
                self.clear_prediction()
                # self.predict_use_best_skill()
                if self.can_use_skills_without_ending_turn:
                    if SKILLS[used_skill]["end_turn"]:
                        self.actor.finish_turn()
                    self.predict_use_best_skill()
                else:
                    self.actor.finish_turn()
                return True

        # debug = f'skill {self.prediction_skill}, target {self.prediction_target}'
        # self.actor.simple_broadcast(debug,debug)
        return False

    def predict_use_best_skill(
        self, offensive_only=False, for_prediction=True, skill_override=None
    ):
        self.prediction_target = None
        self.prediction_skill = None

        # if self.prediction_skill != None:
        #    return

        if self.actor.room == None:
            return False

        if self.actor.room.combat == None:
            return False

        allies, enemies = self.get_targets()
        skills = self.get_skills(for_prediction=for_prediction, combat_only_skills=True)
        # systems.utils.debug_print(self.actor.name,skills)
        # try to use a skill 5 times, if it fails return false
        # return true if you managed to use a skill

        if skill_override != None:
            skills = [skill_override]

        for i in range(0, 20):
            if skills == []:
                break

            skill_to_use = random.choice(skills)

            targets = []

            if offensive_only:
                if not SKILLS[skill_to_use]["is_offensive"]:
                    continue

            if "swing" == skill_to_use and i < 5:
                continue

            if i > 15:
                skill_to_use = "swing"

            if SKILLS[skill_to_use]["is_offensive"]:
                targets = enemies
            else:
                targets = allies

            if targets == []:
                continue

            target = self.actor

            if SKILLS[skill_to_use]["target_others_is_valid"]:
                target = random.choice(targets)
                for t in targets:
                    if t == self.actor:
                        continue
                    if (
                        t.stat_manager.stats[StatType.THREAT]
                        >= target.stat_manager.stats[StatType.THREAT]
                    ):
                        target = t

            # systems.utils.debug_print(self.actor.name, 'prediction target:', target.name)

            # systems.utils.debug_print(target, skill_to_use)
            self.prediction_target = target
            self.prediction_skill = skill_to_use
            # for i in self.actor.room.combat.participants.values():
            #    i.sendLine(f'{self.actor.pretty_name()} {self.get_prediction_string(i)}')
            return True
        return False

    """
    def use_best_skill(self, offensive_only = False):
        if self.actor.room.combat == None:
            return


        allies, enemies = self.get_targets()
        skills = self.get_skills()
        self.actor.sendLine('use_best_skill, will use these skills ' + str(skills), msg_type = [MsgType.DEBUG])

        # try to use a skill 5 times, if it fails return false
        # return true if you managed to use a skill
        for i in range(0,20):

            if skills == []:
                self.actor.sendLine('no valid skills!!', msg_type = [MsgType.DEBUG])
                break

            skill_to_use = random.choice(skills)

            targets = []

            if 'swing' == skill_to_use and i<15:
                self.actor.sendLine('cant swing', msg_type = [MsgType.DEBUG])
                continue

            if i>=15:
                skill_to_use = 'swing'
                self.actor.sendLine('will swing', msg_type = [MsgType.DEBUG])

            if offensive_only:
                if not SKILLS[skill_to_use]['is_offensive']:
                    continue

            if SKILLS[skill_to_use]['is_offensive']:
                targets = enemies
            else:
                targets = allies

            if targets == []:
                self.actor.sendLine('no targets', msg_type = [MsgType.DEBUG])
                continue

            #target = random.choice(targets)
            target = random.choice(targets)
            for t in targets:
                if t.stat_manager.stats[StatType.THREAT] > target.stat_manager.stats[StatType.THREAT]:
                    target = t

            if use_skill(self.actor, target, skill_to_use) == True:
                self.actor.finish_turn()
                return True
            else:
                skills.remove(skill_to_use)
                self.actor.sendLine(f'Skill failed: s:{skill_to_use} t:{target.name} ts:{targets}', msg_type = [MsgType.DEBUG])

            self.actor.sendLine('Didnt exit skill properly', msg_type = [MsgType.DEBUG])
            self.actor.sendLine(f's:{skill_to_use} t:{target.name} ts:{targets}', msg_type = [MsgType.DEBUG])

            #skills.remove(skill_to_use)

        self.actor.simple_broadcast(f'You do nothing',f'{self.actor.pretty_name()} does nothing')
        self.actor.finish_turn()
        return False
    """

    def tick(self):
        if self.actor.factory.ticks_passed <= 3:
            return False

        # if none of these checks exit the loop, then that indicates this enemy is in combat
        if self.actor.room == None:
            return False

        if self.actor.status == ActorStatusType.NORMAL:
            # self.wander()
            return False

        if self.actor.room.combat == None:
            return False

        if self.actor.room.combat.current_actor != self.actor:
            return False

        if self.actor.room.combat.time_since_turn_finished <= int(10):
            return False

        return True


class PlayerAI(AI):
    def __init__(self, actor):
        super().__init__(actor)
        self.can_use_skills_without_ending_turn = True

    def use_prediction(self, no_checks=False):
        if super().use_prediction(no_checks=no_checks):
            return True
        # self.actor.simple_broadcast('You do nothing!', f'{self.actor.pretty_name()} does nothing!')
        return False

    def die(self):
        return

    def initiative(self):
        return

    def tick(self):
        # early return if not in combat
        if not super().tick():
            return

        if self.has_prediction():
            self.use_prediction()
            self.clear_prediction()

        return


class EnemyAI(AI):
    def use_prediction(self, no_checks=False):
        if super().use_prediction(no_checks=no_checks):
            return True

        self.actor.simple_broadcast(
            "You do nothing!", f"{self.actor.pretty_name()} does nothing!"
        )
        # self.predict_use_best_skill()
        self.actor.finish_turn()
        return False

    def tick(self):
        if not super().tick():
            return

        self.use_prediction()


def get_ai(ai_name):
    _ai = AI(None)
    available_ai = loader.load_customs(path="custom.ai", object=_ai)
    available_ai.append(PlayerAI)
    available_ai.append(EnemyAI)
    for i in available_ai:
        # print(f"{ai_name}AI", i.__name__)
        if f"{ai_name}AI" == i.__name__:
            # print(f"{ai_name}AI FOUND")
            return i
    # systems.utils.debug_print(f"cannot find {ai_name}AI, returning EnemyAI")
    return EnemyAI
