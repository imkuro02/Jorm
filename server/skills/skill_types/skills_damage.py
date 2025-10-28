from configuration.config import DamageType, StatType, ActorStatusType, StaticRooms
#import affects.manager as aff_manager
import affects.affects as affects
from combat.damage_event import Damage
from configuration.config import SKILLS
import random
import utils
#from skills.skills import Skill

class SkillDamage(Skill):
     def use(   self, 
                dmg_flat = 0,
                dmg_stat_scale = StatType.GRIT, 
                dmg_type = DamageType.PHYSICAL,
                dmg_to_stat = StatType.HP):

        super().use()
        if self.success:

            if dmg_stat_scale == None:
                dmg = dmg_flat
            else:
                dmg = self.get_dmg_value(dmg_stat_scale) +dmg_flat

            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_actor = self.user,
                damage_source_action = self,
                damage_value = dmg,
                damage_type = dmg_type,
                damage_to_stat = dmg_to_stat
                )

            damage_obj.run()


            return damage_obj

# XD parent damage skills

class SkillDamageByGrit(SkillDamage):
    def use(self):
        return super().use(dmg_stat_scale = StatType.GRIT, dmg_type = DamageType.PHYSICAL)
class SkillDamageByFlow(SkillDamage):
    def use(self):
        return super().use(dmg_stat_scale = StatType.FLOW, dmg_type = DamageType.PHYSICAL)

class SkillDamageByGritFlow(SkillDamage):
    def use(self):
        if self.user.stat_manager.stats[StatType.GRIT] > self.user.stat_manager.stats[StatType.FLOW]:
            return super().use(dmg_stat_scale = StatType.GRIT, dmg_type = DamageType.PHYSICAL)
        else:
            return super().use(dmg_stat_scale = StatType.FLOW, dmg_type = DamageType.PHYSICAL)

class SkillDamageByMind(SkillDamage):
    def use(self):
        return super().use(dmg_stat_scale = StatType.MIND, dmg_type = DamageType.MAGICAL)
class SkillDamageBySoul(SkillDamage):
    def use(self):
        return super().use(dmg_stat_scale = StatType.SOUL, dmg_type = DamageType.PURE)

class SkillCureLightWounds(SkillDamage):
    def use(self):
        return super().use(dmg_stat_scale = StatType.SOUL, dmg_type = DamageType.HEALING)

class SkillRefresh(SkillDamage):
    def use(self):
        self.get_dmg_value_override = self.get_dmg_value(stat_type = StatType.SOUL)
        for i in self.user.room.actors.values():
            self.other = i
            if i.party_manager.get_party_id() == self.user.party_manager.get_party_id():
                super().use(dmg_stat_scale = StatType.SOUL, dmg_type = DamageType.HEALING)
                self.silent_use = True

# XD children of damage skills / damage skills that deal afflictions / interesting damage skills

class SkillDamageByFlowApplyBleed(SkillDamage):
    def use(self):
        super().use(dmg_stat_scale = StatType.FLOW, dmg_type = DamageType.PHYSICAL)
        was_blocked = False 
        roll = random.randint(0,1)
        if not was_blocked:
            if roll <= self.user.stat_manager.stats[StatType.LVL] and not was_blocked:
                bleed_damage = int(self.user.stat_manager.stats[StatType.LVL]/2)
                stunned_affect = affects.AffectBleed(
                    affect_source_actor = self.user,
                    affect_target_actor = self.other,
                    name = 'Bleeding', description = f'Attackers Level as Physical damage per turn',
                    turns = 3,
                    damage = bleed_damage,
                    #get_prediction_string_append = 'is bleeding'
                )
                self.other.affect_manager.set_affect_object(stunned_affect)

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

            # Cause overfeed damage if both actors are in the same combat
            if self.user.room.combat != None:
                if self.user in self.user.room.combat.participants.values() and self.other in self.user.room.combat.participants.values():
                    over_feed_dmg = self.other.stat_manager.stats[StatType.MP] - self.other.stat_manager.stats[StatType.MPMAX] + dmg
                    if dmg > 0:
                        dmg = int(dmg * 0.5)

                    damage_obj = Damage(
                        damage_taker_actor = self.other,
                        damage_source_actor = self.user,
                        damage_source_action = self,
                        damage_value = dmg,
                        damage_type = DamageType.MAGICAL,
                        damage_to_stat = StatType.HP
                        )
                    damage_obj.run()

class SkillBash(SkillDamageByGrit):
    def use(self):
        if self.success:
            damage_obj = super().use()
            was_blocked = damage_obj.damage_value <= -1
            if not was_blocked:
                stunned_affect = affects.AffectStunned(
                    affect_source_actor = self.user,
                    affect_target_actor = self.other,
                    name = 'Stunned', description = 'Unable to act during combat turns',
                    turns = self.script_values['duration'][self.users_skill_level],
                    get_prediction_string_append = 'is stunned!',
                    get_prediction_string_clear = True
                )
                self.other.affect_manager.set_affect_object(stunned_affect)

class SkillDoubleWhack(SkillDamageByGritFlow):
    def use(self):
        if self.success:
            d = super().use()
            if self.other.status != ActorStatusType.DEAD:
                d = super().use()
            return d





# XD skills from consumables

