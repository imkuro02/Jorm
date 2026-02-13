import random

import systems.utils
from combat.damage_event import Damage
from configuration.config import ActorStatusType, DamageType, StatType
from combat.combat_event import CombatEvent

class Affect:
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        resisted_by=None,
        get_prediction_string_append=None,
        get_prediction_string_clear=False,
        dispellable=True,
    ):
        self.affect_target_actor = affect_target_actor
        self.affect_source_actor = affect_source_actor

        self.affect_manager = self.affect_target_actor.affect_manager

        # self.affect_manager = affect_manager
        # self.affect_target_actor = self.affect_manager.actor

        self.name = name
        self.description = description
        # the armor type to resist
        self.resisted_by = resisted_by
        # get prediction string will append this text
        self.get_prediction_string_append = get_prediction_string_append
        # if this is true, the prediction string will be empty and only include affects
        self.get_prediction_string_clear = get_prediction_string_clear
        self.turns = turns

        self.dispellable = dispellable

    def pretty_name(self):
        if self.turns == 0:
            return f'{self.name}'
        return f'{self.name} x{self.turns}' 

    def merge_request(self, affect_to_merge):
        return False

    # def info(self):
    #    return f'{self.name:<15} {self.turns:<3} {self.description}\n'

    # called when applied
    def on_applied(self, silent=False):
        if self.resisted_by != None:
            roll = random.randint(1, 100)
            chance = 0
            if (
                self.affect_manager.actor.stat_manager.stats[StatType.MAGARMOR] <= 0
                and self.affect_manager.actor.stat_manager.stats[StatType.PHYARMOR] <= 0
            ):
                chance += 100
            elif self.affect_manager.actor.stat_manager.stats[self.resisted_by] <= 0:
                chance += 50

            if roll >= chance:
                # self.affect_manager.actor.simple_broadcast(
                #    f'You resist {self.name} (rolled {roll}/100 when need under {chance})',
                #    f'{self.affect_manager.actor.pretty_name()} resists {self.name} (rolled {roll}/100 when need under {chance})',
                # )
                self.affect_manager.actor.simple_broadcast(
                    f"You resist {self.name}",
                    f"{self.affect_manager.actor.pretty_name()} resists {self.name}",
                )
                self.affect_manager.pop_affect(self)
                return

        if silent:
            return
        self.affect_manager.actor.simple_broadcast(
            f"You are {self.name}",
            f"{self.affect_manager.actor.pretty_name()} is {self.name}",
        )

    # called when effect is over
    def on_finished(self, silent=False):
        if not silent:
            self.affect_manager.actor.simple_broadcast(
                f"You are no longer {self.name}",
                f"{self.affect_manager.actor.pretty_name()} is no longer {self.name}",
            )
        self.affect_manager.pop_affect(self)

    # called at start of turn
    def set_turn(self):
        self.turns -= 1
        pass

    # called at end of turn
    def finish_turn(self):
        pass

    # called whenever hp updates in any way
    def take_damage_before_calc(self, damage_obj):
        return damage_obj

    def take_damage_after_calc(self, damage_obj):
        return damage_obj

    def deal_damage(self, damage_obj):
        return damage_obj

    def dealt_damage(self, damage_obj):
        return damage_obj

class AffectWellRested(Affect):
    def set_turn(self):
        # only count if not dead and not in combat
        if self.affect_target_actor.status == ActorStatusType.NORMAL:
            self.turns -= 1
        pass

    def take_damage_after_calc(self, damage_obj):
        if self.affect_target_actor.status != ActorStatusType.FIGHTING:
            return damage_obj
        # print(self.affect_target_actor.room.combat.round)
        if self.affect_target_actor.room.combat.round != 2:
            return damage_obj
        if damage_obj.damage_type == DamageType.HEALING:
            return damage_obj
        damage_obj.damage_value = int(damage_obj.damage_value / 2)
        return damage_obj


