from configuration.config import DamageType, StatType
from combat.damage_event import Damage
from combat.damage_message import ReactionDamage
class Affect:
    def __init__(self, action, affect_manager, name, description, turns):
        self.action = action
        self.affect_manager = affect_manager
        self.actor = self.affect_manager.actor
        self.name = name
        self.description = description
        self.turns = turns

    #def info(self):
    #    return f'{self.name:<15} {self.turns:<3} {self.description}\n'

    # called when applied 
    def on_applied(self):
        self.affect_manager.actor.simple_broadcast(
            f'You are {self.name}',
            f'{self.affect_manager.actor.pretty_name()} is {self.name}',
        )

    # called when effect is over
    def on_finished(self, silent = False):
        if not silent:
            self.affect_manager.actor.simple_broadcast(
                f'You are no longer {self.name}',
                f'{self.affect_manager.actor.pretty_name()} is no longer {self.name}',
            )
        self.affect_manager.pop_affect(self)

    # called at start of turn
    def set_turn(self):
        self.turns -= 1
        pass

    # called at end of turn
    def finish_turn(self):
        pass

    # called whenever hp updates in any way
    def take_damage(self, damage_obj):
        self.action = damage_obj.action
        return damage_obj
    
    def deal_damage(self, damage_obj):
        self.action = damage_obj.action
        return damage_obj
    
    def dealt_damage(self, damage_obj):
        self.action = damage_obj.action
        return damage_obj


class AffectStunned(Affect):
    # called at start of turn
    def set_turn(self):
        super().set_turn()
        #self.actor.simple_broadcast(
        #    f'You are too stunned to act!',
        #    f'{self.actor.pretty_name()} is too stunned to act!')
        self.actor.finish_turn()

class Leech(Affect):
    def __init__(self, action, affect_manager, name, description, turns, leech_power):
        super().__init__(action, affect_manager, name, description, turns)
        self.leech_power = leech_power

    def dealt_damage(self, damage_obj):
        if damage_obj.damage_type != DamageType.PHYSICAL:
            return damage_obj

        if damage_obj.damage_value == 0:
            return damage_obj
        
        reaction = ReactionDamage(
            self,
            damage_obj.damage_source_actor,
            round(damage_obj.damage_value * self.leech_power),
            DamageType.HEALING
        )
        
        leech_heal_damage_obj = Damage(
            action = self.action,
            damage_source_actor = self.actor,
            damage_taker_actor = self.actor,
            damage_value = round(damage_obj.damage_value * self.leech_power),
            damage_type = DamageType.HEALING,
            combat_event = damage_obj.combat_event
        )
        
        return damage_obj
    
class Thorns(Affect):
    def __init__(self, action, affect_manager, name, description, turns, damage_reflected_power):
        super().__init__(action, affect_manager, name, description, turns)
        self.damage_reflected_power = damage_reflected_power # how much in % to reflect

    def take_damage(self, damage_obj):
        super().take_damage(damage_obj)
        if damage_obj.damage_type != DamageType.PHYSICAL:
            return damage_obj

        if damage_obj.damage_value <= 0:
            return damage_obj
        
        reaction = ReactionDamage(
            self,
            damage_obj.damage_source_actor,
            int(damage_obj.damage_value * self.damage_reflected_power),
            DamageType.PURE
        )

        self.action.add_reaction(reaction)
        print('reaction added')

        thorns_damage = Damage(
            action = self.action,
            damage_source_actor = self.actor,
            damage_taker_actor = damage_obj.damage_source_actor,
            damage_value = int(damage_obj.damage_value * self.damage_reflected_power),
            damage_type = DamageType.PURE,
            combat_event = damage_obj.combat_event
        )
        
        return damage_obj

class AffectEthereal(Affect):
    def __init__(self, action, affect_manager, name, description, turns, dmg_amp):
        super().__init__(action, affect_manager, name, description, turns)
        self.dmg_amp = dmg_amp
    
    def take_damage(self, damage_obj: Damage):
        if damage_obj.damage_type == DamageType.PHYSICAL:
            damage_obj.damage_type = DamageType.CANCELLED
            damage_obj.damage_taker_actor.simple_broadcast(
                    f'You take no damage because you are ethereal',
                    f'{damage_obj.damage_taker_actor.pretty_name()} takes no damage because they are ethereal'
                    )

        if damage_obj.damage_type == DamageType.MAGICAL:
            damage_obj.damage_value = int(damage_obj.damage_value * self.dmg_amp)

        return damage_obj
    
    def deal_damage(self, damage_obj: Damage):
        if damage_obj.damage_type == DamageType.PHYSICAL:
            damage_obj.damage_type = DamageType.CANCELLED
            damage_obj.damage_source_actor.simple_broadcast(
                    f'You cannot deal damage since you are ethereal',
                    f'{damage_obj.damage_source_actor.pretty_name()} cannot deal damage since they are ethereal'
                    )
        return damage_obj

class AffectMageArmor(Affect):
    def __init__(self, action, affect_manager, name, description, turns, reduction):
        super().__init__(action, affect_manager, name, description, turns)
        self.reduction = reduction
    
    def take_damage(self, damage_obj: 'Damage'):
        match damage_obj.damage_type:
            case DamageType.CANCELLED:
                return damage_obj
            case DamageType.HEALING:
                return damage_obj
            case _:
                hp_dmg = round(damage_obj.damage_value*(1 - self.reduction))
                mp_dmg = round(damage_obj.damage_value*self.reduction)

                damage_obj.damage_taker_actor.stat_manager.stats[StatType.MP] -= mp_dmg
                if damage_obj.damage_taker_actor.stat_manager.stats[StatType.MP] <= 0:
                    hp_dmg += abs(damage_obj.damage_taker_actor.stat_manager.stats[StatType.MP])

                damage_obj.damage_value = hp_dmg

                return damage_obj
            
        if damage_obj.damage_type == DamageType.PHYSICAL:
            damage_obj.damage_type = DamageType.CANCELLED
            damage_obj.damage_taker_actor.simple_broadcast(
                    f'You take no damage because you are ethereal',
                    f'{damage_obj.damage_taker_actor.pretty_name()} takes no damage because they are ethereal'
                    )

        if damage_obj.damage_type == DamageType.MAGICAL:
            damage_obj.damage_value = int(damage_obj.damage_value * self.dmg_amp)

        return damage_obj
    
class AffectEnrage(Affect):
    def __init__(self, action, affect_manager, name, description, turns, extra_hp):
        super().__init__(action, affect_manager, name, description, turns)
        self.extra_hp = extra_hp
        self.hp = 0

    def on_applied(self):
        super().on_applied()
        self.hp = int( self.actor.stat_manager.stats[StatType.HPMAX] * self.extra_hp )
        self.actor.stat_manager.stats[StatType.HPMAX] += self.hp
        self.actor.stat_manager.stats[StatType.HP] +=    self.hp

    def on_finished(self, silent=False):
        self.actor.stat_manager.stats[StatType.HPMAX] -= self.hp
        self.actor.stat_manager.stats[StatType.HP] -=    self.hp
        self.actor.stat_manager.hp_mp_clamp_update()
        return super().on_finished(silent)