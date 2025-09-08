from configuration.config import DamageType, StatType, ActorStatusType, StaticRooms
#import affects.manager as aff_manager
import affects.affects as affects
from combat.damage_event import Damage
from configuration.config import SKILLS
import random
import utils

class Skill:
    def __init__(self, skill_id, script_values, user, other, users_skill_level: int, use_perspectives, success = False, silent_use = False):
        self.skill_id = skill_id
        self.name = SKILLS[skill_id]['name']
        self.script_values = script_values
        self.user = user
        self.other = other
        self.users_skill_level = users_skill_level
        self.use_perspectives = use_perspectives
        self.success = success
        self.silent_use = silent_use

    def get_dmg_value(self, stat_type = None):
        if 'crit' not in self.script_values or stat_type == None:
            dmg = self.script_values['damage'][self.users_skill_level]
        else:
            crit_min = int(self.script_values['crit'][self.users_skill_level]*0)
            crit_max = int(self.script_values['crit'][self.users_skill_level]*100)
            dmg_stat = int(self.user.stat_manager.stats[stat_type])
            dmg = self.script_values['damage'][self.users_skill_level] + int(dmg_stat * (random.randint(crit_min,crit_max)/100))
            dmg = int(dmg)
        return dmg
    
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

        for receiver in self.user.room.actors.values():
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
        grit = int(self.user.stat_manager.stats[StatType.GRIT])
        flow = int(self.user.stat_manager.stats[StatType.FLOW])

        my_dmg_scaling = StatType.GRIT
        if flow > grit: 
            my_dmg_scaling = StatType.FLOW

        super().use()
        if self.success:
            #amp = int(self.user.stat_manager.stats[my_dmg_scaling]*self.script_values['bonus'][self.users_skill_level])
            #base = self.script_values['damage'][self.users_skill_level]
            #dmg = base + amp
            dmg = self.get_dmg_value(my_dmg_scaling)
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_source_action = self,
                damage_value = dmg,
                damage_type = DamageType.PHYSICAL
                )
            damage_obj.run()

class SkillCureLightWounds(Skill):
    def use(self):
        super().use()
        if self.success:
            dmg = self.get_dmg_value(StatType.SOUL)
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_source_action = self,
                damage_value = dmg,
                damage_type = DamageType.HEALING
                )
            damage_obj.run()

class SkillManaFeed(Skill):
    def use(self):
        super().use()
        if self.success:
            dmg = int(self.user.stat_manager.stats[StatType.MPMAX] * self.script_values['bonus'][self.users_skill_level])
            damage_obj = Damage(
                damage_taker_actor = self.user,
                damage_source_actor = self.user,
                damage_source_action = self,
                damage_value = dmg,
                damage_type = DamageType.PURE,
                damage_to_stat = StatType.MP
                )
            current_mp = self.user.stat_manager.stats[StatType.MP]
            mana_dmg = damage_obj.run()
            if current_mp >= dmg:
                pass
            else:
                dmg = current_mp
            
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_source_action = self,
                damage_value = dmg,
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.MP
                )
            damage_obj.run()
            
class SkillBash(SkillSwing):
    def use(self):
        damage_dealt = super().use()
        if self.success:
            stunned_affect = affects.AffectStunned(
                self.other.affect_manager,
                'Stunned', 'Unable to act during combat turns',
                turns = self.script_values['duration'][self.users_skill_level],
                get_prediction_string_append = 'is stunned!',
                get_prediction_string_clear = True
            )
            if damage_dealt != 0:
                self.other.affect_manager.set_affect_object(stunned_affect)


class SkillDamage(Skill):
     def use(self, my_dmg_scaling = StatType.GRIT, my_dmg_type = DamageType.PHYSICAL):
        super().use()
        if self.success:
            dmg = self.get_dmg_value(my_dmg_scaling)
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_source_action = self,
                damage_value = dmg,
                damage_type = my_dmg_type
                )
            damage_obj.run()