# this affect takes a skill object before its ran and runs it when affect runs outta time
class AffectDelayedAction(Affect):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        skills_to_use_objects,
    ):
        super().__init__(
            affect_source_actor,
            affect_target_actor,
            name,
            description,
            turns,
            dispellable=False,
        )
        self.skills_to_use_objects = skills_to_use_objects
        self.get_prediction_string_append = f"will {self.skills_to_use_objects[0].name} in {self.turns + 1} turn{'s' if self.turns > 1 else ''}"
        self.get_prediction_string_clear = True

    def set_turn(self):
        super().set_turn()
        self.get_prediction_string_append = f"will {self.skills_to_use_objects[0].name} in {self.turns + 1} turn{'s' if self.turns > 1 else ''}"
        self.get_prediction_string_clear = True
        self.affect_target_actor.simple_broadcast(
            f"You are Charging {self.skills_to_use_objects[0].name}",
            f"{self.affect_target_actor.pretty_name()} is Charging {self.skills_to_use_objects[0].name}",
        )
        self.affect_target_actor.finish_turn()

    def take_damage_before_calc(self, damage_obj: Damage):
        if damage_obj.damage_type not in [DamageType.HEALING, DamageType.CANCELLED]:
            # collect skills to cancel
            skills_to_cancel = []
            for i in self.skills_to_use_objects:
                skills_to_cancel.append(i)

            # reset skills to use on finished 
            self.skills_to_use_objects = []
            # finish the charging
            self.on_finished()

            # run delay use got cancelled on all cancelled skills
            for i in skills_to_cancel:
                i.delay_use_got_cancelled()
            
        # return the damage object for some reason    
        return damage_obj

    def on_finished(self, silent=False):
        super().on_finished(silent)
        if self.affect_target_actor.status != ActorStatusType.FIGHTING:
            return

        for i in self.skills_to_use_objects:
            if i.other.status != ActorStatusType.FIGHTING:
                continue
            i.pre_use(no_delay=True)

        self.affect_target_actor.finish_turn()


class AffectStunned(Affect):
    # called at start of turn
    def set_turn(self):
        super().set_turn()
        self.affect_target_actor.simple_broadcast(
            f"You are too stunned to act!",
            f"{self.affect_target_actor.pretty_name()} is too stunned to act!",
        )
        self.affect_target_actor.finish_turn()

class AffectGuarding(Affect):
    def __init__(self, *args, **kwargs):
        self.heal_power = kwargs['heal_power']
        del kwargs['heal_power']
        super().__init__(*args, **kwargs)
        
        self.got_hit = False


    def set_turn(self):
        super().set_turn()
        
        self.affect_target_actor.simple_broadcast(
            f"You are guarding and cannot act!",
            f"{self.affect_target_actor.pretty_name()} is guarding and cannot act!",
        )
        self.affect_target_actor.finish_turn()

    def take_damage_before_calc(self, damage_obj: Damage):
        if (
            damage_obj.damage_type != DamageType.HEALING
            and damage_obj.damage_type != DamageType.CANCELLED
            and damage_obj.damage_type != DamageType.PURE
        ):
            damage_obj.damage_type = DamageType.CANCELLED
            # damage_obj.damage_taker_actor.room.combat.current_actor = damage_obj.damage_taker_actor
            self.got_hit = True
            self.on_finished()
            # damage_obj.damage_taker_actor.set_turn()
        return damage_obj
        

    def on_finished(self, silent=False):
        if self.got_hit:
            return super().on_finished(silent)
        else:
            power = self.heal_power
            damage_obj1 = Damage(
                damage_taker_actor=self.affect_target_actor,
                damage_source_action=self,
                combat_event=None,
                damage_source_actor=self.affect_target_actor,
                damage_value=int(
                    self.affect_target_actor.stat_manager.stats[StatType.PHYARMORMAX] * power
                ),
                damage_type=DamageType.HEALING,
                damage_to_stat=StatType.PHYARMOR,
            )

            damage_obj2 = Damage(
                damage_taker_actor=self.affect_target_actor,
                damage_source_action=self,
                combat_event=damage_obj1.combat_event,
                damage_source_actor=self.affect_target_actor,
                damage_value=int(
                    self.affect_target_actor.stat_manager.stats[StatType.MAGARMORMAX] * power
                ),
                damage_type=DamageType.HEALING,
                damage_to_stat=StatType.MAGARMOR,
                silent = True
            )

            damage_obj1.run()
            return super().on_finished(silent)



