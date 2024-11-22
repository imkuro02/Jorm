'''
import random
import yaml
#from actor import Actor
import utils

factory = None

with open('config/skills.yaml', 'r') as file:
    SKILLS = {}
    SKILLS_UNFILTERED = yaml.safe_load(file)
    for i in SKILLS_UNFILTERED:
        if 'template' not in i:
            SKILLS[i] = SKILLS_UNFILTERED[i]


def skill_simple_damage(user, target, arguments):
    base_damage = arguments[0]      # int
    damage_type = arguments[1]      # string 
    bonus_damages = arguments[2]    # dictionary like {'str': 1.1}

    damage = base_damage
    for i in bonus_damages:
        damage += user.stats[i] * bonus_damages[i]
        
    damage = int(damage)
    target.take_damage(damage, damage_type)

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

def suse_broadcast(user, target, for_self, for_others):

    for i in user.room.entities.values():
        if type(i).__name__ != "Player":
            continue

        # perspectives of 
        if i == user and i == target: # you are the user and the target
            message = for_self.replace('#USER#', 'you')
            message = message.replace('#TARGET#', 'yourself')
            i.sendLine(message)
            continue

        if i != user and user == target: # you arent the user but the user is the target
            message = for_others.replace('#USER#', target.pretty_name())
            message = message.replace('#TARGET#', 'themself')
            i.sendLine(message)
            continue

        if i == user: # check if you are the user
            message = for_self.replace('#USER#', 'you')
            message = message.replace('#TARGET#', target.pretty_name())
            i.sendLine(message)
            continue

        elif i == target: # check if you are the target
            message = for_others.replace('#USER#', user.pretty_name())
            message = message.replace('#TARGET#', 'you')
            i.sendLine(message)
            continue

        else: # everyone else
            message = for_others.replace('#USER#', user.pretty_name())
            message = message.replace('#TARGET#', target.pretty_name())
            i.sendLine(message)
            continue
       
def use_broadcast(user, other, perspectives):
    for perspective in perspectives:
        perspectives[perspective] = perspectives[perspective].replace('#USER#', user.pretty_name())
        perspectives[perspective] = perspectives[perspective].replace('#OTHER#', other.pretty_name())

    for receiver in user.room.entities.values():
        if type(receiver).__name__ != "Player":
            continue

        if receiver == user and receiver == other:
            receiver.sendLine(perspectives['you on you'])
            continue
        if receiver == user and receiver != other:
            receiver.sendLine(perspectives['you on other'])
            continue
        if receiver != user and receiver != other and user == other:
            receiver.sendLine(perspectives['user on user'])
            continue
        if receiver != user and receiver == other:
            receiver.sendLine(perspectives['user on you'])
            continue
        if receiver != user and receiver != other:
            receiver.sendLine(perspectives['user on other'])
            continue

def use_skill(user: "Actor", target: "Actor", skill_name: str):
    #best_match, best_score = process.extractOne(skill, SKILLS.keys())
    # match skill_name to users skills
    best_match = utils.match_word(skill_name, user.skills.keys())
    skill_name = SKILLS[best_match]["name"]

    # return if learned skill does not actually exist
    if best_match not in SKILLS.keys():
        error(user, f'{skill_name} is not learned yet')
        return

    # cant target yourself
    if target == user and not SKILLS[best_match]['target_self_is_valid']:
        error(user, f'You can\'t use {skill_name} on yourself')
        return

    if SKILLS[best_match]['must_be_fighting']:
        if user.status != 'fighting':
            error(user, f'{skill_name} can only be used during a fight')
            return

    if user.status == 'fighting' and target.status != 'fighting':
        error(user, f'You are in a fight but {target.name} is not participating!')
        return

    if user.status != 'fighting' and target.status == 'fighting':
        error(user, f'{target.name} is in a fight you are not participating in!')
        return

    hp_cost = SKILLS[best_match]['hp_cost']
    mp_cost = SKILLS[best_match]['mp_cost']

    if hp_cost > user.stats['hp'] + 1:
        error(user, f'You need atleast {hp_cost} HP to use {skill_name}')
        return
    
    if mp_cost > user.stats['mp']:
        error(user, f'You need atleast {mp_cost} MP to use {skill_name}')
        return

    user.stats['hp'] -= hp_cost
    user.stats['mp'] -= mp_cost

    roll = random.randint(1,100)
    success = roll <= user.skills[best_match]

    use_perspectives = SKILLS[best_match]['use_perspectives']

    perspectives = {
            'you on you':       use_perspectives['you on you fail'],
            'you on other':     use_perspectives['you on other fail'],
            'user on user':     use_perspectives['user on user fail'],
            'user on you':      use_perspectives['user on you fail'],
            'user on other':    use_perspectives['user on other fail']
        }
    if success:
        perspectives = {
            'you on you':       use_perspectives['you on you'],
            'you on other':     use_perspectives['you on other'],
            'user on user':     use_perspectives['user on user'],
            'user on you':      use_perspectives['user on you'],
            'user on other':    use_perspectives['user on other']
        }
    
    use_broadcast(user, target, perspectives)
    
    if success:
        script = globals()[SKILLS[best_match]['script_to_run']['name_of_script']]
        arguments = SKILLS[best_match]['script_to_run']['arguments']
        script(user, target, arguments)

    return True
        
'''