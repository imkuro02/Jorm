from configuration.config import DamageType, StatType, ActorStatusType, StaticRooms
#import affects.manager as aff_manager
import affects.affects as affects
from combat.damage_event import Damage
from configuration.config import SKILLS
import random
import utils


class Skill:
    def __init__(self, skill_id, script_values, user, other, users_skill_level: int, use_perspectives, success = False, silent_use = False, no_cooldown = False, bounce = 0, combat_event = None):
        self.skill_id = skill_id
        self.name = SKILLS[skill_id]['name']
        self.script_values = script_values
        self.user = user
        self.other = other
        self.users_skill_level = users_skill_level
        self.use_perspectives = use_perspectives
        self.success = success
        self.silent_use = silent_use
        self.no_cooldown = no_cooldown
        #self.aoe = aoe # area of effect
        self.bounce = bounce # the amount of times it bounces
        self.get_dmg_value_override = None
        self.combat_event = combat_event

    def get_dmg_value(self, stat_type = None):
        if self.get_dmg_value_override == None:
            if 'crit' not in self.script_values or stat_type == None:
                dmg = self.script_values['damage'][self.users_skill_level]
            else:
                crit_min = int(self.script_values['crit'][self.users_skill_level]*80)
                crit_max = int(self.script_values['crit'][self.users_skill_level]*100)
                dmg_stat = int(self.user.stat_manager.stats[stat_type])
                dmg = self.script_values['damage'][self.users_skill_level] + int(dmg_stat * (random.randint(crit_min,crit_max)/100))
                dmg = int(dmg)

            self.get_dmg_value_override = dmg
            return self.get_dmg_value_override
        else:
            return self.get_dmg_value_override
    
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
        #print('aoe:',self.aoe)
        if not self.no_cooldown:
            cool = self.script_values['cooldown'][self.users_skill_level]
            #if cool <= 1: 
            #    cool = 2
            self.user.cooldown_manager.add_cooldown(self.skill_id, cool)

        if self.silent_use:
            return
        self.use_broadcast()

    def pre_use_get_targets(self):
        skill = SKILLS[self.skill_id]
        targets = [] # make this the first target
        for i in self.user.room.actors.values():
            if self.user.status != i.status:
                continue
            if self.other == i:
                continue
            if not skill['is_offensive']:
                if i.party_manager.get_party_id() == self.user.party_manager.get_party_id():
                    targets.append(i)
            else:
                if i.party_manager.get_party_id() != self.user.party_manager.get_party_id():
                    targets.append(i)

        
        random.shuffle(targets)
        targets.append(self.other)
        targets = targets[::-1]
        return targets

    def pre_use(self, override_bounce_amount = None):
        skill = SKILLS[self.skill_id]
        skill_obj = self.__class__
        _skill_objects = []

        targets = self.pre_use_get_targets()
        
        if override_bounce_amount == None:
            bounce_amount = skill['script_values']['bounce_amount'][self.users_skill_level] if 'bounce_amount' in skill['script_values'] else 0
        else:
            bounce_amount = override_bounce_amount

        if 'aoe' in skill['script_values']:
            current_aoe = 0
            for target in targets:

                _skill_obj = skill_obj(
                    skill_id = self.skill_id, 
                    script_values = skill['script_values'], 
                    user = self.user, 
                    other = target, 
                    users_skill_level = self.users_skill_level, 
                    use_perspectives = self.use_perspectives, 
                    success = self.success, 
                    silent_use = self.silent_use ,  
                    #aoe = False,
                    no_cooldown = self.no_cooldown,
                    bounce = bounce_amount,
                    combat_event = self.combat_event
                )
                _skill_objects.append(_skill_obj)
                if current_aoe > skill['script_values']['aoe'][self.users_skill_level]:
                    break
                current_aoe += 1

        else:
            _skill_obj = skill_obj(
                skill_id = self.skill_id, 
                script_values = skill['script_values'], 
                user = self.user, 
                other = self.other, 
                users_skill_level = self.users_skill_level, 
                use_perspectives = self.use_perspectives, 
                success = self.success, 
                silent_use = self.silent_use, 
                no_cooldown = self.no_cooldown,
                #aoe = False,
                bounce = bounce_amount,
                combat_event = self.combat_event
            )
            _skill_objects.append(_skill_obj)


        # loop for each aoe spawned skill
        for _skill_object in _skill_objects:

            _skill_object.silent_use = self.silent_use
            _skill_object.use()

            self.silent_use = True

            #first_object = False
            
            damage =  0
            bounce_loss = 0

            if _skill_object.get_dmg_value_override != None:
                damage =  _skill_object.get_dmg_value_override
                bounce_loss = int(damage/(_skill_object.bounce+1))
            
            # if there are bounces, do that
            while _skill_object.bounce >= 1:
                _skill_object.silent_use = self.silent_use
                _skill_object.bounce -= 1
                if 'bounce_bonus' in skill['script_values']:
                    damage = damage + int(damage *  skill['script_values']['bounce_bonus'][self.users_skill_level])
                _skill_object.get_dmg_value_override = damage
                
                targets = self.pre_use_get_targets()
                if _skill_object.other in targets:
                    targets.remove(_skill_object.other)
                if targets == []:
                    to_broadcast = 'no valid bounce targets'
                    #self.user.simple_broadcast(to_broadcast, to_broadcast)
                    return
                _skill_object.other = random.choice(targets)
                #self.user.simple_broadcast(_skill_object.bounce,'fjdsbfkdsaf')
                #to_broadcast = 
                #self.simple_broadcast('')
                _skill_object.use()


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
                damage_source_action = self, combat_event = self.combat_event,
                damage_value = dmg,
                damage_type = dmg_type,
                damage_to_stat = dmg_to_stat
                )

            if self.combat_event == None:
                damage_obj.run()
            # easy way of checking if a skill killed someone
            #print(f'{damage_obj.damage_taker_actor.name} {damage_obj.damage_taker_actor.status}')
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