class SkillDoubleWhack(Skill):
    def use(self):
        
        for i in range(0,2):
            dmg = self.get_dmg_value(StatType.FLOW)
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_source_action = self,
                damage_value = dmg,
                damage_type = DamageType.PHYSICAL
                )
            #damage = self.user.deal_damage(damage_obj)
            
            if self.success:
                super().use()
                damage_obj.run()


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
        super().use(StatType.SOUL, DamageType.PURE)

class SkillBoostStat(Skill):
    def use(self, name_of_boost = 'boosted', stat = StatType.GRIT):
        #super().use()
        if self.success:
            turns =         int(self.script_values['duration'][self.users_skill_level])
            bonus =         self.script_values['bonus'][self.users_skill_level]
            aff   = affects.AffectBoostStat(
                    affect_manager = self.other.affect_manager, 
                    name = name_of_boost, description = f'Temporary boost {StatType.name[stat].lower()} by {int(bonus*100)}% (+{int(self.other.stat_manager.stats[stat]*bonus)})', 
                    turns = turns, bonus = bonus, stat=stat)
            self.other.affect_manager.set_affect_object(aff)        
class SkillBoostStatGrit(SkillBoostStat):
    def use(self):
        Skill.use(self)
        super().use(name_of_boost='Grit Blessed',stat=StatType.GRIT)
class SkillBoostStatFlow(SkillBoostStat):
    def use(self):
        Skill.use(self)
        super().use(name_of_boost='Flow Blessed',stat=StatType.FLOW)
class SkillBoostStatMind(SkillBoostStat):
    def use(self):
        Skill.use(self)
        super().use(name_of_boost='Mind Blessed',stat=StatType.MIND)
class SkillBoostStatSoul(SkillBoostStat):
    def use(self):
        Skill.use(self)
        super().use(name_of_boost='Soul Blessed',stat=StatType.SOUL)
class SkillBoostStats(SkillBoostStat):
    def use(self):
        Skill.use(self)
        super().use(name_of_boost='Grit Blessed',stat=StatType.GRIT)
        super().use(name_of_boost='Flow Blessed',stat=StatType.FLOW)
        super().use(name_of_boost='Mind Blessed',stat=StatType.MIND)
        super().use(name_of_boost='Soul Blessed',stat=StatType.SOUL)

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
            bonus =      self.script_values['bonus'][self.users_skill_level]
            enrage_affect = affects.AffectEnrage(
                affect_manager = self.other.affect_manager, 
                name = 'Enraged', description = f'Grit increased, and all armor decreased by {int(bonus*100)}%', 
                turns = turns, bonus = bonus)
            self.user.affect_manager.set_affect_object(enrage_affect)  

class SkillAdrenaline(Skill):
    def use(self):
        super().use()
        if self.success:
            turns =         int(self.script_values['duration'][self.users_skill_level])
            extra_hp =      self.script_values['bonus'][self.users_skill_level]
            enrage_affect = affects.AffectAdrenaline(
                affect_manager = self.other.affect_manager, 
                name = 'Surging', description = f'Temporary {int(extra_hp*100)}% Health', 
                turns = turns, extra_hp = extra_hp)
            self.user.affect_manager.set_affect_object(enrage_affect)  
            
class SkillLeech(Skill):
    def use(self):
        super().use()
        if self.success:
            leech_power = self.script_values['bonus'][self.users_skill_level]
            #affect_manager, name, description, turns
            leech_affect = affects.Leech(
                affect_manager = self.other.affect_manager,
                name = 'Leeching',
                description = f'Convert {int(leech_power*100)}% of physical damage dealt to healing.',
                turns = int(self.script_values['duration'][self.users_skill_level]),
                leech_power = leech_power
            )

            self.other.affect_manager.set_affect_object(leech_affect)  

