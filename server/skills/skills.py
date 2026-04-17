import random
from combat.combat_event import CombatEvent
import affects.affects as affects
import systems.utils
from combat.damage_event import Damage
from configuration.config import SKILLS


from configuration.constants.actor_status_type import ActorStatusType
from configuration.constants.damage_type import DamageType
from configuration.constants.room_constant import RoomConstant
from configuration.constants.stat_type import StatType
from configuration.constants.message_type import MessageType

class Skill:
    def __init__(
        self,
        skill_id,
        user,
        script_values = None,
        other = None,
        name = None,
        success=True,
        silent_use=False,
        no_cooldown=False,
        bounce=0,
        combat_event=None,
    ):
        self.skill_id = skill_id
        
        # used for pretty_name and pretty_broadcast 
        self.id = 'skill_id-'+skill_id

        self.name = name
        #if self.name == None:
        #    self.name = SKILLS[skill_id]["name"]

        self.script_values = script_values
        if self.script_values == None:
            self.script_values = SKILLS[skill_id]["script_values"]

        self.user = user
        self.other = other

        self.users_skill_level = 0
        if self.skill_id in self.user.skill_manager.skills:
            self.users_skill_level = self.user.skill_manager.skills[self.skill_id]

        self.success = success
        self.silent_use = silent_use
        self.no_cooldown = no_cooldown
        # self.aoe = aoe # area of effect
        self.bounce = bounce  # the amount of times it bounces
        self.get_dmg_value_override = None
        
        self.combat_event = combat_event
        if self.combat_event == None:
            self.combat_event = CombatEvent()


        self.evaluation = self.evaluate()
    
    def calculate_script_value(self, value, next_level = False):
        if value not in self.script_values:
            return 999999
            
        self.users_skill_level += next_level

        if self.users_skill_level == 0:
            return 0

        val = self.script_values[value][0]
        val = val + (self.script_values[value][2] * (self.users_skill_level -1))

        value_goes_down = self.script_values[value][0] > self.script_values[value][1]

        if value_goes_down:
            if val >= self.script_values[value][0]: val = self.script_values[value][0]
            if val <= self.script_values[value][1]: val = self.script_values[value][1]
        else:
            if val <= self.script_values[value][0]: val = self.script_values[value][0]
            if val >= self.script_values[value][1]: val = self.script_values[value][1]

        self.users_skill_level -= next_level
        val = int(val)

        return val

    def normalize_combat_event(self):
        if self.combat_event == None:
            self.combat_event = CombatEvent()
            
    def set_other_by_hp_percent_lowest(self):
        valid = self.get_valid_set_other_actors()
        best = None
        for i in valid:
            if best == None:
                best = i
            #if i.stat_manager.stats[StatType.HP] < best.stat_manager.stats[StatType.HP]:
            if i.stat_manager.stats[StatType.HP] / i.stat_manager.stats[StatType.HPMAX] < best.stat_manager.stats[StatType.HP] / best.stat_manager.stats[StatType.HPMAX]:
                best = i
        return best

    def set_other_by_threat(self):
        valid = self.get_valid_set_other_actors()
        best = None
        for i in valid:
            if best == None:
                best = i
            if i.stat_manager.stats[StatType.THREAT] > best.stat_manager.stats[StatType.THREAT]:
                best = i
        return best

    def get_valid_set_other_actors(self):
        all_actors = list(self.user.room.actors.values())
        valid = []
        for i in all_actors:
            if i == self.user and not SKILLS[self.skill_id]['target_self_is_valid']:
                continue
            if i != self.user and not SKILLS[self.skill_id]['target_others_is_valid']:
                continue

            if i.status != self.user.status:
                continue
            
            if SKILLS[self.skill_id]['is_offensive']:
                if self.user.party_manager.get_party_id() == i.party_manager.get_party_id():
                    continue
            else:
                if not self.user.party_manager.get_party_id() == i.party_manager.get_party_id():
                    continue

            valid.append(i)

        msg = f'{self.user.name} valid targets = {valid} for skill {self.skill_id}'
        self.user.simple_broadcast(msg,msg, msg_type = ['debug'])
        return valid

    def evaluate(self):
        # if a target is set then the prio is 1000
        if self.other != None:
            return 1000

        # by default get target by valid highest threat
        self.other = self.set_other_by_threat()

        # if no other is picked return 0
        if self.other == None:
            return 0
            
        # return 1 (by default)
        return 1

    '''
    def get_dmg_value(self, stat_type=None):
        if self.get_dmg_value_override == None:
            if "crit" not in self.script_values or stat_type == None:
                dmg = self.calculate_script_value(value = 'damage')
            else:
                crit_min = 0 #int(self.script_values["crit"][self.users_skill_level] * 50)
                crit_max = int(self.script_values["crit"][self.users_skill_level] * 100)
                dmg_stat = int(self.user.stat_manager.stats[stat_type])
                dmg = self.script_values["damage"][self.users_skill_level] + int(
                    dmg_stat * (random.randint(crit_min, crit_max) / 100)
                )
                dmg = int(dmg)

            # dmg = dmg + (self.user.stat_manager.stats[StatType.LVL]*2)
            self.get_dmg_value_override = dmg
            return self.get_dmg_value_override
        else:
            return self.get_dmg_value_override
    '''

    def pretty_name(self, identifier = None):
        
        if self.name == None:
            return systems.utils.add_godot_url_skill_pretty_name(identifier, self.skill_id)
        else:
            return self.name

    def use_broadcast(self):



        perspectives = {
            "you on you":       'You used #SKILL#',
            "you on other":     'You used #SKILL# on #OTHER#',
            "user on user":     '#USER# used #SKILL#',
            "user on you":      '#USER# used #SKILL# on you',
            "user on other":    '#USER# used #SKILL# on #OTHER#',
        }
       
        '''
        for perspective in perspectives:
            perspectives[perspective] = perspectives[perspective].replace(
                "#USER#", self.user.pretty_name()
            )
            perspectives[perspective] = perspectives[perspective].replace(
                "#OTHER#", self.other.pretty_name()
            )
            perspectives[perspective] = perspectives[perspective].replace(
                "#SKILL#", self.pretty_name()
            )
        '''

        for receiver in self.user.room.actors.values():
            if type(receiver).__name__ != "Player":
                continue

            _line_to_send = ''

            if receiver == self.user and receiver == self.other:
                _line_to_send = perspectives["you on you"]
                
            if receiver == self.user and receiver != self.other:
                _line_to_send = perspectives["you on other"]
                
            if (
                receiver != self.user
                and receiver != self.other
                and self.user == self.other
            ):
                _line_to_send = perspectives["user on user"]
                
            if receiver != self.user and receiver == self.other:
                _line_to_send = perspectives["user on you"]
                
            if receiver != self.user and receiver != self.other:
                _line_to_send = perspectives["user on other"]
                
            
            _line_to_send = _line_to_send.replace("#USER#", self.user.id)
            _line_to_send = _line_to_send.replace("#OTHER#", self.other.id)
            _line_to_send = _line_to_send.replace("#SKILL#", self.id)

            list_pretty_name_objects = [self, self.user, self.other]
            receiver.pretty_broadcast(
                line_self = _line_to_send,
                line_others = None,
                list_pretty_name_objects =  list_pretty_name_objects  
            )

    # runs in delay affliction if the affliction gets cancelled
    def delay_use_got_cancelled(self):
        pass
        #self.user.send_line('delayed use stopped')

    def after_use(self):
        pass

    def use(self):
        self.user.add_to_combat_history(self)

        self.normalize_combat_event()

        if not self.no_cooldown:
            cool = int(self.calculate_script_value(value = 'cooldown'))
            if cool != 0:
                self.user.cooldown_manager.add_cooldown(self.skill_id, cool)

        if not self.silent_use:
            self.use_broadcast()

        

    def pre_use_get_targets(self):
        skill = SKILLS[self.skill_id]
        targets = []  # make this the first target
        for i in self.user.room.actors.values():
            if self.user.status != i.status:
                continue
            if self.other == i:
                continue
            if (
                i.party_manager.get_party_id()
                == self.other.party_manager.get_party_id()
            ):
                targets.append(i)

        random.shuffle(targets)
        #targets.append(self.other)
        targets = targets[::-1]
        return targets

    def pre_use_attempt_to_apply_delay_affect(self, skill):
        if self.user.status != ActorStatusType.FIGHTING:
            return False
        delay = 0
        delayed_actions = []

        # delay = self.user.stat_manager.stats[StatType.LVL]
        # delayed_actions = [self]

        if "delay" in skill["script_values"]:
            delay = int(self.calculate_script_value(value = 'delay'))
            delayed_actions = [self]
        else:
            return False

        if delayed_actions != []:
            # print('delayed')
            delayed_actions_affect = affects.AffectDelayedAction(
                affect_source_actor=self.user,
                affect_target_actor=self.user,
                name=f"Charging {delayed_actions[0].name}",
                description=f"Skills will be used when this affliction is over",
                turns=delay - 1,
                skills_to_use_objects=delayed_actions,
            )
            self.user.affect_manager.set_affect_object(delayed_actions_affect)
            self.user.finish_turn()
            return True
        return False

    def pre_use(self, override_bounce_amount=None, no_delay=False):
        #self.normalize_combat_event()
        self.normalize_combat_event()

        skill = SKILLS[self.skill_id]

        self.evaluate()

        if not no_delay:
            if self.pre_use_attempt_to_apply_delay_affect(skill):
                return

        self.bounce = 0
        if 'bounce_amount' in self.script_values:
            self.bounce = self.calculate_script_value(value = 'bounce_amount')

        self.aoe = 0
        if 'aoe' in self.script_values:
            self.aoe = self.calculate_script_value(value = 'aoe')

        if self.aoe >= 1:
            used_in_aoe = [self.other]

            for i in range(0, self.aoe+1):
                self.use()
                self.combat_event.run()
                self.combat_event = CombatEvent()
                self.silent_use = True
                if len(self.pre_use_get_targets()) == 0:
                    break


                self.other = self.pre_use_get_targets()[0]
                attempts = 0
                while self.other in used_in_aoe:
                    self.other = self.pre_use_get_targets()[0]
                    attempts += 1
                    if attempts >= 10:
                        break
                
                if self.other in used_in_aoe:
                    break

                used_in_aoe.append(self.other)

        else:
            self.use()

        while self.bounce >= 2:
            self.combat_event.run()
            self.combat_event = CombatEvent()
            if len(self.pre_use_get_targets()) == 0:
                break
            self.other = self.pre_use_get_targets()[0]
            self.bounce -= 1
            self.silent_use = True
            self.no_cooldown = True
            if "bounce_bonus" in self.script_values:
                damage = self.get_dmg_value_override
                damage = damage + int(
                    damage
                    * (self.calculate_script_value(value = 'bounce_bonus')/100)
                )
                if damage <= 1:
                    damage = 1
                self.get_dmg_value_override = damage
            
            if self.aoe >= 1:
                used_in_aoe = [self.other]

                for i in range(0, self.aoe+1):
                    self.use()
                    
                    self.combat_event.run()
                    self.combat_event = CombatEvent()
                    self.silent_use = True
                    if len(self.pre_use_get_targets()) == 0:
                        break


                    self.other = self.pre_use_get_targets()[0]
                    attempts = 0
                    while self.other in used_in_aoe:
                        self.other = self.pre_use_get_targets()[0]
                        attempts += 1
                        if attempts >= 10:
                            break
                    
                    if self.other in used_in_aoe:
                        break

                    used_in_aoe.append(self.other)

            else:
                self.use()
                    
            

        '''
        if override_bounce_amount == None:
            bounce_amount = (
                self.script_values["bounce_amount"][self.users_skill_level]
                if "bounce_amount" in self.script_values
                else 0
            )
        else:
            bounce_amount = override_bounce_amount

        if "aoe" in self.script_values:
            current_aoe = 0
            targets = self.pre_use_get_targets()
            for target in targets:
                _skill_obj = skill_obj(
                    skill_id=self.skill_id,
                    name = self.name,
                    script_values=self.script_values,
                    user=self.user,
                    other=target,
                    users_skill_level=self.users_skill_level,
                    success=self.success,
                    silent_use=self.silent_use,
                    # aoe = False,
                    no_cooldown=self.no_cooldown,
                    bounce=bounce_amount,
                    combat_event=self.combat_event,
                )
                _skill_objects.append(_skill_obj)
                if current_aoe >= self.script_values["aoe"][self.users_skill_level]:
                    break
                current_aoe += 1

        else:
            _skill_obj = skill_obj(
                skill_id=self.skill_id,
                name = self.name,
                script_values=self.script_values,
                user=self.user,
                other=self.other,
                users_skill_level=self.users_skill_level,
                success=self.success,
                silent_use=self.silent_use,
                no_cooldown=self.no_cooldown,
                # aoe = False,
                bounce=bounce_amount,
                combat_event=self.combat_event,
            )
            _skill_objects.append(_skill_obj)

        # loop for each aoe spawned skill
        for _skill_object in _skill_objects:
            _skill_object.silent_use = self.silent_use
            _skill_object.no_cooldown = self.silent_use

            _skill_object.use()

            self.silent_use = True

            # first_object = False

            damage = 0
            bounce_loss = 0

            if _skill_object.get_dmg_value_override != None:
                damage = _skill_object.get_dmg_value_override
                bounce_loss = int(damage / (_skill_object.bounce + 1))

            # if there are bounces, do that
            while _skill_object.bounce >= 1:
                _skill_object.silent_use = self.silent_use
                _skill_object.no_cooldown = self.silent_use
                _skill_object.bounce -= 1
                if "bounce_bonus" in self.script_values:
                    damage = damage + int(
                        damage
                        * self.script_values["bounce_bonus"][self.users_skill_level]
                    )
                if damage <= 1:
                    damage = 1
                _skill_object.get_dmg_value_override = damage

                targets = self.pre_use_get_targets()
                if _skill_object.other in targets:
                    targets.remove(_skill_object.other)

                # self.user.simple_broadcast(str([[target.name+','+target.status] for target in targets]), str(targets))
                if targets == []:
                    to_broadcast = "*Fizzles out*"
                    self.user.simple_broadcast(to_broadcast, to_broadcast)
                    break

                _new_target = random.choice(targets)
                _skill_object.other = _new_target
                self.other = _new_target
                # _skill_object.other.combat_event = self.combat_event
                # self.user.simple_broadcast(_skill_object.bounce,'fjdsbfkdsaf')
                # to_broadcast =
                # self.simple_broadcast('')
                if self.other == None:
                    to_broadcast = "*Fizzles out*"
                    self.user.simple_broadcast(to_broadcast, to_broadcast)
                    return
                _skill_object.use()
        '''


