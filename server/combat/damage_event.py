
from configuration.config import StatType, DamageType, IndentType
from utils import indent
from combat.combat_event import CombatEvent
from combat.damage_message import ReactionDamage

class Damage:
    def __init__(self, 
                 action,
                 damage_taker_actor,
                 damage_source_actor, 
                 damage_value, damage_type, 
                 damage_to_stat = StatType.HP,
                 silent = False,
                 combat_event = None):
        self.action = action
        self.damage_taker_actor = damage_taker_actor
        self.damage_source_actor = damage_source_actor
        self.damage_value = damage_value
        self.damage_type = damage_type
        self.damage_to_stat = damage_to_stat
        self.silent = silent

        self.combat_event = combat_event
        if self.combat_event == None:
            self.combat_event = CombatEvent()
            self.combat_event.add_to_queue(self)
        else:
            self.combat_event.add_to_queue(self)
            
    def run(self):
        self.combat_event.run()
        return self

    def add_self_as_reaction_to_action(self):
        if self.action == None:
            return
        reaction = ReactionDamage(  self.damage_source_actor, 
                                    self.damage_taker_actor, 
                                    self.damage_value, 
                                    self.damage_type)
        self.action.add_reaction(reaction)

    def calculate(self):
        match self.damage_type:
            # meaning the damage was completely cancelled by something
            # the affect should sendLine what exactly happened
            # example: physical damage while ethereal should send "You are ethereal"
            case DamageType.CANCELLED: 
                self.damage_value = 0
                return self
            case DamageType.PHYSICAL:
                self.damage_value -= self.damage_taker_actor.stat_manager.stats[StatType.ARMOR]
            case DamageType.MAGICAL:
                self.damage_value -= self.damage_taker_actor.stat_manager.stats[StatType.MARMOR]
            case DamageType.PURE:
                pass
            case DamageType.HEALING:
                self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] += self.damage_value
                if not self.silent:
                    self.add_self_as_reaction_to_action()
                    #self.damage_taker_actor.simple_broadcast(
                    #    indent(f'You heal {self.damage_value} {StatType.name[self.damage_to_stat]}', IndentType.MINOR),
                    #    indent(f'{self.damage_taker_actor.pretty_name()} heals {self.damage_value} {StatType.name[self.damage_to_stat]}', IndentType.MINOR)
                    #    )

                self.damage_taker_actor.stat_manager.hp_mp_clamp_update()
                return self.damage_value

        
        if self.damage_value <= 0:
            if not self.silent:
                self.add_self_as_reaction_to_action()
                #self.damage_taker_actor.simple_broadcast(
                #indent(f'You block', IndentType.MINOR),
                #indent(f'{self.damage_taker_actor.pretty_name()} blocks', IndentType.MINOR)
                #)
            return self

        self.damage_taker_actor.stat_manager.stats[self.damage_to_stat ] -= self.damage_value

        if self.damage_to_stat == StatType.HP:
            if not self.silent:
                self.add_self_as_reaction_to_action()
                #self.damage_taker_actor.simple_broadcast(
                #    indent(f'You take {self.damage_value} damage', IndentType.MINOR),
                #    indent(f'{self.damage_taker_actor.pretty_name()} takes {self.damage_value} damage', IndentType.MINOR)
                #    )
            
        if self.damage_to_stat == StatType.MP:
            if not self.silent:
                self.add_self_as_reaction_to_action()
                #self.damage_taker_actor.simple_broadcast(
                #    indent(f'You lose {self.damage_value} Magicka', IndentType.MINOR),
                #    indent(f'{self.damage_taker_actor.pretty_name()} loses {self.damage_value} Magicka', IndentType.MINOR)
                #    )


        self.damage_taker_actor.stat_manager.hp_mp_clamp_update()
        return self