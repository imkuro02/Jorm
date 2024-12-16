from config import DamageType, StatType
from combat.manager import Damage

class Affect:
    def __init__(self, _id, affect_manager, name, description, turns):
        self.id = _id
        self.affect_manager = affect_manager
        self.owner = self.affect_manager.owner
        self.name = name
        self.description = description
        self.turns = turns

    #def info(self):
    #    return f'{self.name:<15} {self.turns:<3} {self.description}\n'

    # called when applied 
    def on_applied(self):
        self.affect_manager.owner.simple_broadcast(
            f'You are {self.name}',
            f'{self.affect_manager.owner.pretty_name()} is {self.name}',
        )

    # called when effect is over
    def on_finished(self, silent = False):
        if not silent:
            self.affect_manager.owner.simple_broadcast(
                f'You are no longer {self.name}',
                f'{self.affect_manager.owner.pretty_name()} is no longer {self.name}',
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
        return damage_obj

class AffectStunned(Affect):
    # called at start of turn
    def set_turn(self):
        super().set_turn()
        self.owner.simple_broadcast(
            f'You are too stunned to act!',
            f'{self.owner.pretty_name()} is too stunned to act!')
        self.owner.finish_turn()

class AffectEthereal(Affect):
    def __init__(self, _id, affect_manager, name, description, turns, dmg_amp):
        super().__init__(_id, affect_manager, name, description, turns)
        self.dmg_amp = dmg_amp
    
    def take_damage(self, damage_obj: 'Damage'):
        if damage_obj.damage_type == DamageType.PHYSICAL:
            damage_obj.damage_type = DamageType.CANCELLED
            damage_obj.damage_taker.simple_broadcast(
                    f'You take no damage because you are ethereal',
                    f'{damage_obj.damage_taker.pretty_name()} takes no damage because they are ethereal'
                    )

        if damage_obj.damage_type == DamageType.MAGICAL:
            damage_obj.damage_value = int(damage_obj.damage_value * self.dmg_amp)

        return damage_obj