class SkillDamage(Skill):
    def use(
        self,
        dmg_flat=0,
        dmg_stat_scale=None,
        dmg_type=DamageType.PHYSICAL,
        dmg_to_stat=StatType.HP,
    ):
        super().use()
        
        if self.success:
            if dmg_stat_scale == None:
                dmg = dmg_flat
            else:
                dmg = self.calculate_script_value(value = 'damage') + dmg_flat

            damage_obj = Damage(
                damage_taker_actor=self.other,
                damage_source_actor=self.user,
                damage_source_action=self,
                combat_event=self.combat_event,
                damage_value=dmg,
                damage_type=dmg_type,
                damage_to_stat=dmg_to_stat,
            )

            #self.combat_event.add_to_queue(damage_obj)
            #if self.combat_event == None:
            #    damage_obj.run()
            # easy way of checking if a skill killed someone
            # systems.utils.debug_print(f'{damage_obj.damage_taker_actor.name} {damage_obj.damage_taker_actor.status}')

            
            return damage_obj


# XD parent damage skills

class SkillDamageByGrit(SkillDamage):
    def use(self):
        return super().use(dmg_stat_scale=StatType.GRIT, dmg_type=DamageType.PHYSICAL)


class SkillDamageByFlow(SkillDamage):
    def use(self):
        return super().use(dmg_stat_scale=StatType.FLOW, dmg_type=DamageType.PHYSICAL)