class SkillRegenPercentFromPotion(Skill):
    def use(self, power_percent, stat_to_heal):
        super().use()
        if self.success:
            damage_obj = Damage(
                    damage_taker_actor = self.other,
                    damage_source_action = self,
                    damage_source_actor = self.user,
                    damage_value = int(self.user.stat_manager.stats[stat_to_heal+'_max']*power_percent),
                    damage_type = DamageType.HEALING,
                    damage_to_stat = stat_to_heal
                    )
            damage_obj.run()   

class SkillApplyDOT(Skill):
    def use(self, name = 'DOT', description = 'Damage over time', damage_value = 0, damage_type = DamageType.PURE, damage_to_stat = StatType.HP, turns = 10000):
        super().use()
        if self.success:
            DOT = affects.AffectDOT(
                affect_source_actor = self.user,
                affect_target_actor = self.other,
                name = name,
                description = description,
                turns = turns,
                damage_value = damage_value,
                damage_type = damage_type,
                damage_to_stat = damage_to_stat
            ) 
            self.other.affect_manager.set_affect_object(DOT)      

class SkillRegenHP30(SkillRegenPercentFromPotion):
    def use(self):
        super().use(power_percent = .3, stat_to_heal = StatType.HP)
class SkillRegenMP30(SkillRegenPercentFromPotion):
    def use(self):
        super().use(power_percent = .3, stat_to_heal = StatType.MP)            
class SkillRenewHP30(SkillApplyDOT):
    def use(self):
        power_percent = .3
        turns = 3
        damage_value = int(self.other.stat_manager.stats[StatType.HPMAX]*(power_percent/turns))
        super().use(
                name = 'Renewed', 
                description = f'Heal {int(power_percent*100)}% of your {StatType.name[StatType.HPMAX]} over {turns} turns',
                damage_value = damage_value, damage_type = DamageType.HEALING, damage_to_stat = StatType.HP, turns = turns)

class SkillRenewMP30(SkillApplyDOT):
    def use(self):
        power_percent = .3
        turns = 3
        damage_value = int(self.other.stat_manager.stats[StatType.MPMAX]*(power_percent/turns))
        super().use(
                name = 'Renewed', 
                description = f'Heal {int(power_percent*100)}% of your {StatType.name[StatType.MPMAX]} over {turns} turns',
                damage_value = damage_value, damage_type = DamageType.HEALING, damage_to_stat = StatType.MP, turns = turns)
                
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






class SkillGuard(Skill):
    def use(self):
        super().use()
        if self.success:
            power = self.script_values['bonus'][self.users_skill_level]
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_action = self,
                damage_source_actor = self.user,
                damage_value = int(self.user.stat_manager.stats[StatType.PHYARMORMAX]*power),
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.PHYARMOR
                )
            damage_obj.run()        
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_action = self,
                damage_source_actor = self.user,
                damage_value = int(self.user.stat_manager.stats[StatType.MAGARMORMAX]*power),
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.MAGARMOR
                )
            damage_obj.run()          

# XD affliction only skills

class SkillBecomeEthereal(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.script_values['duration'][self.users_skill_level])
            dmg_amp = self.script_values['bonus'][self.users_skill_level]
            ethereal_affect = affects.AffectEthereal(
                affect_source_actor = self.user,
                affect_target_actor = self.other,
                name = 'Ethereal', description = f'You take {int(dmg_amp*100)}% damage from spells, but are immune to physical damage', 
                turns = turns, dmg_amp = dmg_amp)
            self.other.affect_manager.set_affect_object(ethereal_affect)  

class SkillMageArmor(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.script_values['duration'][self.users_skill_level])
            reduction = self.script_values['bonus'][self.users_skill_level]
            ethereal_affect = affects.AffectMageArmor(
                affect_source_actor = self.user,
                affect_target_actor = self.other, 
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
                affect_source_actor = self.user,
                affect_target_actor = self.other, 
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
                affect_source_actor = self.user,
                affect_target_actor = self.other, 
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
                affect_source_actor = self.user,
                affect_target_actor = self.other,
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
            thorns_affect = affects.AffectThorns(
                affect_source_actor = self.user,
                affect_target_actor = self.other,
                name = 'Thorny',
                description = f'Reflect {int(damage_reflected_power*100)}% of physical damage back. ',
                turns = int(self.script_values['duration'][self.users_skill_level]),
                damage_reflected_power = damage_reflected_power
            ) 
            self.other.affect_manager.set_affect_object(thorns_affect)  

class SkillStealth(Skill):
    def use(self):
        super().use()
        if self.success:
            damage_bonus = self.script_values['bonus'][self.users_skill_level]
            stealthed_affect = affects.AffectStealth(
                affect_source_actor = self.user,
                affect_target_actor = self.other,
                name = 'Stealthed',
                description = f'Multiply your next attack by {int(damage_bonus*100)}%',
                turns = int(self.script_values['duration'][self.users_skill_level]),
                bonus = damage_bonus
            ) 
            self.other.affect_manager.set_affect_object(stealthed_affect)  

# XD boost main stats skills

class SkillBoostStat(Skill):
    def use(self, name_of_boost = 'boosted', stat = StatType.GRIT):
        #super().use()
        if self.success:
            turns =         int(self.script_values['duration'][self.users_skill_level])
            bonus =         self.script_values['bonus'][self.users_skill_level]
            aff   = affects.AffectBoostStat(
                    affect_source_actor = self.user,
                    affect_target_actor = self.other,
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

# XD unique skills

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