class AffectNightmare(Affect):
    def set_turn(self):
        super().set_turn()
        self.affect_target_actor.simple_broadcast(
            f"You are sleeping and cannot act!",
            f"{self.affect_target_actor.pretty_name()} is sleeping and cannot act!",
        )
        self.affect_target_actor.finish_turn()

    def take_damage_after_calc(self, damage_obj: Damage):
        if (
            damage_obj.damage_type != DamageType.HEALING
            and damage_obj.damage_type != DamageType.CANCELLED
        ):
            damage_obj.damage_taker_actor.room.combat.order.insert(
                0, damage_obj.damage_taker_actor
            )
            
            # not tried yet
            damage_obj.damage_taker_actor.ai.predict_use_best_skill()
            
            
            # damage_obj.damage_taker_actor.room.combat.current_actor = damage_obj.damage_taker_actor
            self.on_finished()
            # damage_obj.damage_taker_actor.set_turn()
        return damage_obj

    def on_finished(self, silent=False):
        return super().on_finished(silent)


class Leech(Affect):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        leech_power,
    ):
        super().__init__(
            affect_source_actor, affect_target_actor, name, description, turns
        )
        self.leech_power = leech_power

    def dealt_damage(self, damage_obj):
        if damage_obj.damage_type != DamageType.PHYSICAL:
            return damage_obj

        if damage_obj.damage_value <= 0:
            return damage_obj

        damage_value = round(damage_obj.damage_value * self.leech_power)

        leech_heal_damage_obj = Damage(
            damage_source_actor=self.affect_target_actor,
            damage_taker_actor=self.affect_target_actor,
            damage_source_action=self,
            damage_value=damage_value,
            damage_type=DamageType.HEALING,
            combat_event=damage_obj.combat_event,
        )


        return damage_obj


class AffectThorns(Affect):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        damage_reflected_power,
    ):
        super().__init__(
            affect_source_actor, affect_target_actor, name, description, turns
        )
        self.damage_reflected_power = damage_reflected_power  # how much in % to reflect

    def take_damage_after_calc(self, damage_obj):
        if damage_obj.damage_type != DamageType.PHYSICAL:
            return damage_obj

        # if damage_obj.damage_value > 0:
        #    return damage_obj

        thorns_damage = Damage(
            damage_source_actor=self.affect_source_actor,
            damage_taker_actor=damage_obj.damage_source_actor,
            damage_source_action=self,
            damage_value=abs(
                int(damage_obj.damage_value * self.damage_reflected_power)
            ),
            damage_type=DamageType.PURE,
            combat_event=damage_obj.combat_event,
        )

        return damage_obj