class SkillDamageByGritFlow(SkillDamage):
    def use(self, dmg_stat_scale=StatType.GRIT, dmg_type=DamageType.PHYSICAL, dmg_flat = 0):
        if (
            self.user.stat_manager.stats[StatType.GRIT]
            > self.user.stat_manager.stats[StatType.FLOW]
        ):
            return super().use(
                dmg_stat_scale=StatType.GRIT, dmg_type=DamageType.PHYSICAL, dmg_flat = dmg_flat
            )
        else:
            return super().use(
                dmg_stat_scale=StatType.FLOW, dmg_type=DamageType.PHYSICAL, dmg_flat = dmg_flat
            )


class SkillDamageByMind(SkillDamage):
    def use(self):
        return super().use(dmg_stat_scale=StatType.MIND, dmg_type=DamageType.MAGICAL)


class SkillDamageBySoul(SkillDamage):
    def use(self):
        return super().use(dmg_stat_scale=StatType.SOUL, dmg_type=DamageType.PURE)


class SkillCureLightWounds(SkillDamage):
    def evaluate(self):
        if self.other == None:
            self.other = self.set_other_by_hp_percent_lowest()
        if self.other == None:
            return 0
        if self.other.stat_manager.stats[StatType.HP] > self.other.stat_manager.stats[StatType.HPMAX]*0.75:
            return 0
        return 2

    def use(self):
        return super().use(dmg_stat_scale=StatType.SOUL, dmg_type=DamageType.HEALING)