class SkillThorns(Skill):
    def use(self):
        super().use()
        if self.success:
            damage_reflected_power = self.script_values['bonus'][self.users_skill_level]
            thorns_affect = affects.Thorns(
                affect_manager = self.other.affect_manager,
                name = 'Thorny',
                description = f'Reflect {int(damage_reflected_power*100)}% of physical damage back. ',
                turns = int(self.script_values['duration'][self.users_skill_level]),
                damage_reflected_power = damage_reflected_power
            ) 
            self.other.affect_manager.set_affect_object(thorns_affect)  

# Potions
class SkillRegenPercentFromPotion(Skill):
    def use(self, power_percent, stat_to_heal):
        super().use()
        if self.success:
            if 'Potion Sick' not in self.other.affect_manager.affects:
                damage_obj = Damage(
                    damage_taker_actor = self.other,
                    damage_source_action = self,
                    damage_source_actor = self.user,
                    damage_value = int(self.user.stat_manager.stats[stat_to_heal+'_max']*power_percent),
                    damage_type = DamageType.HEALING,
                    damage_to_stat = stat_to_heal
                    )
                damage_obj.run()   

                potion_sickness = affects.Affect(
                    affect_manager = self.other.affect_manager,
                    name = 'Potion Sick',
                    description = f'Immune to potion effects',
                    turns = 3
                ) 
                self.other.affect_manager.set_affect_object(potion_sickness)      
            else:
                self.other.simple_broadcast('You are still potion sick', f'{self.other.pretty_name()} is still potion sick')  
class SkillRegenHP30(SkillRegenPercentFromPotion):
    def use(self):
        super().use(power_percent = .3, stat_to_heal = StatType.HP)
class SkillRegenMP30(SkillRegenPercentFromPotion):
    def use(self):
        super().use(power_percent = .3, stat_to_heal = StatType.MP)            

class SkillRefreshingDrink(Skill):
    def use(self):
        super().use()
        if self.success:
            power = self.script_values['bonus'][self.users_skill_level]
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_action = self,
                damage_source_actor = self.user,
                damage_value = int(self.user.stat_manager.stats[StatType.HPMAX]*power),
                damage_type = DamageType.HEALING
                )
            damage_obj.run()        
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_action = self,
                damage_source_actor = self.user,
                damage_value = int(self.user.stat_manager.stats[StatType.MPMAX]*power),
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.MP
                )
            damage_obj.run()          

class SkillAlchemy(Skill):
    def use(self):
        super().use()
        if self.success:
            failed = False
            if type(self.other).__name__ != 'Equipment' :
                failed = 'Only equipment can be alchemized'
                self.user.simple_broadcast(f'Suddenly, it mends itself again, and you feel like nothing ever happened, '+failed, 
                                        'Suddenly, it mends itself again as if nothing happened')
                return
            if self.other.keep:
                failed = 'Kept items cannot be alchemized'
                self.user.simple_broadcast(f'Suddenly, it mends itself again, and you feel like nothing ever happened, '+failed, 
                                        'Suddenly, it mends itself again as if nothing happened')
                return
            if self.other.equiped:
                failed = 'Equipped items cannot be alchemized'
                self.user.simple_broadcast(f'Suddenly, it mends itself again, and you feel like nothing ever happened, '+failed, 
                                        'Suddenly, it mends itself again as if nothing happened')
                return
            
            lvl = self.other.stat_manager.reqs[StatType.LVL] * self.other.stack
            lvl = int(lvl * self.script_values['bonus'][self.users_skill_level])
            self.user.gain_exp(lvl)
            self.user.inventory_manager.remove_item(self.other)


class SkillGetPracticePoint(Skill):
     def use(self):
        super().use()
        if self.success:
            self.other.gain_practice_points(1)


class SkillPortal(Skill):
    def use(self):
        super().use()
        if self.success:
            e_id = 'skill_portal'
            e = utils.create_npc(self.user.room.world.rooms[StaticRooms.LOADING], e_id, spawn_for_lore = True)
            e.talk_to(self.user)
            e.die()