class AffectArmorReduceToZero(Affect):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        dispellable=False,
        resisted_by=None
    ):
        super().__init__(
            affect_source_actor,
            affect_target_actor,
            name,
            description,
            turns,
            dispellable=dispellable,
            resisted_by=resisted_by,
        )
        self.armor = 0
        self.marmor = 0

    def on_applied(self):
        super().on_applied()
        self.armor = self.affect_target_actor.stat_manager.stats[StatType.PHYARMOR]
        self.affect_target_actor.stat_manager.stats[StatType.PHYARMOR] = 0
        self.marmor = self.affect_target_actor.stat_manager.stats[StatType.MAGARMOR]
        self.affect_target_actor.stat_manager.stats[StatType.MAGARMOR] = 0

        combat_event = CombatEvent()
        damage_obj = Damage(
            damage_source_actor=self.affect_source_actor,
            damage_taker_actor=self.affect_target_actor,
            damage_source_action=self,
            damage_value=self.armor,
            damage_type=DamageType.PURE,
            damage_to_stat=StatType.PHYARMOR,
            dont_proc=True,
            combat_event = combat_event,
        )

        #damage_obj.run()

        damage_obj = Damage(
            damage_source_actor=self.affect_source_actor,
            damage_taker_actor=self.affect_target_actor,
            damage_source_action=self,
            damage_value=self.marmor,
            damage_type=DamageType.PURE,
            damage_to_stat=StatType.MAGARMOR,
            dont_proc=True,
            combat_event = combat_event,
        )

        #damage_obj.run()
        combat_event.run()

    def on_finished(self, silent=False):
        if self.affect_target_actor.status == ActorStatusType.DEAD:
            return super().on_finished(silent)

        self.affect_target_actor.stat_manager.stats[StatType.PHYARMOR] += self.armor
        self.affect_target_actor.stat_manager.stats[StatType.MAGARMOR] += self.marmor

        combat_event = CombatEvent()
        damage_obj = Damage(
            damage_source_actor=self.affect_source_actor,
            damage_taker_actor=self.affect_target_actor,
            damage_source_action=self,
            damage_value=self.armor,
            damage_type=DamageType.HEALING,
            damage_to_stat=StatType.PHYARMOR,
            dont_proc=True,
            combat_event = combat_event,
        )

        #damage_obj.run()

        damage_obj = Damage(
            damage_source_actor=self.affect_source_actor,
            damage_taker_actor=self.affect_target_actor,
            damage_source_action=self,
            damage_value=self.marmor,
            damage_type=DamageType.HEALING,
            damage_to_stat=StatType.MAGARMOR,
            dont_proc=True,
            combat_event = combat_event,
        )

        #damage_obj.run()
        combat_event.run()
        return super().on_finished(silent)


"""
class AffectOvercharge(Affect):
    def __init__(self, affect_source_actor, affect_target_actor, name, description, turns, bonus = 1):
        super().__init__(affect_source_actor, affect_target_actor, name, description, turns)
        self.mp_percentage_lost_damage = bonus
        self.mp_start = 0
        self.mp_end = 0

    def on_applied(self):
        super().on_applied()
        self.mp_start = self.affect_source_actor.stat_manager.stats[StatType.MPMAX]
        self.affect_source_actor.stat_manager.stats[StatType.MP] = self.affect_source_actor.stat_manager.stats[StatType.MPMAX]

    def on_finished(self, silent=False):
        if self.affect_target_actor.status == ActorStatusType.DEAD:
            return super().on_finished(silent)

        self.mp_end = self.affect_source_actor.stat_manager.stats[StatType.MP]

        dmg = int((self.mp_start - self.mp_end) * self.mp_percentage_lost_damage)
        damage_obj = Damage(
            damage_source_actor = self.affect_source_actor,
            damage_taker_actor = self.affect_target_actor,
            damage_source_action = self,
            damage_value = dmg,
            damage_type = DamageType.MAGICAL
        )

        damage_obj.run()
        return super().on_finished(silent)
"""


class AffectDeflectMagic(Affect):
    def __init__(
        self, affect_source_actor, affect_target_actor, name, description, turns
    ):
        super().__init__(
            affect_source_actor, affect_target_actor, name, description, turns
        )

    def take_damage_before_calc(self, damage_obj: Damage):
        if damage_obj.damage_type == DamageType.MAGICAL:
            damage_obj.damage_taker_actor = damage_obj.damage_source_actor
            damage_obj.damage_source_action = self
            damage_obj.damage_type = DamageType.PURE
        return damage_obj