class SkillStrike(SkillDamage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name_prefix = ''

    def pretty_name(self, identifier = None):
        if self.name == None:
            return self.name_prefix + ' ' + systems.utils.add_godot_url_skill_pretty_name(identifier, self.skill_id)
        else:
            return self.name

    def use(self):
        
        highest_stat = StatType.GRIT
        dmg_type = DamageType.PHYSICAL
        prefix = 'Heavy'

        for i in [StatType.GRIT, StatType.FLOW, StatType.MIND, StatType.SOUL]:
            if self.user.stat_manager.stats[i] > self.user.stat_manager.stats[highest_stat]:
                highest_stat = i

        match highest_stat:
            case StatType.GRIT:
                highest_stat = StatType.GRIT
                dmg_type = DamageType.PHYSICAL
                prefix = 'Heavy'
            case StatType.FLOW:
                highest_stat = StatType.FLOW
                dmg_type = DamageType.PHYSICAL
                prefix = 'Quick'
            case StatType.MIND:
                highest_stat = StatType.MIND
                dmg_type = DamageType.MAGICAL
                prefix = 'Mindful'
            case StatType.SOUL:
                highest_stat = StatType.SOUL
                dmg_type = DamageType.MAGICAL
                prefix = 'Sacred'

        #self.name = f'{prefix} {self.name}'
        self.name_prefix = prefix
        #super().use()
        history = self.user.fetch_combat_history()
        bonus = 0
        _calculated_strike = False

        if self.user.room.combat.round -1 != 0:
            valid_packets = [_packet for _packet in history if _packet.round == self.user.room.combat.round -1]
            valid_packets = [_packet for _packet in valid_packets if _packet.actor_id == self.user.id]
            valid_packets = [_packet for _packet in valid_packets if _packet.skill_id == 'strike']

            if len(valid_packets) == 0:
                _calculated_strike = True

        if _calculated_strike:
            self.name_prefix = 'Calculated ' + self.name_prefix
            bonus = int(self.user.stat_manager.stats[StatType.FLOW]/4)

        _dmg_obj = super().use(
            dmg_stat_scale=highest_stat, dmg_type=dmg_type, dmg_flat = bonus
        )

        return _dmg_obj

class SkillGuard(Skill):
    def use(self):
        super().use()
        if self.success:
            power = (self.calculate_script_value(value = 'bonus')/100)
            turns = int(self.calculate_script_value(value = 'duration'))
            affect = affects.AffectGuarding(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Guarding",
                description=f"Guarding from physical and magical damage",
                turns=turns,
                get_prediction_string_append="is guarding!",
                get_prediction_string_clear=True,
                heal_power = power,
                dispellable = False,
            )
            self.other.affect_manager.set_affect_object(affect)

class SkillFinisher(SkillDamageByGritFlow):
    def pre_use(self, override_bounce_amount=None):
        super().pre_use(
            override_bounce_amount=len(self.user.cooldown_manager.cooldowns.values())
        )

    def use(self):
        return super().use()


# XD children of damage skills / damage skills that deal afflictions / interesting damage skills

class SkillDamageByFlowApplyBleed(SkillDamageByFlow):
    def use(self):
        # super().use(dmg_stat_scale = StatType.FLOW, dmg_type = DamageType.PHYSICAL)
        damage_obj = super().use()
        return damage_obj

    def after_use(self):
        bleed_damage = int(self.user.stat_manager.stats[StatType.LVL] / 2)
        bleeding_affect = affects.AffectBleed(
            affect_source_actor=self.user,
            affect_target_actor=self.other,
            name="Bleeding",
            description=f"Take physical damage each turn",
            turns = int(self.calculate_script_value(value = 'duration')),
            resisted_by=StatType.PHYARMOR,
            damage=bleed_damage,
            # get_prediction_string_append = 'is bleeding'
        )
        self.other.affect_manager.set_affect_object(bleeding_affect)


class SkillBash(SkillDamageByGrit):
    def use(self):
        damage_obj = super().use()
      
    def after_use(self):
        stunned_affect = affects.AffectStunned(
            affect_source_actor=self.user,
            affect_target_actor=self.other,
            name="Stunned",
            description="Unable to act during combat turns",
            turns=int(self.calculate_script_value(value = 'duration')),
            resisted_by=StatType.PHYARMOR,
            get_prediction_string_append="stunned!",
            get_prediction_string_clear=True,
        )
        self.other.affect_manager.set_affect_object(stunned_affect)


class SkillCleave(SkillDamage):
    
    def use(self):
        '''
        class CustomAffect(affects.Affect):
            def dealt_damage(self, damage_obj):
                #print(damage_obj.damage_taker_actor.stat_manager.stats[StatType.HP], damage_obj.damage_taker_actor.status)
                if damage_obj.damage_taker_actor.stat_manager.stats[StatType.HP] <= 0:
                    damage_obj.damage_source_actor.room.combat.order.insert(
                        0, damage_obj.damage_source_actor
                    )
                    damage_obj.damage_source_actor.room.combat.current_actor = (
                        damage_obj.damage_source_actor
                    )
                    del damage_obj.damage_source_actor.cooldown_manager.cooldowns['cleave']

        aff = CustomAffect(affect_source_actor=self.user, affect_target_actor=self.user, 
                          name = 'Cleaving', description = 'Get a free turn on kill with cleave', turns = 0, resisted_by= None, dispellable = False)

        #print('should be applied innit?')
        #self.user.affect_manager.set_affect_object(aff)
        '''

        damage_obj = super().use(
            dmg_stat_scale=StatType.GRIT, dmg_type=DamageType.PHYSICAL
        )
        

    def after_use(self):
        if self.other.stat_manager.stats[StatType.HP] <= 0:
            #self.user.send_line('dead enemy')
            self.user.room.combat.order.insert(
                0, self.user
            )
            self.user.room.combat.current_actor = (
                self.user
            )
            del self.user.cooldown_manager.cooldowns['cleave']
        #else:
        #    self.user.send_line('alive enemy')

            
class SkillBite(SkillDamageByGritFlow):
    def use(self):
        # apply flat damage for all bites used this combat
        history = self.user.fetch_combat_history()

        bonus = 0
        for packet in history:
            #print(packet.__dict__, self.user.room.combat.round)
            #if packet.round != self.user.room.combat.round:
                #print(packet.skill, packet.round, self.user.room.combat.round)
            #    continue
            #if packet.actor_id != self.user.id:
            #    continue
            
            if packet.skill_id == 'bite':
                bonus += 2
            
        super().use(dmg_flat = bonus)
        #damage_obj = super().use(
        #    dmg_stat_scale=StatType.GRIT, dmg_type=DamageType.PHYSICAL, dmg_flat = bonus * 1
        #)

class SkillDoubleWhack(SkillDamageByGritFlow):
    def use(self):
        if self.success:

            d = super().use()
            if self.other.status != ActorStatusType.DEAD:
                d = super().use()
            return d

class SkillFireball(SkillDamage):
    def pretty_name(self, identifier = None):
        if hasattr(self, 'fireball_dmg_obj'):
            if self.fireball_dmg_obj.damage_type == DamageType.PHYSICAL:
                return 'Knuckle-Sandwich ' + systems.utils.add_godot_url_skill_pretty_name(identifier, self.skill_id)

        if self.name == None:
            return systems.utils.add_godot_url_skill_pretty_name(identifier, self.skill_id)
        else:
            return self.name

    def delay_use_got_cancelled(self):
        self.other = self.user
        _dmg_obj = super().use(dmg_stat_scale=StatType.MIND, dmg_type=DamageType.MAGICAL)
        self.fireball_dmg_obj = _dmg_obj
        return _dmg_obj

    def use(self):
        _dmg_obj = super().use(dmg_stat_scale=StatType.MIND, dmg_type=DamageType.MAGICAL)
        self.fireball_dmg_obj = _dmg_obj
        return _dmg_obj

# XD skills from consumables

class SkillFlatHeal(SkillDamage):
    def use(self, power, stat_to_heal):

        #if healing is negative then jsut deal pure dmg
        dmg_type = DamageType.HEALING
        if power <= -1:
            dmg_type = DamageType.PURE

        power = abs(power)

        return super().use(
            dmg_flat=power,
            dmg_stat_scale=None,
            dmg_type=dmg_type,
            dmg_to_stat=stat_to_heal,
            )
        
class SkillFlatHealHP(SkillFlatHeal):
    def use(self):
        return super().use(power = self.users_skill_level, stat_to_heal = StatType.HP)

class SkillFlatHealPA(SkillFlatHeal):
    def use(self):
        return super().use(power = self.users_skill_level, stat_to_heal = StatType.PHYARMOR)

class SkillFlatHealMA(SkillFlatHeal):
    def use(self):
        return super().use(power = self.users_skill_level, stat_to_heal = StatType.MAGARMOR)

'''
class SkillRegenPercentFromPotion(Skill):
    def use(self, power_percent, stat_to_heal):
        super().use()
        if self.success:
            damage_obj = Damage(
                damage_taker_actor=self.other,
                damage_source_action=self,
                combat_event=self.combat_event,
                damage_source_actor=self.user,
                damage_value=int(
                    self.user.stat_manager.stats[stat_to_heal + "_max"] * power_percent
                ),
                damage_type=DamageType.HEALING,
                damage_to_stat=stat_to_heal,
            )
            
            return damage_obj
'''

class SkillApplyDOT(Skill):
    def use(
        self,
        name="DOT",
        description="Damage over time",
        damage_value=0,
        damage_type=DamageType.PURE,
        damage_to_stat=StatType.HP,
        turns=10000,
    ):
        super().use()
        if self.success:
            DOT = affects.AffectDOT(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name=name,
                description=description,
                turns=turns,
                damage_value=damage_value,
                damage_type=damage_type,
                damage_to_stat=damage_to_stat,
            )
            self.other.affect_manager.set_affect_object(DOT)

'''
class SkillPercentAllHeal(SkillRegenPercentFromPotion):
    def use(self):
        self.silent_use = True
        power_percent = (self.users_skill_level/100)
    
        dmg_1 = super().use(power_percent = power_percent, stat_to_heal = StatType.HP)
        dmg_2 = super().use(power_percent = power_percent, stat_to_heal = StatType.PHYARMOR)
        dmg_3 = super().use(power_percent = power_percent, stat_to_heal = StatType.MAGARMOR)
'''

class SkillRefreshingDrink(Skill):
    def use(self):
        super().use()
        if self.success:
            power = (self.calculate_script_value(value = 'bonus')/100)
            damage_obj = Damage(
                damage_taker_actor=self.other,
                damage_source_action=self,
                combat_event=self.combat_event,
                damage_source_actor=self.user,
                damage_value=int(self.user.stat_manager.stats[StatType.HPMAX] * power),
                damage_type=DamageType.HEALING,
            )
            
            

# XD affliction only skills
class SkillNightmare(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.calculate_script_value(value = 'duration'))
            affect = affects.AffectNightmare(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Nightmared",
                description=f"Unable to act until affect wears off, damage will start your turn",
                turns=turns,
                get_prediction_string_append="is sleeping!",
                get_prediction_string_clear=True,
            )
            self.other.affect_manager.set_affect_object(affect)


class SkillBecomeEthereal(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.calculate_script_value(value = 'duration'))
            dmg_amp = (self.calculate_script_value(value = 'bonus')/100)
            ethereal_affect = affects.AffectEthereal(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Ethereal",
                description=f"You take {int(dmg_amp * 100)}% damage from spells, but are immune to physical damage",
                turns=turns,
                dmg_amp=dmg_amp,
            )
            self.other.affect_manager.set_affect_object(ethereal_affect)

class SkillMendArmor(Skill):
    def evaluate(self):
        if self.other == None:
            self.other = self.set_other_by_hp_percent_lowest()
        if self.other == None:
            return 0
        if self.other.stat_manager.stats[StatType.HP] > self.other.stat_manager.stats[StatType.HPMAX]*0.75:
            return 0
        return 2
        
    def use(self):
        super().use()

        dmg = self.calculate_script_value(value = 'damage') + int(
            (
                self.user.stat_manager.stats[StatType.MIND]
                + self.user.stat_manager.stats[StatType.SOUL]
            )
            / 1
        )

        damage_obj = Damage(
            damage_taker_actor=self.other,
            damage_source_action=self,
            combat_event=self.combat_event,
            damage_source_actor=self.user,
            damage_value=dmg,
            damage_type=DamageType.HEALING,
            damage_to_stat=StatType.MAGARMOR,
        )

        damage_obj = Damage(
            damage_taker_actor=self.other,
            damage_source_action=self,
            combat_event=self.combat_event,
            damage_source_actor=self.user,
            damage_value=dmg,
            damage_type=DamageType.HEALING,
            damage_to_stat=StatType.PHYARMOR,
        )

        #self.combat_event.run()
        return damage_obj            

class SkillDisorient(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.calculate_script_value(value = 'duration'))
            # reduction = self.script_values['bonus'][self.users_skill_level]
            _effect = affects.AffectArmorReduceToZero(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Disoriented",
                description=f"All armor is reduced to 0 momentarily",
                turns=turns,
                dispellable=False,
                #resisted_by=None
            )
            self.other.affect_manager.set_affect_object(_effect)


class SkillDeflectMagic(Skill):
    def use(self):
        super().use()
        if self.success:
            turns = int(self.calculate_script_value(value = 'duration'))
            _effect = affects.AffectDeflectMagic(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Deflecting magic",
                description=f"All magical damage is deflected onto the original caster",
                turns=turns,
            )
            self.other.affect_manager.set_affect_object(_effect)

class SkillLeech(Skill):
    def use(self):
        super().use()
        if self.success:
            leech_power = (self.calculate_script_value(value = 'bonus')/100)
            # affect_manager, name, description, turns
            leech_affect = affects.Leech(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Leeching",
                description=f"Convert {int(leech_power * 100)}% of physical damage dealt to healing.",
                turns=int(self.calculate_script_value(value = 'duration')),
                leech_power=leech_power,
            )

            self.other.affect_manager.set_affect_object(leech_affect)


class SkillThorns(Skill):
    def evaluate(self):
        # if a target is set then the prio is 1000
        if self.other != None:
            return 1000

        self.other = self.user

        # if no other is picked return 0
        if self.other == None:
            return 0
            
        # return 1 (by default)
        return 2
    def use(self):
        super().use()
        if self.success:
            damage_reflected_power = (self.calculate_script_value(value = 'bonus')/100)
            thorns_affect = affects.AffectThorns(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Thorny",
                description=f"Reflect {int(damage_reflected_power * 100)}% of physical damage back. ",
                turns=int(self.calculate_script_value(value = 'duration')),
                damage_reflected_power=damage_reflected_power,
            )
            self.other.affect_manager.set_affect_object(thorns_affect)


class SkillStealth(Skill):
    def use(self):
        super().use()
        if self.success:
            damage_bonus = (self.calculate_script_value(value = 'bonus')/100)
            stealthed_affect = affects.AffectStealth(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Stealthed",
                description=f"Multiply your next stab by {int(damage_bonus * 100)}%",
                turns=int(self.calculate_script_value(value = 'duration')),
                bonus=damage_bonus,
            )
            self.other.affect_manager.set_affect_object(stealthed_affect)

# XD boost main stats skills


class SkillBoostStat(Skill):
    def use(self, name_of_boost="boosted", stat=StatType.GRIT):
        # super().use()
        if self.success:
            turns = int(self.calculate_script_value(value = 'duration'))
            bonus = (self.calculate_script_value(value = 'bonus')/100)
            if int(self.other.stat_manager.stats[stat] * bonus) < 0:
                bonus_str = f'{int(self.other.stat_manager.stats[stat] * bonus)}'
            else:
                bonus_str = f'+{int(self.other.stat_manager.stats[stat] * bonus)}'
            aff = affects.AffectBoostStat(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name=name_of_boost,
                description=f"Temporary boost {StatType.name[stat].lower()} by {int(bonus * 100)}% ({bonus_str})",
                turns=turns,
                bonus=bonus,
                stat=stat,
            )
            self.other.affect_manager.set_affect_object(aff)


class SkillBoostStatGrit(SkillBoostStat):
    def use(self):
        Skill.use(self)
        super().use(name_of_boost="Grit Blessed", stat=StatType.GRIT)


class SkillBoostStatFlow(SkillBoostStat):
    def use(self):
        Skill.use(self)
        super().use(name_of_boost="Flow Blessed", stat=StatType.FLOW)


class SkillBoostStatMind(SkillBoostStat):
    def use(self):
        Skill.use(self)
        super().use(name_of_boost="Mind Blessed", stat=StatType.MIND)


class SkillBoostStatSoul(SkillBoostStat):
    def use(self):
        Skill.use(self)
        super().use(name_of_boost="Soul Blessed", stat=StatType.SOUL)


class SkillBoostStats(SkillBoostStat):
    def use(self):
        Skill.use(self)
        super().use(name_of_boost="Grit Blessed", stat=StatType.GRIT)
        super().use(name_of_boost="Flow Blessed", stat=StatType.FLOW)
        super().use(name_of_boost="Mind Blessed", stat=StatType.MIND)
        super().use(name_of_boost="Soul Blessed", stat=StatType.SOUL)



'''
class SkillConsumeCorpsesOnSetTurn(Skill):
    def use(self):
        from affects.affects import Affect
        class AffectConsumeCorpsesOnSetTurn(Affect):
            def __init__(self, *args, **kwargs):
                self.percentage_healing = kwargs['percentage_healing']
                
                del kwargs['percentage_healing']
                super().__init__(*args, **kwargs)

                self.healing_value = self.affect_target_actor.stat_manager.stats[StatType.HPMAX] * self.percentage_healing

            def wont_overheal(self):
                #msg = f'{self.affect_target_actor.stat_manager.stats[StatType.HP]}, {self.affect_target_actor.stat_manager.stats[StatType.HPMAX]}'
                #self.affect_target_actor.simple_broadcast(msg,msg)
                if self.affect_target_actor.stat_manager.stats[StatType.HP] + self.healing_value >= self.affect_target_actor.stat_manager.stats[StatType.HPMAX]:
                    return True
                return False

            def check_if_corpses_present(self):
                items = []
                for i in self.affect_target_actor.room.inventory_manager.items.values():
                    items.append(i)

                for i in items:
                    if hasattr(i, 'corpse_npc_id'):
                        return i
                
                return False
            def take_damage_after_calc(self, damage):
                if not self.wont_overheal():
                    self.get_prediction_string_append = 'hungry!'
                    self.get_prediction_string_clear=True
                else:
                    self.get_prediction_string_append=None
                    self.get_prediction_string_clear=False
                return damage
                #self.affect_target_actor.prediction_override = 'will canibalize a corpse'
            
            def set_turn(self):

                # check if a corpse is present, and stop if not
                corpse = self.check_if_corpses_present()

                if corpse == False:
                    return

                if self.wont_overheal():
                    return
               
                # set turn to 0 to have retty name not print out duration
                self.turns = 0

                # skip eating a corpse if it would overheal you

                # print message and remove corpse from room
                msg_o = f'{self.affect_target_actor.id} consumes {corpse.id}'
                msg_s = f'You consume {corpse.id}'
                list_pretty_name_objects = [self.affect_target_actor, corpse]
                self.affect_target_actor.pretty_broadcast(msg_s, msg_o, list_pretty_name_objects = list_pretty_name_objects)
                self.affect_target_actor.room.inventory_manager.remove_item(corpse)

                # calculate healing and run it
                healing = int(self.healing_value)
                damage_obj = Damage(
                    damage_taker_actor=self.affect_target_actor,
                    damage_source_action=self,
                    #combat_event=self.combat_event,
                    damage_source_actor=self.affect_target_actor,
                    damage_value=healing,
                    damage_type=DamageType.HEALING,
                )
                damage_obj.run()

                # set turns back to 1
                self.turns = 1

                # finish current turn
                self.affect_target_actor.finish_turn()

        if self.success:
            affect = AffectConsumeCorpsesOnSetTurn(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Canibalizing",
                description=f"Abruptly stop your current action to consume a corpse",
                turns=int(self.script_values["duration"][self.users_skill_level]),
                percentage_healing = self.script_values["bonus"][self.users_skill_level],
                hidden = True
            )
            self.other.affect_manager.set_affect_object(affect) 
'''

class SkillAreaOfEffectDamageOnFinished(Skill):
    def use(self):
        if self.success:
            affect = affects.AffectAreaOfEffectDamageOnFinished(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Detonating",
                description=f"Dealing max life damage to all enemies on finished",
                turns=int(self.calculate_script_value(value = 'duration')),
            )
            self.other.affect_manager.set_affect_object(affect)

class SkillSlimeApplyCooldown(Skill):
    def use(self):
        super().use()
        if self.success:
            '''
            armor_percentage = self.other.stat_manager.stats[StatType.MAGARMOR] / self.other.stat_manager.stats[StatType.MAGARMORMAX]

            amount = 10 - (10 * armor_percentage)
            amount = int(amount) 
            while amount > 0:
                skill_id = random.choice(list(self.other.skill_manager.skills.keys()))
                amount -= 1

                x = 1
                if skill_id not in self.other.cooldown_manager.cooldowns:
                    x = 2

                self.other.cooldown_manager.add_cooldown(skill_id, x)
                msg_s = f'Your {SKILLS[skill_id]["name"]} is slimed'
                msg_o = f'{self.other.id}\'s {SKILLS[skill_id]["name"]} is slimed'
                list_pretty_name_objects = [self.other]
                self.other.pretty_broadcast(msg_s, msg_o, msg_type=[MessageType.COMBAT], list_pretty_name_objects = list_pretty_name_objects)
            '''
            skill_id = random.choice(list(self.other.skill_manager.skills.keys()))

            x = int(self.calculate_script_value(value = 'duration'))

            self.other.cooldown_manager.add_cooldown(skill_id, x)
            msg_s = f'Your {SKILLS[skill_id]["name"]} is slimed'
            msg_o = f'{self.other.id}\'s {SKILLS[skill_id]["name"]} is slimed'
            list_pretty_name_objects = [self.other]
            self.other.pretty_broadcast(msg_s, msg_o, msg_type=[MessageType.COMBAT], list_pretty_name_objects = list_pretty_name_objects)
            
                
class SkillDispel(Skill):
    def use(self):
        super().use()
        if self.success:
            #is_ally = (
            #    self.other.party_manager.get_party_id()
            #    == self.user.party_manager.get_party_id()
            #)
            is_ally = self.other.party_manager.get_is_friendly(self.user)
            
            affs = self.other.affect_manager.affects.values()
            #print(is_ally, affs)
            to_dispel = []
            if is_ally:
                for i in affs:
                    if i.dispellable and i.resisted_by != None:
                        to_dispel.append(i)

            if not is_ally:
                for i in affs:
                    if i.dispellable and i.resisted_by == None:
                        to_dispel.append(i)

            if to_dispel == []:
                self.user.send_line("Nothing to dispel")
                return

            dispel_this = random.choice(to_dispel)
            dispel_this.on_finished()

            if is_ally:
                damage_obj = Damage(
                    damage_taker_actor=self.other,
                    damage_source_action=self,
                    combat_event=self.combat_event,
                    damage_source_actor=self.user,
                    damage_value=int(self.user.stat_manager.stats[StatType.SOUL]),
                    damage_type=DamageType.HEALING,
                )
            else:
                damage_obj = Damage(
                    damage_taker_actor=self.other,
                    damage_source_action=self,
                    combat_event=self.combat_event,
                    damage_source_actor=self.user,
                    damage_value=int(self.user.stat_manager.stats[StatType.MIND]),
                    damage_type=DamageType.MAGICAL,
                )
            #self.combat_event.run()
            return damage_obj
            


class SkillGetPracticePoint(Skill):
    def use(self):
        super().use()
        if self.success:
            self.other.gain_practice_points(1)


class SkillPortal(Skill):
    def use(self):
        super().use()
        if self.success:
            e_id = "skill_portal"
            e = systems.utils.create_npc(
                self.user.room.world.rooms[RoomConstant.LOADING],
                e_id,
                spawn_for_lore=True,
            )
            e.talk_to(self.user)
            e.die()


class SkillPromise(Skill):
    def evaluate(self):
        if self.other == None:
            self.other = self.set_other_by_hp_percent_lowest()
        if self.other == None:
            return 0
        if self.other.stat_manager.stats[StatType.HP] > self.other.stat_manager.stats[StatType.HPMAX]*0.75:
            return 0
        return 2
        
    def use(self):
        super().use()
        if self.success:
            # damage_bonus = self.script_values['bonus'][self.users_skill_level]
            stealthed_affect = affects.AffectPromise(
                affect_source_actor=self.user,
                affect_target_actor=self.other,
                name="Promised",
                description=f"Pause all healing and damage",
                turns=int(self.calculate_script_value(value = 'duration')),
            )
            self.other.affect_manager.set_affect_object(stealthed_affect)

# XD Summon
# testing stuff here
'''
class SkillSummon(Skill):
    def get_party_id(self):
        return self.user.party_manager.get_party_id()

    def use(self, npc_summon_id):
        super().use()
        from actors.npcs import create_npc
        e = create_npc(self.user.room, npc_summon_id)
       
        e.party_manager.get_party_id = self.get_party_id
        e.name = e.name.replace('The','The Summoned')
        e.loot = {}
        e.stat_manager.stats[StatType.EXP] = 0
        e.npc_id = f'summoned_{e.npc_id}'
        e.reset_stats_after_combat = False

        turns = int(self.script_values["duration"][self.users_skill_level])
        affect = affects.AffectSummoner(
            affect_source_actor=self.user,
            affect_target_actor=self.other,
            name="Summoner",
            description=f"You have summoned someone or something.",
            turns = turns*100,
            dispellable = False,
            summoned_actor = e,
        )
        self.other.affect_manager.set_affect_object(affect)

        if self.user.status == ActorStatusType.FIGHTING:
            self.user.room.combat.add_participant(e)

class SkillSummonRat(SkillSummon):
    def use(self):
        super().use('rat')
'''

class SkillTargetItem(Skill):
    def pre_use(self):
        self.use()

class SkillConsumeCorpse(SkillTargetItem):
    def check_if_corpses_present(self):
        items = []
        for i in self.user.room.inventory_manager.items.values():
            items.append(i)

        for i in items:
            if hasattr(i, 'corpse_npc_id'):
                return i

        return None

    def get_healing_value(self):
        return int(self.user.stat_manager.stats[StatType.HPMAX] * (self.calculate_script_value(value = 'bonus')/100) )

    def evaluate(self):
        if self.other != None:
            return 1000

        corpse = self.check_if_corpses_present()
        
        if corpse == False:
            return 0

        if self.user.stat_manager.stats[StatType.HP] + self.get_healing_value() >= self.user.stat_manager.stats[StatType.HPMAX]:
            return 0

        self.other = corpse
        return 2

    def use(self):
        if self.other == None:
            self.other = self.check_if_corpses_present()

        if self.other == None:
            self.user.send_line(f'There are no corpses to eat')
            return

        if not hasattr(self.other, 'corpse_npc_id'):
            self.user.send_line(f'You cannot canibalize {self.other.name}')
            return False

        if self.other not in self.user.room.inventory_manager.items.values():
            msg_o = f'{self.user.id} becomes visibly confused at the lack of a corpse'
            msg_s = f'You become upset and confused at the lack of a corpse'
            list_pretty_name_objects = [self.user]
            self.user.pretty_broadcast(msg_s, msg_o, list_pretty_name_objects = list_pretty_name_objects)
            return False

        #if self.other != None:
        #    corpse = self.other

        super().use()

        msg_o = f'{self.user.id} consumes {self.other.id}'
        msg_s = f'You consume {self.other.id}'
        list_pretty_name_objects = [self.user, self.other]
        self.user.pretty_broadcast(msg_s, msg_o, list_pretty_name_objects = list_pretty_name_objects)
        self.user.room.inventory_manager.remove_item(self.other)

        # calculate healing and run it
        healing = self.get_healing_value()
        damage_obj = Damage(
            damage_taker_actor=self.user,
            damage_source_action=self,
            combat_event=self.combat_event,
            damage_source_actor=self.user,
            damage_value=healing,
            damage_type=DamageType.HEALING,
        )
        #self.combat_event.run()
        return damage_obj


class SkillNecromancerRessurect(SkillTargetItem):
    def check_if_corpses_present(self):
        items = []
        for i in self.user.room.inventory_manager.items.values():
            items.append(i)

        for i in items:
            if hasattr(i, 'corpse_npc_id'):
                return i

        return None

    def use(self):
        from actors.ai import EnemyAI
        from types import MethodType
        from actors.npcs import Npc
        from configuration.config import ENEMIES

        if self.other == None:
            self.other = self.check_if_corpses_present()

        if self.other == None:
            self.user.send_line(f'There are no corpses to ressurect')
            return
  
        if not hasattr(self.other, 'corpse_npc_id'):
            self.user.send_line(f'You cannot resurrect {self.other.name}')
            return False

        super().use()

        if hasattr(self.other, 'corpse_npc_id'):
            # remove corpse item on ground
            self.other.inventory_manager.remove_item(self.other)

            # send_line
            self.user.simple_broadcast(f'You resurrect {self.other.corpse_npc_name}',f'{self.user.pretty_name()} resurrects {self.other.corpse_npc_name}')

            npc_class = Npc
            npc_id = self.other.corpse_npc_id
            e = npc_class(
                npc_id = f'summoned_{npc_id}',
                ai = EnemyAI,
                name = self.other.corpse_npc_name.replace('The','The resurrected'),
                description = ENEMIES[npc_id]["description"],
                room = self.user.room,
                stats = ENEMIES[npc_id]["stats"],
                loot = {},
                skills = ENEMIES[npc_id]["skills"],
                dialog_tree = None,
                can_start_fights = True,
                dont_join_fights = False,
                on_death_skills_use = ENEMIES[npc_id]["on_death_skills_use"],
                on_start_skills_use = ENEMIES[npc_id]["on_start_skills_use"],
            )

            #self.user.room.move_actor(e, silent=True)

            e.stat_manager.stats[StatType.HPMAX] =       int(e.stat_manager.stats[StatType.HPMAX]/3) + self.user.stat_manager.stats[StatType.SOUL]
            e.stat_manager.stats[StatType.PHYARMORMAX] = int(e.stat_manager.stats[StatType.PHYARMORMAX]/3) + self.user.stat_manager.stats[StatType.SOUL]
            e.stat_manager.stats[StatType.MAGARMORMAX] = int(e.stat_manager.stats[StatType.MAGARMORMAX]/3) + self.user.stat_manager.stats[StatType.SOUL]

            e.stat_manager.stats[StatType.HP] =      e.stat_manager.stats[StatType.HPMAX]
            e.stat_manager.stats[StatType.PHYARMOR] = e.stat_manager.stats[StatType.PHYARMORMAX]
            e.stat_manager.stats[StatType.MAGARMOR] = e.stat_manager.stats[StatType.MAGARMORMAX]

            e.reset_stats_after_combat = False

            # triggers
            def trigger_dismiss(self, player, line):
                line = line.replace('dismiss','',1)
                
                if player != self.player_that_ressurected_me:
                    return False

                target = line

                tar = player.get_actor(target)

                if tar != self:
                    return False

                player.simple_broadcast(
                    f'You dismiss {self.name}',
                    f'{player.pretty_name()} dismisses {self.name}')

                self.die()
                return True

            def trigger_rename(self, player, line):
                line = line.replace('rename','',1)
                
                if player != self.player_that_ressurected_me:
                    return False
                
                if ' to ' not in line:
                    player.send_line(f'Rename {self.name} to what?')
                    return False

                _split = line.split(' to ')
                target = _split[0]
                new_name = _split[1]

                tar = player.get_actor(target)

                if tar != self:
                    return False

                player.simple_broadcast(
                    f'You rename {self.name} to "{new_name}"',
                    f'{player.pretty_name()} renames {self.name} to "{new_name}"')

                self.name = new_name
                return True

            
            # link get_party_id to master party id
            e.party_manager.get_party_id = MethodType(
                type(self.user.party_manager).get_party_id,  # unbound function
                self.user.party_manager                      # bind to USER party manager
            )

            # link triggers 
            e.trigger_rename = MethodType(
                trigger_rename,       # unbound function
                e   # bind to SUMMONED ACTOR 
            )

            e.trigger_dismiss = MethodType(
                trigger_dismiss,      # unbound function
                e   # bind to SUMMONED ACTOR 
            )

            # honestly forgor wat this do
            e.player_that_ressurected_me = self.user
            
            # add trigger keys
            e.trigger_manager.trigger_add('rename', e.trigger_rename)
            e.trigger_manager.trigger_add('dismiss', e.trigger_dismiss)

            # add trigger descriptions
            e.description += f'\nResurrected by {self.user.name}'
            e.description += f'\nCan be renamed with "rename <name> to <new name>".'
            e.description += f'\nCan be dismissed with "dismiss <name>".'
            e.stat_manager.stats[StatType.EXP] = 0
            # create aff
            affect = affects.AffectSummoner(
                affect_source_actor=self.user,
                affect_target_actor=self.user,
                name="Necrobound",
                description=f"You have summoned someone or something.",
                turns = self.user.stat_manager.stats[StatType.SOUL],
                dispellable = False,
                summoned_actor = e,
            )

            # set aff on player
            self.user.affect_manager.set_affect_object(affect)

            if self.user.status == ActorStatusType.FIGHTING:
                self.user.room.combat.add_participant(e)

       

