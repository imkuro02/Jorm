import random

import skills.skills
import systems.utils
from configuration.config import (
    SKILLS,
    ActorStatusType,
    Audio,
    Color,
    DamageType,
    StatType,
)


def get_skills():
    name_to_id = {}
    id_to_name = {}
    for skill in SKILLS.keys():
        name_to_id[SKILLS[skill]["name"]] = skill
    for skill in SKILLS.keys():
        id_to_name[skill] = SKILLS[skill]["name"]

    return id_to_name, name_to_id


def error(user, err):
    if type(user).__name__ == "Player":
        # return if in combat and autobattling
        # because then its likely that the error is caused by
        # autobattler using wrong skill
        # if user.settings_manager.autobattler:
        #    if user.status == ActorStatusType.FIGHTING:
        #        return
        user.sendLine(err)
        user.sendSound(Audio.ERROR)
    else:
        systems.utils.debug_print(err)


def get_user_skill_level_as_index(user, skill_id):
    skill = SKILLS[skill_id]
    users_skill_level = -1
    # _users_skill_level = user.stat_manager.stats[StatType.LVL]
    _users_skill_level = user.skill_manager.skills[skill_id]
    for i in range(0, len(skill["script_values"]["levels"])):
        if _users_skill_level >= skill["script_values"]["levels"][i]:
            users_skill_level = i
    return users_skill_level


def skill_checks(user, target, skill_id):
    skill = SKILLS[skill_id]
    skill_name = skill["name"]

    # return if learned skill does not actually exist
    if skill_id not in user.skill_manager.skills.keys():
        error(user, f"{skill_name} is not learned yet")
        return False

    if skill_id in user.cooldown_manager.cooldowns:
        error(user, f"{skill_name} is on cooldown!")
        return False

    if systems.utils.get_object_parent(target) == "Actor":
        # cant target yourself
        if target == user and not skill["target_self_is_valid"]:
            error(user, f"You can't use {skill_name} on yourself")
            return False

        # cant target others
        if target != user and not skill["target_others_is_valid"]:
            if systems.utils.get_object_parent(target) != "Item":
                error(user, f"You can't use {skill_name} on others")
                return False

        # if systems.utils.get_object_parent(target) != "Actor":
        #    error(user, f'You can\'t use {skill_name} on {target.name}')
        #    return False

        if not skill["can_use_in_combat"]:
            if user.status == ActorStatusType.FIGHTING:
                error(user, f"{skill_name} cannot be used in combat")
                return False

        if not skill["can_use_out_of_combat"]:
            if user.status != ActorStatusType.FIGHTING:
                error(user, f"{skill_name} cannot be out of combat")
                return False

        # allow using skills on dead targets
        if user.status == ActorStatusType.FIGHTING and (
            target.status != ActorStatusType.FIGHTING
            and target.status != ActorStatusType.DEAD
        ):
            error(user, f"You are in a fight but {target.name} is not participating!")
            return False

        if (
            user.status != ActorStatusType.FIGHTING
            and target.status == ActorStatusType.FIGHTING
        ):
            error(user, f"{target.name} is in a fight you are not participating in!")
            return False

    if (
        systems.utils.get_object_parent(target) == "Item"
        and not skill["target_item_is_valid"]
    ):
        error(user, f"You can't use {skill_name} on items")
        return False

    users_skill_level = get_user_skill_level_as_index(user, skill_id)

    hp_cost = 0
    mp_cost = 0

    if "hp_cost" in skill["script_values"]:
        hp_cost = skill["script_values"]["hp_cost"][users_skill_level]
        hp_cost = hp_cost + int(user.stat_manager.stats[StatType.LVL] * 0.5)
        if hp_cost > user.stat_manager.stats[StatType.HP] + 1:
            error(
                user,
                f"You need atleast {hp_cost + 1} {Color.stat[StatType.HP]}{StatType.name[StatType.HP]}{Color.BACK} to use {skill_name}",
            )
            return False
    # if 'mp_cost' in skill['script_values']:

    # mp_cost = skill['script_values']['mp_cost'][users_skill_level]

    #    mp_cost = systems.utils.calculate_skill_mp_cost(actor = user, base_value = skill['script_values']['mp_cost'][users_skill_level])

    #    if mp_cost > user.stat_manager.stats[StatType.MP]:
    #        error(user, f'You need atleast {mp_cost} MP to use {skill_name}')
    #        return False

    user.stat_manager.stats[StatType.HP] -= hp_cost
    # user.stat_manager.stats[StatType.MP] -= mp_cost

    return True