class AffectEthereal(Affect):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        dmg_amp,
    ):
        super().__init__(
            affect_source_actor, affect_target_actor, name, description, turns
        )
        self.dmg_amp = dmg_amp

    def take_damage_before_calc(self, damage_obj: Damage):
        if damage_obj.damage_type == DamageType.PHYSICAL:
            damage_obj.damage_type = DamageType.CANCELLED
            damage_obj.damage_taker_actor.simple_broadcast(
                f"You take no damage because you are ethereal",
                f"{damage_obj.damage_taker_actor.pretty_name()} takes no damage because they are ethereal",
            )

        if damage_obj.damage_type == DamageType.MAGICAL:
            damage_obj.damage_value = int(damage_obj.damage_value * self.dmg_amp)

        return damage_obj

    def deal_damage(self, damage_obj: Damage):
        if damage_obj.damage_type == DamageType.PHYSICAL:
            damage_obj.damage_type = DamageType.CANCELLED
            damage_obj.damage_source_actor.simple_broadcast(
                f"You cannot deal damage since you are ethereal",
                f"{damage_obj.damage_source_actor.pretty_name()} cannot deal damage since they are ethereal",
            )
        return damage_obj


class AffectBoostStat(Affect):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        bonus,
        stat,
    ):
        super().__init__(
            affect_source_actor, affect_target_actor, name, description, turns
        )
        self.bonus = bonus
        self.stat = stat
        self.new_stat = 0

    def on_applied(self):
        super().on_applied()
        self.new_stat = int(
            self.affect_target_actor.stat_manager.stats[self.stat] * self.bonus
        )
        # self.affect_target_actor.stat_manager.stats[self.stat] += self.new_stat
        self.affect_target_actor.stat_manager.gain_stat_points(self.stat, self.new_stat)

    def on_finished(self, silent=False):
        self.affect_target_actor.stat_manager.gain_stat_points(
            self.stat, -self.new_stat
        )
        self.affect_target_actor.stat_manager.hp_mp_clamp_update()
        return super().on_finished(silent)


class AffectStealth(Affect):
    def __init__(
        self, affect_source_actor, affect_target_actor, name, description, turns, bonus
    ):
        super().__init__(
            affect_source_actor, affect_target_actor, name, description, turns
        )
        self.bonus = bonus
        self.new_stat = 0

    def on_applied(self):
        super().on_applied()
        self.new_stat = int(
            self.affect_target_actor.stat_manager.stats[StatType.FLOW] * 1
        )
        self.affect_target_actor.stat_manager.stats[StatType.FLOW] += self.new_stat

    def deal_damage(self, damage_obj: "Damage"):
        self.on_finished(silent=False)
        if damage_obj.damage_type != DamageType.PHYSICAL:
            return damage_obj

        # systems.utils.debug_print(systems.utils.get_object_parent(damage_obj.damage_source_action))
        # return damage_obj
        if systems.utils.get_object_parent(damage_obj.damage_source_action) != "Skill":
            return damage_obj

        if damage_obj.damage_source_action.skill_id != "stab":
            return damage_obj

        damage_obj.damage_value = int(damage_obj.damage_value * self.bonus)
        return damage_obj

    def take_damage_before_calc(self, damage_obj: "Damage"):
        if damage_obj.damage_type != DamageType.HEALING:
            self.on_finished(silent=False)
        return damage_obj

    def on_finished(self, silent=False):
        self.affect_target_actor.stat_manager.stats[StatType.FLOW] -= self.new_stat
        self.affect_target_actor.stat_manager.hp_mp_clamp_update()
        return super().on_finished(silent)


