import utils
import random

from config import SKILLS, DamageType, ActorStatusType, StatType, AffType
SKILLS = SKILLS
from affects import manager as aff_manager

def get_skills():
    name_to_id = {}
    id_to_name = {}
    for skill in SKILLS.keys():
        name_to_id[SKILLS[skill]['name']] = skill
    for skill in SKILLS.keys():
        id_to_name[skill] = SKILLS[skill]['name']

    return id_to_name, name_to_id

def error( user, err):
    if type(user).__name__ == "Player":
        user.sendLine(err)
    else:
        print(err)

def use_skill(user: "Actor", target: "Actor", skill_name: str, used_from_consumable = False, forced_perspectives = None, silent_use = False):
    try:
        def roll():
            return random.randint(1,100)

        if not used_from_consumable:
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

            # cant target others
            if target != user and not SKILLS[best_match]['target_others_is_valid']:
                error(user, f'You can\'t use {skill_name} on others')
                return

            if SKILLS[best_match]['must_be_fighting']:
                if user.status != ActorStatusType.FIGHTING:
                    error(user, f'{skill_name} can only be used during a fight')
                    return

            if user.status == ActorStatusType.FIGHTING and target.status != ActorStatusType.FIGHTING:
                error(user, f'You are in a fight but {target.name} is not participating!')
                return

            if user.status != ActorStatusType.FIGHTING and target.status == ActorStatusType.FIGHTING:
                error(user, f'{target.name} is in a fight you are not participating in!')
                return

            if best_match in user.cooldown_manager.cooldowns:
                error(user, f'{SKILLS[best_match]["name"]} is on cooldown!')
                return

            users_skill_level = user.skills[best_match]

            hp_cost = SKILLS[best_match]['hp_cost'] * users_skill_level
            mp_cost = SKILLS[best_match]['mp_cost'] * users_skill_level

            if hp_cost > user.stats[StatType.HP] + 1:
                error(user, f'You need atleast {hp_cost} HP to use {skill_name}')
                return
            
            if mp_cost > user.stats[StatType.MP]:
                error(user, f'You need atleast {mp_cost} MP to use {skill_name}')
                return

            user.stats[StatType.HP] -= hp_cost
            user.stats[StatType.MP] -= mp_cost
            
            level_to_successrate = {
                1: 10,
                2: 20,
                3: 30,
                4: 40,
                5: 50,
                6: 60,
                7: 70,
                8: 80,
                9: 90,
                10: 95
            }
            
            success = roll() <= level_to_successrate[users_skill_level]
        else:
            users_skill_level = 1
            best_match = skill_name
            if user == target:
                success = True
            else:
                success = roll() <= 70

        if forced_perspectives == None:
            use_perspectives = SKILLS[best_match]['use_perspectives']
        else:
            use_perspectives = forced_perspectives

        skill_id = best_match
        cooldown = SKILLS[best_match]['cooldown']

        script = globals()['Skill'+str(SKILLS[best_match]['script_to_run'])](skill_id = best_match, cooldown = cooldown, user = user, other = target, users_skill_level = users_skill_level, use_perspectives = use_perspectives, success = success, silent_use = silent_use)
        script.use()
        del script

        return True
    except Exception as e:
        error(user, f'Exception in {__name__}: {e}')
        return False



class Skill:
    def __init__(self, skill_id, cooldown, user, other, users_skill_level: int, use_perspectives, success, silent_use = False):
        self.skill_id = skill_id
        self.cooldown = cooldown
        self.user = user
        self.other = other
        self.users_skill_level = users_skill_level
        self.use_perspectives = use_perspectives
        self.success = success
        self.silent_use = silent_use


    def use_broadcast(self):
        perspectives = {
            'you on you':       self.use_perspectives['you on you fail'],
            'you on other':     self.use_perspectives['you on other fail'],
            'user on user':     self.use_perspectives['user on user fail'],
            'user on you':      self.use_perspectives['user on you fail'],
            'user on other':    self.use_perspectives['user on other fail']
        }
        if self.success:
            perspectives = {
                'you on you':       self.use_perspectives['you on you'],
                'you on other':     self.use_perspectives['you on other'],
                'user on user':     self.use_perspectives['user on user'],
                'user on you':      self.use_perspectives['user on you'],
                'user on other':    self.use_perspectives['user on other']
            }

        for perspective in perspectives:
            perspectives[perspective] = perspectives[perspective].replace('#USER#', self.user.pretty_name())
            perspectives[perspective] = perspectives[perspective].replace('#OTHER#', self.other.pretty_name())

        for receiver in self.user.room.entities.values():
            if type(receiver).__name__ != "Player":
                continue

            if receiver == self.user and receiver == self.other:
                receiver.sendLine(perspectives['you on you'])
                continue
            if receiver == self.user and receiver != self.other:
                receiver.sendLine(perspectives['you on other'])
                continue
            if receiver != self.user and receiver != self.other and self.user == self.other:
                receiver.sendLine(perspectives['user on user'])
                continue
            if receiver != self.user and receiver == self.other:
                receiver.sendLine(perspectives['user on you'])
                continue
            if receiver != self.user and receiver != self.other:
                receiver.sendLine(perspectives['user on other'])
                continue

    def use(self):
        if self.silent_use:
            return
        self.user.cooldown_manager.add_cooldown(self.skill_id, self.cooldown)
        self.use_broadcast()

class SkillSwing(Skill):
    def use(self):
        super().use()
        if self.success:
            self.other.take_damage(self.user, 1 + self.user.stats[StatType.BODY], DamageType.PHYSICAL)

class SkillCureLightWounds(Skill):
    def use(self):
        super().use()
        if self.success:
            self.other.take_damage(self.user, 10 * self.users_skill_level, DamageType.HEALING)

class SkillBash(SkillSwing):
    def use(self):
        super().use()
        if self.success:
            stunned_affect = aff_manager.AffectStunned(
                AffType.STUNNED,
                self.other.affect_manager,
                'Stunned', 'Unable to act during combat turns',
                turns = 3
            )
            self.other.affect_manager.set_affect_object(stunned_affect)

class SkillMagicMissile(Skill):
    def use(self):
        super().use()
        if self.success:
            self.other.take_damage(self.user, self.users_skill_level + self.user.stats[StatType.MIND], DamageType.MAGICAL)

class SkillBecomeEthereal(Skill):
    def use(self):
        try:
            super().use()
            if self.success:
                turns = 4 + int(self.users_skill_level*0.3)
                dmg_amp = 2.4 - self.users_skill_level*0.1
                ethereal_affect = aff_manager.AffectEthereal(
                    AffType.ETHEREAL, 
                    self.user.affect_manager, 
                    'Ethereal', f'You take {int(dmg_amp*100)}% damage from spells, but are immune to physical damage', 
                    turns, dmg_amp)
                self.user.affect_manager.set_affect_object(ethereal_affect)
        except Exception as e:
            print(e)