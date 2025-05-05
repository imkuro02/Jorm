import utils
import random

from configuration.config import SKILLS, DamageType, ActorStatusType, StatType
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

def get_user_skill_level_as_index(user,skill_id):
    skill = SKILLS[skill_id]
    users_skill_level = -1
    _users_skill_level = user.skill_manager.skills[skill_id]
    for i in range(0,len(skill['script_values']['levels'])):
        if _users_skill_level >= skill['script_values']['levels'][i]:
            users_skill_level = i
    return users_skill_level

def skill_checks(user, target, skill_id):
    skill = SKILLS[skill_id]
    skill_name = skill['name']

    # return if learned skill does not actually exist
    if skill_id not in user.skill_manager.skills.keys():
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
    
    if utils.get_object_parent(target) != "Actor":
        error(user, f'You can\'t use {skill_name} on {target.name}')
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


    users_skill_level = get_user_skill_level_as_index(user,skill_id)

    hp_cost = 0
    mp_cost = 0

    if 'mp_cost' in skill['script_values']:
        if hp_cost > user.stat_manager.stats[StatType.HP] + 1:
            hp_cost = skill['script_values']['hp_cost'][users_skill_level]
            error(user, f'You need atleast {hp_cost} HP to use {skill_name}')
            return False
    if 'mp_cost' in skill['script_values']:
        mp_cost = skill['script_values']['mp_cost'][users_skill_level]
        if mp_cost > user.stat_manager.stats[StatType.MP]:
            error(user, f'You need atleast {mp_cost} MP to use {skill_name}')
            return False

    user.stat_manager.stats[StatType.HP] -= hp_cost 
    user.stat_manager.stats[StatType.MP] -= mp_cost 

    return True

def use_skill_from_consumable(user: "Actor", target: "Actor", skill_id: str, consumable_item):
        if skill_id not in SKILLS:
            return False
        skill = SKILLS[skill_id]
        try:
            skill_obj = getattr(skills.skills, f'Skill{skill["script_to_run"]}')
        except AttributeError:
            user.simple_broadcast(
                f'@redscript_to_run:{skill["script_to_run"]} is not a valid skill object in skills.py@normal',
                f'@redscript_to_run:{skill["script_to_run"]} is not a valid skill object in skills.py@normal')
            return False
        
        users_skill_level = 0
        use_perspectives = consumable_item.use_perspectives
        success = True # random.randint(1,100) < skill['script_values']['chance'][users_skill_level]*100
        silent_use = False
        no_cooldown = True
        skill_obj = skill_obj(
                skill_id = skill_id, 
                script_values = skill['script_values'], 
                user = user, 
                other = target, 
                users_skill_level = users_skill_level, 
                use_perspectives = use_perspectives, 
                success = success, 
                silent_use = silent_use, 
                )
        
        skill_obj.use()
        del skill_obj
        


def use_skill(user, target, skill_id, no_checks = False):
    if skill_id not in SKILLS:
        return False
    skill = SKILLS[skill_id]

    if skill_id not in user.skill_manager.skills:
        user.sendLine(f'You do not know {skill["name"]}')
        return

    users_skill_level = get_user_skill_level_as_index(user,skill_id)

    if users_skill_level == -1:
        user.sendLine(f'You do not know {skill["name"]}')
        return

    if skill_checks(user, target, skill_id) or no_checks:
        try:
            skill_obj = getattr(skills.skills, f'Skill{skill["script_to_run"]}')
        except AttributeError:
            user.simple_broadcast(
                f'@redscript_to_run:{skill["script_to_run"]} is not a valid skill object in skills.py@normal',
                f'@redscript_to_run:{skill["script_to_run"]} is not a valid skill object in skills.py@normal')
            return False
        
        use_perspectives = skill['use_perspectives']

        

        success = True #random.randint(1,100) < (skill['script_values']['chance'][users_skill_level]*100)
        silent_use = False
        no_cooldown = False

        skill_obj = skill_obj(
            skill_id = skill_id, 
            script_values = skill['script_values'], 
            user = user, 
            other = target, 
            users_skill_level = users_skill_level, 
            use_perspectives = use_perspectives, 
            success = success, 
            silent_use = silent_use, 
            )

        skill_obj.use()
        del skill_obj
        return True
    return False