class AffectBleed(Affect):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        resisted_by,
        damage,
    ):
        super().__init__(
            affect_source_actor,
            affect_target_actor,
            name,
            description,
            turns,
            resisted_by,
        )
        self.damage = damage

    # def take_damage_after_calc(self, damage_obj):
    #    if damage_obj.damage_type == DamageType.HEALING:
    #        self.on_finished()
    #    return damage_obj

    def merge_request(self, affect_to_merge):
        # if affect_to_merge.turns > self.turns:
        # if self.damage < affect_to_merge.damage:
        #    self.damage = affect_to_merge.damage
        self.damage += affect_to_merge.damage
        self.turns = affect_to_merge.turns
        # if affect_to_merge.damage < self.damage:
        #    return False
        return True

    def set_turn(self):
        super().set_turn()
        damage_obj = Damage(
            damage_source_actor=self.affect_source_actor,
            damage_taker_actor=self.affect_target_actor,
            damage_source_action=self,
            damage_value=self.damage,
            damage_type=DamageType.PHYSICAL,
        )

        # self.damage = int(self.damage*0.5)

        damage_obj.run()


class AffectDOT(Affect):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        damage_value,
        damage_type,
        damage_to_stat,
    ):
        super().__init__(
            affect_source_actor, affect_target_actor, name, description, turns
        )
        self.damage_value = damage_value
        self.damage_type = damage_type
        self.damage_to_stat = damage_to_stat

    def set_turn(self):
        super().set_turn()
        damage_obj = Damage(
            damage_source_actor=self.affect_source_actor,
            damage_taker_actor=self.affect_target_actor,
            damage_source_action=self,
            damage_value=self.damage_value,
            damage_type=self.damage_type,
            damage_to_stat=self.damage_to_stat,
        )

        damage_obj.run()


class AffectPromise(Affect):
    # def merge_request(self, affect_to_merge):
    #    return True

    def on_applied(self):
        super().on_applied()
        self.accumulated_damage = 0
        self.hp = self.affect_target_actor.stat_manager.stats[StatType.HP]
        self.pa = self.affect_target_actor.stat_manager.stats[StatType.PHYARMOR]
        self.ma = self.affect_target_actor.stat_manager.stats[StatType.MAGARMOR]

    def on_finished(self, silent=False):
        super().on_finished(silent=False)
        if self.accumulated_damage <= 0:
            return

        damage_obj = Damage(
            damage_source_actor=self.affect_target_actor,
            damage_taker_actor=self.affect_target_actor,
            damage_source_action=self,
            damage_value=self.accumulated_damage,
            damage_type=DamageType.PURE,
        )

        damage_obj.run()

    def take_damage_after_calc(self, damage_obj):
        # self.affect_target_actor.simple_broadcast('absorbed','absorbed')
        # if self.turns <= 0:
        #    return damage_obj

        damage_obj.damage_value = abs(damage_obj.damage_value)
        if damage_obj.damage_type == DamageType.HEALING:
            self.accumulated_damage -= damage_obj.damage_value
        elif damage_obj.damage_type != DamageType.CANCELLED:
            self.accumulated_damage += damage_obj.damage_value

        self.affect_target_actor.stat_manager.stats[StatType.HP] = self.hp
        self.affect_target_actor.stat_manager.stats[StatType.PHYARMOR] = self.pa
        self.affect_target_actor.stat_manager.stats[StatType.MAGARMOR] = self.ma

        # out = f'accumulated damage is {self.accumulated_damage}'
        # self.affect_target_actor.simple_broadcast(out,out)

        return damage_obj

class AffectSummoner(Affect):
    def __init__(self, *args, **kwargs):
        self.summoned_actor = kwargs['summoned_actor']
        del kwargs['summoned_actor']
        super().__init__(*args, **kwargs)
        
    def summon_checks(self):
        if self.summoned_actor == None:
            return False
        if self.summoned_actor.status == ActorStatusType.DEAD:
            return False
        if self.summoned_actor.room == None:
            return False
        return True

    def set_turn(self):
        super().set_turn()
        if not self.summon_checks():
            return

        if self.summoned_actor.room != self.affect_target_actor.room:
            self.affect_target_actor.room.move_actor(self.summoned_actor)

    def on_finished(self,silent=False):
        super().on_finished(silent=silent)
        if not self.summon_checks():
            return
        self.summoned_actor.die()
        

