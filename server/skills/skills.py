from configuration.config import DamageType, StatType, ActorStatusType
#import affects.manager as aff_manager
import affects.affects as affects
from combat.manager import Damage

import random

class Skill:
    def __init__(self, skill_id, script_values, user, other, users_skill_level: int, use_perspectives, success = False, silent_use = False):
        self.skill_id = skill_id
        self.script_values = script_values
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
        cool = self.script_values['cooldown'][self.users_skill_level]
        self.user.cooldown_manager.add_cooldown(self.skill_id, cool)

        if self.silent_use:
            return
        self.use_broadcast()


class SkillSwing(Skill):
    def use(self):
        grit = int(self.user.stats[StatType.GRIT])
        flow = int(self.user.stats[StatType.FLOW])

        my_dmg_scaling = StatType.GRIT
        if flow > grit: 
            my_dmg_scaling = StatType.FLOW

        super().use()
        if self.success:
            amp = int(self.user.stats[my_dmg_scaling]*self.script_values['bonus'][self.users_skill_level])
            base = self.script_values['damage'][self.users_skill_level]
            dmg = base + amp
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_value = dmg,
                damage_type = DamageType.PHYSICAL
                )
            damage = self.user.deal_damage(damage_obj)

class SkillCureLightWounds(Skill):
    def use(self):
        super().use()
        if self.success:
            amp = int(self.user.stats[StatType.SOUL]*self.script_values['bonus'][self.users_skill_level])
            base = self.script_values['damage'][self.users_skill_level]
            dmg = base + amp
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_value = dmg,
                damage_type = DamageType.HEALING
                )
            self.user.deal_damage(damage_obj)
            
class SkillBash(SkillSwing):
    def use(self):
        damage_dealt = super().use()
        if self.success:
            stunned_affect = affects.AffectStunned(
                self.other.affect_manager,
                'Stunned', 'Unable to act during combat turns',
                turns = 1
            )
            if damage_dealt != 0:
                self.other.affect_manager.set_affect_object(stunned_affect)



class SkillDamage(Skill):
     def use(self, my_dmg_scaling = StatType.GRIT, my_dmg_type = DamageType.PHYSICAL):
        super().use()
        if self.success:
            amp = int(self.user.stats[my_dmg_scaling]*self.script_values['bonus'][self.users_skill_level])
            base = self.script_values['damage'][self.users_skill_level]
            dmg = base + amp
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_value = dmg,
                damage_type = my_dmg_type
                )
            damage = self.user.deal_damage(damage_obj)

class SkillDoubleWhack(Skill):
    def use(self):
        for i in range(0,2):
            amp = int(self.user.stats[StatType.FLOW]*self.script_values['bonus'][self.users_skill_level])
            base = self.script_values['damage'][self.users_skill_level]
            dmg = base + amp
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_value = dmg,
                damage_type = self.user.stats[StatType.FLOW]
                )
            #damage = self.user.deal_damage(damage_obj)
            self.user.deal_damage(damage_obj)
            if self.success:
                self.user.deal_damage(damage_obj)

class SkillDamageByGrit(SkillDamage):
    def use(self):
        super().use(StatType.GRIT, DamageType.PHYSICAL)
class SkillDamageByFlow(SkillDamage):
    def use(self):
        super().use(StatType.FLOW, DamageType.PHYSICAL)
class SkillDamageByMind(SkillDamage):
    def use(self):
        super().use(StatType.MIND, DamageType.MAGICAL)
class SkillDamageBySoul(SkillDamage):
    def use(self):
        super().use(StatType.SOUL, DamageType.MAGICAL)

class SkillBecomeEthereal(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.script_values['duration'][self.users_skill_level])
            dmg_amp = self.script_values['bonus'][self.users_skill_level]
            ethereal_affect = affects.AffectEthereal(
                self.other.affect_manager, 
                'Ethereal', f'You take {int(dmg_amp*100)}% damage from spells, but are immune to physical damage', 
                turns, dmg_amp)
            self.other.affect_manager.set_affect_object(ethereal_affect)  

class SkillMageArmor(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.script_values['duration'][self.users_skill_level])
            reduction = self.script_values['bonus'][self.users_skill_level]
            ethereal_affect = affects.AffectMageArmor(
                affect_manager = self.other.affect_manager, 
                name = 'Magically protected', description = f'{int(reduction*100)}% of damage is converted to Magicka damage.', 
                turns = turns, reduction = reduction)
            self.other.affect_manager.set_affect_object(ethereal_affect)  

class SkillEnrage(Skill):
    def use(self):
        super().use()
        if self.success:
            turns =         int(self.script_values['duration'][self.users_skill_level])
            extra_hp =      self.script_values['bonus'][self.users_skill_level]
            enrage_affect = affects.AffectEnrage(
                affect_manager = self.other.affect_manager, 
                name = 'Enraged', description = f'Temporary {int(extra_hp*100)}% Health', 
                turns = turns, extra_hp = extra_hp)
            self.user.affect_manager.set_affect_object(enrage_affect)  
            
class SkillRegenHP30(Skill):
    def use(self):
        super().use()
        if self.success:
            #self.other.take_damage(self.user, int(self.user.stats[StatType.HPMAX]*.3), DamageType.HEALING)
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_value = int(self.user.stats[StatType.HPMAX]*.3),
                damage_type = DamageType.HEALING
                )
            self.other.take_damage(damage_obj)           

class SkillRegenMP30(Skill):
    def use(self):
        super().use()
        if self.success:
            #self.other.take_damage(self.user, int(self.user.stats[StatType.HPMAX]*.3), DamageType.HEALING)
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_value = int(self.user.stats[StatType.MPMAX]*.3),
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.MP
                )
            self.other.take_damage(damage_obj)                

