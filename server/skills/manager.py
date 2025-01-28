import utils
import random

from configuration.config import SKILLS, DamageType, ActorStatusType, StatType, AffType
import skills.skills 

def get_skills():
    name_to_id = {}
    id_to_name = {}
    for skill in SKILLS.keys():
        name_to_id[SKILLS[skill]['name']] = skill
    for skill in SKILLS.keys():
        id_to_name[skill] = SKILLS[skill]['name']

    return id_to_name, name_to_id

def error(user, err):
    if type(user).__name__ == "Player":
        user.sendLine(err)
    else:
        print(err)

def skill_checks(user, target, skill_id):
    skill = SKILLS[skill_id]
    skill_name = skill['name']

    # return if learned skill does not actually exist
    if skill_id not in user.skills.keys():
        error(user, f'{skill_name} is not learned yet')
        return False

    # cant target yourself
    if target == user and not skill['target_self_is_valid']:
        error(user, f'You can\'t use {skill_name} on yourself')
        return False

    # cant target others
    if target != user and not skill['target_others_is_valid']:
        error(user, f'You can\'t use {skill_name} on others')
        return False

    if skill['must_be_fighting']:
        if user.status != ActorStatusType.FIGHTING:
            error(user, f'{skill_name} can only be used during a fight')
            return False

    # allow using skills on dead targets
    if user.status == ActorStatusType.FIGHTING and (target.status != ActorStatusType.FIGHTING and target.status != ActorStatusType.DEAD):
        error(user, f'You are in a fight but {target.name} is not participating!')
        return False

    if user.status != ActorStatusType.FIGHTING and target.status == ActorStatusType.FIGHTING:
        error(user, f'{target.name} is in a fight you are not participating in!')
        return False

    if skill_id in user.cooldown_manager.cooldowns:
        error(user, f'{skill_name} is on cooldown!')
        return False

    users_skill_level = user.skills[skill_id]

    hp_cost = skill['hp_cost'] 
    mp_cost = skill['mp_cost'] 

    if hp_cost > user.stats[StatType.HP] + 1:
        error(user, f'You need atleast {hp_cost} HP to use {skill_name}')
        return False
    
    if mp_cost > user.stats[StatType.MP]:
        error(user, f'You need atleast {mp_cost} MP to use {skill_name}')
        return False

    user.stats[StatType.HP] -= hp_cost 
    user.stats[StatType.MP] -= mp_cost 

    return True

def use_skill_from_consumable(user: "Actor", target: "Actor", skill_id: str, consumable_item):
        if skill_id not in SKILLS:
            return False
        skill = SKILLS[skill_id]
        try:
            skill_obj = getattr(skills.skills, f'Skill{skill["script_to_run"]}')
        except AttributeError:
            user.sendLine(f'@redscript_to_run:{skill["script_to_run"]} is not a valid skill object in skills.py@normal')
            return False
        
        users_skill_level = 1
        cooldown = skill['cooldown']
        use_perspectives = consumable_item.use_perspectives
        success = random.randint(1,100) < 85
        silent_use = False
        no_cooldown = True

        skill_obj = skill_obj(
                skill_id = skill_id, 
                cooldown = cooldown, 
                user = user, 
                other = target, 
                users_skill_level = users_skill_level, 
                use_perspectives = use_perspectives, 
                success = success, 
                silent_use = silent_use, 
                no_cooldown = no_cooldown
                )
        
        skill_obj.use()
        del skill_obj
        


def use_skill(user, target, skill_id, no_checks = False):
    if skill_id not in SKILLS:
        return False
    skill = SKILLS[skill_id]


    if skill_checks(user, target, skill_id) or no_checks:
        try:
            skill_obj = getattr(skills.skills, f'Skill{skill["script_to_run"]}')
        except AttributeError:
            user.sendLine(f'@redscript_to_run:{skill["script_to_run"]} is not a valid skill object in skills.py@normal')
            return False
        
        users_skill_level = user.skills[skill_id]
        cooldown = skill['cooldown']
        use_perspectives = skill['use_perspectives']
        success = random.randint(1,100) < user.skills[skill_id]
        silent_use = False
        no_cooldown = False

        skill_obj = skill_obj(
            skill_id = skill_id, 
            cooldown = cooldown, 
            user = user, 
            other = target, 
            users_skill_level = users_skill_level, 
            use_perspectives = use_perspectives, 
            success = success, 
            silent_use = silent_use, 
            no_cooldown = no_cooldown
            )

        skill_obj.use()
        del skill_obj
        return True
    return False