# XD Reforges


class AffectReforge(Affect):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        source_item=None,
        reforge_variables=None,
        dispellable=False,
    ):
        super().__init__(
            affect_source_actor,
            affect_target_actor,
            name,
            description,
            turns,
            dispellable=dispellable,
        )
        self.source_item = source_item
        self.reforge_variables = reforge_variables
        # need to double check if afflictions get messed up when unequipping shit
        # during "practice" and "skills" commands
        # import random
        # self.description = str(random.randint(0,99999))

    def merge_request(self, affect_to_merge):
        # check if has this attribute, if so then the affliction is caused by an equipment
        if hasattr(affect_to_merge, "source_item"):
            # if the items are different, dont merge but overwrite
            if self.source_item != affect_to_merge.source_item:
                return False

        # if same affliction but new one has more turns, add more turns
        if affect_to_merge.turns > self.turns:
            self.turns = affect_to_merge.turns
        return True

    # called when applied
    def on_applied(self):
        affects = self.affect_target_actor.affect_manager.affects

        # Move this affect to the front of the dict
        if self in affects.values():
            # Remove and reinsert at the beginning
            for key, value in list(affects.items()):
                if value == self:
                    affects.pop(key)
                    # Reinsert at the front (Python 3.7+ keeps insertion order)
                    affects = {key: self, **affects}
                    break

            # Update the original dict reference
            self.affect_target_actor.affect_manager.affects = affects
        super().on_applied(silent=True)
        # systems.utils.debug_print('aff applied')

    # called when effect is over
    def on_finished(self, silent=False):
        super().on_finished(silent=True)

    # called at start of turn
    def set_turn(self):
        self.turns -= 1
        pass

    # called at end of turn
    def finish_turn(self):
        pass

    # called whenever hp updates in any way
    def take_damage_before_calc(self, damage_obj):
        return damage_obj

    def take_damage_after_calc(self, damage_obj):
        return damage_obj

    def deal_damage(self, damage_obj):
        return damage_obj

    def dealt_damage(self, damage_obj):
        return damage_obj


class ReforgeTest(AffectReforge):
    def finish_turn(self):
        pass


class ReforgeStatBonusPerItemLevel(AffectReforge):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        source_item=None,
        reforge_variables=None,
        dispellable=False,
    ):
        super().__init__(
            affect_source_actor,
            affect_target_actor,
            name,
            description,
            turns,
            source_item=source_item,
            reforge_variables=reforge_variables,
            dispellable=dispellable,
        )
        # self.stat = self.reforge_variables['var_a']
        # self.bonus = float(self.reforge_variables['var_b'])
        # self.bonus = self.bonus * self.source_item.stat_manager.reqs[StatType.LVL]
        # self.source_item.stat_manager.reqs[self.stat] += 1 * self.bonus
        # self.source_item.stat_manager.stats[self.stat] += 1 * self.bonus

        # self.bonus = int(self.bonus * self.source_item.stat_manager.reqs[StatType.LVL])

        # 2 - 5 = -3
        # if self.affect_target_actor.stat_manager.stats[self.stat] - self.bonus <= 0:
        #    self.bonus = self.bonus - self.affect_target_actor.stat_manager.stats[self.stat]

    def on_applied(self):
        super().on_applied()
        # self.affect_target_actor.stat_manager.stats[self.stat] += self.bonus

    def on_finished(self, silent=False):
        # self.affect_target_actor.stat_manager.stats[self.stat] -= self.bonus
        return super().on_finished(silent)