class SkillCleave(SkillDamage):
    def use(self):
        damage_obj = super().use(dmg_stat_scale = StatType.GRIT, dmg_type = DamageType.PHYSICAL)
        if damage_obj.damage_taker_actor.status == ActorStatusType.DEAD:
            damage_obj.damage_source_actor.room.combat.order.insert(0, damage_obj.damage_source_actor)
            damage_obj.damage_source_actor.room.combat.current_actor = damage_obj.damage_source_actor
            del damage_obj.damage_source_actor.cooldown_manager.cooldowns[self.skill_id]
            #damage_obj.damage_source_actor.set_turn()
    
class SkillRefresh(SkillDamage):
    def use(self):
        self.get_dmg_value_override = self.get_dmg_value(stat_type = StatType.SOUL)
        for i in self.user.room.actors.values():
            self.other = i
            if i.party_manager.get_party_id() == self.user.party_manager.get_party_id():
                super().use(dmg_stat_scale = StatType.SOUL, dmg_type = DamageType.HEALING)
                self.silent_use = True

class SkillGuard(Skill):
    def use(self):
        super().use()
        if self.success:
            power = self.script_values['bonus'][self.users_skill_level]
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_action = self, combat_event = self.combat_event,
                damage_source_actor = self.user,
                damage_value = int(self.user.stat_manager.stats[StatType.PHYARMORMAX]*power),
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.PHYARMOR
                )
            if self.combat_event == None:
                damage_obj.run()        
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_action = self, combat_event = self.combat_event,
                damage_source_actor = self.user,
                damage_value = int(self.user.stat_manager.stats[StatType.MAGARMORMAX]*power),
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.MAGARMOR
                )
            if self.combat_event == None:
                damage_obj.run()   
    

class SkillFinisher(SkillDamageByGritFlow):
    def pre_use(self, override_bounce_amount = None):
        super().pre_use(override_bounce_amount = len(self.user.cooldown_manager.cooldowns.values()))

    def use(self):
        return super().use()

# XD children of damage skills / damage skills that deal afflictions / interesting damage skills
'''
class SkillWildMagic(Skill):
    def pre_use_get_targets(self):
        skill = SKILLS[self.skill_id]
        targets = [] # make this the first target
        for i in self.user.room.actors.values():
            if self.user.status != i.status:
                continue
            if self.other == i:
                continue
            targets.append(i)

        
        random.shuffle(targets)
        targets.append(self.other)
        targets = targets[::-1]
        return targets
    
    def pre_use(self):
        skill = SKILLS[self.skill_id]
        skill_obj = self.__class__
        _skill_obj = skill_obj(
                skill_id = self.skill_id, 
                script_values = skill['script_values'], 
                user = self.user, 
                other = self.other, 
                users_skill_level = self.users_skill_level, 
                use_perspectives = self.use_perspectives, 
                success = self.success, 
                silent_use = self.silent_use, 
                #aoe = False,
                bounce = skill['script_values']['bounce_amount'][self.users_skill_level] if 'bounce_amount' in skill['script_values'] else 0
            )
        _skill_obj.use()

        self.silent_use = True

        #first_object = False
        
        damage =  0
        bounce_loss = 0

        if _skill_obj.get_dmg_value_override != None:
            damage =  _skill_obj.get_dmg_value_override
            bounce_loss = int(damage/(_skill_obj.bounce+1))
        
        # if there are bounces, do that
        while _skill_obj.bounce >= 1:
            _skill_obj.silent_use = self.silent_use
            _skill_obj.bounce -= 1
            damage = damage + int(damage *  skill['script_values']['bounce_bonus'][self.users_skill_level])
            _skill_obj.get_dmg_value_override = damage
            
            targets = self.pre_use_get_targets()
            if _skill_obj.other in targets:
                targets.remove(_skill_obj.other)
            if targets == []:
                to_broadcast = 'no valid bounce targets'
                #self.user.simple_broadcast(to_broadcast, to_broadcast)
                return
            _skill_obj.other = random.choice(targets)
            _skill_obj.use()

    def use(self):
        damage_obj = Damage(
            damage_taker_actor = self.other,
            damage_source_actor = self.user,
            damage_source_action = self, combat_event = self.combat_event,
            damage_value = self.get_dmg_value(stat_type = StatType.MIND),
            damage_type = random.choice([DamageType.HEALING, DamageType.PHYSICAL, DamageType.MAGICAL, DamageType.PURE]),
            damage_to_stat = StatType.HP
            )

        damage_obj.run()
        return damage_obj
'''

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
                damage_source_action = self, combat_event = self.combat_event,
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
                damage_source_action = self, combat_event = self.combat_event,
                damage_value = dmg,
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.MP
                )
            if self.combat_event == None:
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
                        damage_source_action = self, combat_event = self.combat_event,
                        damage_value = dmg,
                        damage_type = DamageType.MAGICAL,
                        damage_to_stat = StatType.HP
                        )
                    if self.combat_event == None:
                        damage_obj.run()   