def use_skill_from_consumable(
    user: "Actor", target: "Actor", skill_id: str, consumable_item
):
    if skill_id not in SKILLS:
        return False
    skill = SKILLS[skill_id]
    try:
        skill_obj = getattr(skills.skills, f"Skill{skill['script_to_run']}")
    except AttributeError:
        user.simple_broadcast(
            f"@redscript_to_run:{skill['script_to_run']} is not a valid skill object in skills.py@normal",
            f"@redscript_to_run:{skill['script_to_run']} is not a valid skill object in skills.py@normal",
        )
        return False

    users_skill_level = 0
    use_perspectives = consumable_item.use_perspectives
    success = True  # random.randint(1,100) < skill['script_values']['chance'][users_skill_level]*100
    silent_use = True
    no_cooldown = True

    _skill_obj = skill_obj(
        skill_id=skill_id,
        script_values=skill["script_values"],
        user=user,
        other=target,
        users_skill_level=users_skill_level,
        use_perspectives=use_perspectives,
        success=success,
        silent_use=silent_use,
        # aoe = skill['aoe'],
        # bounce = skill['bounce']
    )

    _skill_obj.pre_use()
    del _skill_obj
    return True


def use_skill(user, target, skill_id, no_checks=False):
    if skill_id not in SKILLS:
        return False
    skill = SKILLS[skill_id]

    if skill_id not in user.skill_manager.skills:
        user.sendLine(f"You do not know {skill['name']}")
        return False

    if user.skill_manager.skills[skill_id] <= 0:
        user.sendLine(f"You do not know {skill['name']}")
        return False

    users_skill_level = get_user_skill_level_as_index(user, skill_id)

    if users_skill_level == -1:
        user.sendLine(f"You are not high enough level to use {skill['name']}")
        return False

    if skill_checks(user, target, skill_id) or no_checks:
        try:
            skill_obj = getattr(skills.skills, f"Skill{skill['script_to_run']}")
        except AttributeError:
            user.simple_broadcast(
                f"@redscript_to_run:{skill['script_to_run']} is not a valid skill object in skills.py@normal",
                f"@redscript_to_run:{skill['script_to_run']} is not a valid skill object in skills.py@normal",
            )
            return False

        use_perspectives = skill["use_perspectives"]

        success = True  # random.randint(1,100) < (skill['script_values']['chance'][users_skill_level]*100)
        silent_use = False
        no_cooldown = False

        _skill_obj = skill_obj(
            skill_id=skill_id,
            script_values=skill["script_values"],
            user=user,
            other=target,
            users_skill_level=users_skill_level,
            use_perspectives=use_perspectives,
            success=success,
            silent_use=silent_use,
            # aoe = skill['aoe'],
            # bounce = skill['bounce']
        )

        _skill_obj.pre_use()
        del _skill_obj
        return True

        """
        if skill['aoe']:
            targets = []

            for i in user.room.actors.values():
                if user.status != i.status:
                    continue
                if not skill['is_offensive']:
                    if i.party_manager.get_party_id() == user.party_manager.get_party_id():
                        targets.append(i)
                else:
                    if i.party_manager.get_party_id() != user.party_manager.get_party_id():
                        targets.append(i)

            for target in targets:
                _skill_obj = skill_obj(
                    skill_id = skill_id,
                    script_values = skill['script_values'],
                    user = user,
                    other = target,
                    users_skill_level = users_skill_level,
                    use_perspectives = use_perspectives,
                    success = success,
                    silent_use = silent_use,
                    aoe = skill['aoe'],
                    bounce = skill['bounce']
                )

                _skill_obj.use()
                del _skill_obj
                #silent_use = True

            return True
        else:
            _skill_obj = skill_obj(
                skill_id = skill_id,
                script_values = skill['script_values'],
                user = user,
                other = target,
                users_skill_level = users_skill_level,
                use_perspectives = use_perspectives,
                success = success,
                silent_use = silent_use,
                aoe = skill['aoe'],
                bounce = skill['bounce']
            )

            _skill_obj.use()
            del _skill_obj
            return True
        """

    return False