class ReforgePlusDamageTypeMinusDamageTypes(AffectReforge):
    def deal_damage(self, damage_obj):
        # systems.utils.debug_print(damage_obj.damage_value)
        if damage_obj.damage_type == self.reforge_variables["var_a"]:
            damage_obj.damage_value = int(
                damage_obj.damage_value * float(self.reforge_variables["var_b"])
            )
        else:
            damage_obj.damage_value = int(
                damage_obj.damage_value * float(self.reforge_variables["var_c"])
            )
        # systems.utils.debug_print(damage_obj.damage_value)
        return damage_obj


class ReforgeConvertDamageType(AffectReforge):
    def deal_damage(self, damage_obj):
        #print(self.reforge_variables["var_a"],damage_obj.damage_type)
        if 'dmg_'+self.reforge_variables["var_a"] == damage_obj.damage_type:
            damage_obj.damage_type = 'dmg_'+self.reforge_variables["var_b"]
        return damage_obj


class ReforgeSkillDamageBonus(AffectReforge):
    def deal_damage(self, damage_obj):
        if systems.utils.get_object_parent(damage_obj.damage_source_action) == "Skill":
            if (
                damage_obj.damage_source_action.skill_id
                == self.reforge_variables["var_a"]
            ):
                damage_obj.damage_value = int(
                    damage_obj.damage_value * float(self.reforge_variables["var_b"])
                )

        return damage_obj


# this can make indirect healing like leech heal you for less...
class ReforgeRandomTargetBonus(AffectReforge):
    def __init__(
        self,
        affect_source_actor,
        affect_target_actor,
        name,
        description,
        turns,
        source_item=None,
        reforge_variables=None,
    ):
        super().__init__(
            affect_source_actor,
            affect_target_actor,
            name,
            description,
            turns,
            source_item=source_item,
            reforge_variables=reforge_variables,
            dispellable=dispellable,
        )
        self.target = None

    def set_turn(self):
        super().set_turn()
        if self.affect_target_actor.status != ActorStatusType.FIGHTING:
            return
        self.target = random.choice(
            list(self.affect_target_actor.room.combat.participants.values())
        )
        if self.target == self.affect_target_actor:
            self.affect_target_actor.sendLine(f"You are your own target")
        else:
            self.affect_target_actor.sendLine(
                f"Your target is {self.target.pretty_name()}"
            )

    def deal_damage(self, damage_obj):
        if damage_obj.damage_taker_actor == self.target:
            damage_obj.damage_value = int(
                damage_obj.damage_value * float(self.reforge_variables["var_a"])
            )
        else:
            damage_obj.damage_value = int(
                damage_obj.damage_value * float(self.reforge_variables["var_b"])
            )
        return damage_obj


"""
# not fully working
# enemies that have spent their round do not count as targetting you
class ReforgePureDamageBonusToNonTargettingEnemies(AffectReforge):
    def __init__(self,
            affect_source_actor,
            affect_target_actor,
            name, description, turns,
            source_item = None,
            reforge_variables = None
        ):
        super().__init__(affect_source_actor, affect_target_actor, name, description, turns, source_item = source_item, reforge_variables = reforge_variables)

    def deal_damage(self, damage_obj):
        #systems.utils.debug_print('damage_obj.damage_taker_actor.ai.prediction_target == damage_obj.damage_source_actor:',damage_obj.damage_taker_actor.ai.prediction_target == damage_obj.damage_source_actor)
        if damage_obj.damage_taker_actor.ai.prediction_target != damage_obj.damage_source_actor:
            damage_obj.damage_value = int(damage_obj.damage_value * 1.1)
            damage_obj.damage_source_actor.simple_broadcast('HOLY MOLY','HOLY MOLY')
        else:
            damage_obj.damage_value = int(damage_obj.damage_value * 0.5)
            damage_obj.damage_source_actor.simple_broadcast('unHOLY MOLY','unHOLY MOLY')
        return damage_obj
"""
