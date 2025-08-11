
from configuration.config import StatType, DamageType, IndentType
from utils import indent
from combat.combat_event import CombatEvent
class Damage:
    def __init__(self, 
                 damage_taker_actor,
                 damage_source_action,
                 damage_source_actor, 
                 damage_value, damage_type, 
                 damage_to_stat = StatType.HP,
                 silent = False,
                 combat_event = None):
        self.damage_source_action = damage_source_action
        self.damage_taker_actor = damage_taker_actor
        self.damage_source_actor = damage_source_actor
        self.damage_value = damage_value
        self.damage_blocked_value = 0 # the amount that is blocked by armor and marmor
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

    # if the damage is negative, this means that the damage has been blocked by armor or marmor
    # if its positive, assume that the armor is broken and damage is dealt directly to hp / whatever stat
    def calculate(self):
        
        #lvl_taker = self.damage_taker_actor.stat_manager.stats[StatType.LVL]
        #lvl_source = self.damage_taker_actor.stat_manager.stats[StatType.LVL]
        #lvl_diff = lvl_source - lvl_taker
        #if lvl_diff <= 0:
        #    lvl_diff = 0

        # add 20% of max hp of the taker to damage
        #if self.damage_taker_actor.room.combat != None:
        #    combat_round = self.damage_taker_actor.room.combat.round
        #    taker_max_hp = self.damage_taker_actor.stat_manager.stats[StatType.HPMAX]
        #    self.damage_value += int(self.damage_value * (0.05 * (combat_round-1)))
        
        if self.damage_value <= 0:
            return self
            
        match self.damage_type:
            # meaning the damage was completely cancelled by something
            # the affect should sendLine what exactly happened
            # example: physical damage while ethereal should send "You are ethereal"
            case DamageType.CANCELLED: 
                self.damage_value = 0
                return self

            case DamageType.PHYSICAL:
                self.damage_taker_actor.stat_manager.stats[StatType.PHYARMOR] -= self.damage_value
                if self.damage_taker_actor.stat_manager.stats[StatType.PHYARMOR] < 0:
                    self.damage_value = -1*self.damage_taker_actor.stat_manager.stats[StatType.PHYARMOR]
                    self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] -= self.damage_value
                else:
                    self.damage_value = -1*self.damage_value
                    

            case DamageType.MAGICAL:
                self.damage_taker_actor.stat_manager.stats[StatType.MAGARMOR] -= self.damage_value
                if self.damage_taker_actor.stat_manager.stats[StatType.MAGARMOR] < 0:
                    self.damage_value = -1*self.damage_taker_actor.stat_manager.stats[StatType.MAGARMOR]
                    self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] -= self.damage_value
                else:
                    self.damage_value = -1*self.damage_value
                    

            case DamageType.PURE:
                self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] -= self.damage_value
                pass
                
            case DamageType.HEALING:
                self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] += self.damage_value
                return self.damage_value

        '''
        if self.damage_value <= 0:
            if not self.silent:
                self.damage_taker_actor.simple_broadcast(
                indent(f'You block', IndentType.MINOR),
                indent(f'{self.damage_taker_actor.pretty_name()} blocks', IndentType.MINOR)
                )
            return self
        '''

        #if self.damage_value <= 0:
        #    self.damage_value = 0
    
        #self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] -= self.damage_value

        '''
        if self.damage_to_stat == StatType.HP:
            if not self.silent:
                self.damage_taker_actor.simple_broadcast(
                    indent(f'You take {self.damage_value} damage', IndentType.MINOR),
                    indent(f'{self.damage_taker_actor.pretty_name()} takes {self.damage_value} damage', IndentType.MINOR)
                    )
            
        if self.damage_to_stat == StatType.MP:
            if not self.silent:
                self.damage_taker_actor.simple_broadcast(
                    indent(f'You lose {self.damage_value} Magicka', IndentType.MINOR),
                    indent(f'{self.damage_taker_actor.pretty_name()} loses {self.damage_value} Magicka', IndentType.MINOR)
                    )
        '''


        #self.damage_taker_actor.stat_manager.hp_mp_clamp_update()

        
        return self