class SkillBash(SkillDamageByGrit):
    def use(self):
        if self.success:
            all_armors = {}
            for i in self.user.room.actors.values():
                all_armors[i] = i.stat_manager.stats[StatType.PHYARMOR]

            if self.combat_event == None:  
                damage_obj = super().use()
            
            print(damage_obj)
            if all_armors[damage_obj.damage_taker_actor] > 0:
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
            if self.combat_event == None: 
                d = super().use()
            if self.other.status != ActorStatusType.DEAD:
                if self.combat_event == None: 
                    d = super().use()
            return d





# XD skills from consumables

class SkillRegenPercentFromPotion(Skill):
    def use(self, power_percent, stat_to_heal):
        super().use()
        if self.success:
            damage_obj = Damage(
                    damage_taker_actor = self.other,
                    damage_source_action = self, combat_event = self.combat_event,
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
                damage_source_action = self, combat_event = self.combat_event,
                damage_source_actor = self.user,
                damage_value = int(self.user.stat_manager.stats[StatType.HPMAX]*power),
                damage_type = DamageType.HEALING
                )
            damage_obj.run()        
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_action = self, combat_event = self.combat_event,
                damage_source_actor = self.user,
                damage_value = int(self.user.stat_manager.stats[StatType.MPMAX]*power),
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.MP
                )
            damage_obj.run()          


    

# XD affliction only skills

class SkillNightmare(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.script_values['duration'][self.users_skill_level])
            affect = affects.AffectNightmare(
                affect_source_actor = self.user,
                affect_target_actor = self.other,
                name = 'Nightmared', description = f'Unable to act until affect wears off, damage will start your turn', 
                turns = turns,
                get_prediction_string_append = 'is sleeping!',
                get_prediction_string_clear = True)
            self.other.affect_manager.set_affect_object(affect)  

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
            damage_obj = Damage(
                damage_taker_actor = self.other,
                damage_source_action = self, combat_event = self.combat_event,
                damage_source_actor = self.user,
                damage_value = int(self.get_dmg_value(stat_type = StatType.MIND)),
                damage_type = DamageType.HEALING,
                damage_to_stat = StatType.MAGARMOR
                )
            damage_obj.run()     
            turns = int(self.script_values['duration'][self.users_skill_level])
            reduction = self.script_values['bonus'][self.users_skill_level]
            ethereal_affect = affects.AffectMageArmor(
                affect_source_actor = self.user,
                affect_target_actor = self.other, 
                name = 'Magically protected', description = f'{int(reduction*100)}% of damage is converted to Magicka damage.', 
                turns = turns, reduction = reduction)
            self.other.affect_manager.set_affect_object(ethereal_affect)  

class SkillDisorient(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.script_values['duration'][self.users_skill_level])
            #reduction = self.script_values['bonus'][self.users_skill_level]
            _effect = affects.AffectArmorReduceToZero(
                affect_source_actor = self.user,
                affect_target_actor = self.other, 
                name = 'Disoriented', description = f'All armor is reduced to 0 momentarily', 
                turns = turns)
            self.other.affect_manager.set_affect_object(_effect) 

class SkillDeflectMagic(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.script_values['duration'][self.users_skill_level])
            _effect = affects.AffectDeflectMagic(
                affect_source_actor = self.user,
                affect_target_actor = self.other, 
                name = 'Deflecting magic', description = f'All magical damage is deflected onto the original caster', 
                turns = turns)
            self.other.affect_manager.set_affect_object(_effect) 

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
                description = f'Multiply your next stab by {int(damage_bonus*100)}%',
                turns = int(self.script_values['duration'][self.users_skill_level]),
                bonus = damage_bonus
            ) 
            self.other.affect_manager.set_affect_object(stealthed_affect)  

class SkillOvercharge(Skill):
    def use(self):
        super().use()
        if self.success:
            damage_bonus = self.script_values['bonus'][self.users_skill_level]
            stealthed_affect = affects.AffectOvercharge(
                affect_source_actor = self.user,
                affect_target_actor = self.other,
                name = 'Overcharged',
                description = f'Take damage equal to {int(damage_bonus*100)}% magicka spent.',
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