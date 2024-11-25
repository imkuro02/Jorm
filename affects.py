

class AffectsManager:
    def __init__(self, owner):
        self.owner = owner
        self.affects = []

    def load_affect(self, affect_id):
        if affect_id == 'affect':
            return Affect(self, 'Poison', 2)
        if affect_id == 'DOT':
            return AffectDOT(self, 'DOT', 10)
        if affect_id == 'HealAmp':
            return AffectHealAmp(self, 'Heal Amp', 10)

    def set_affect(self, affect):
        self.affects.append(affect)

    def pop_affect(self, affect):
        self.affects.remove(affect)

    # called at start of turn
    def set_turn(self):
        for aff in self.affects:
            aff.set_turn()

    # called at end of turn
    def finish_turn(self):
        for aff in self.affects:
            aff.finish_turn()

    # called whenever hp updates in any way
    def take_damage(self, source, damage, damage_type):
        for aff in self.affects:
            damage, damage_type = aff.take_damage(source, damage, damage_type)
        return damage, damage_type
        
class Affect:
    def __init__(self, affect_manager, name, turns):
        self.affect_manager = affect_manager

        self.name = name
        self.turns = turns

        self.on_applied()

    # called when applied 
    def on_applied(self):
        self.affect_manager.owner.simple_broadcast(
            f'You are affected by {self.name}',
            f'{self.affect_manager.owner.name} is affected by {self.name}',
        )


    # called when effect is over
    def on_finished(self):
        self.affect_manager.owner.simple_broadcast(
            f'You are no longer affected by {self.name}',
            f'{self.affect_manager.owner.name} is no longer affected by {self.name}',
        )
        self.affect_manager.pop_affect(self)

    # called at start of turn
    def set_turn(self):
        pass

    # called at end of turn
    def finish_turn(self):
        self.turns -= 1
        if self.turns <= 0:
            self.on_finished()

    # called whenever hp updates in any way
    def take_damage(self, source, damage, damage_type):
        return damage, damage_type
        
class AffectDOT(Affect):
    def __init__(self, affect_manager, name, turns):
        self.affect_manager = affect_manager

        self.name = name
        self.turns = turns

        self.on_applied()

    # called when applied 
    def on_applied(self):
        super().on_applied()

    # called when effect is over
    def on_finished(self):
        super().on_finished()

    # called at start of turn
    def set_turn(self):
        super().set_turn()

    # called at end of turn
    def finish_turn(self):
        super().finish_turn()
        self.affect_manager.owner.take_damage(None, 1, 'pure')

    # called whenever hp updates in any way
    def take_damage(self, source, damage, damage_type):
        return super().take_damage(source, damage, damage_type)
        
        
class AffectHealAmp(Affect):
    def __init__(self, affect_manager, name, turns):
        self.affect_manager = affect_manager

        self.name = name
        self.turns = turns

        self.on_applied()

    # called when applied 
    def on_applied(self):
        super().on_applied()

    # called when effect is over
    def on_finished(self):
        super().on_finished()

    # called at start of turn
    def set_turn(self):
        super().set_turn()

    # called at end of turn
    def finish_turn(self):
        super().finish_turn()
        #self.affect_manager.owner.take_damage(None, 1, 'pure')

    # called whenever hp updates in any way
    def take_damage(self, source, damage, damage_type):
        super().take_damage(source, damage, damage_type)
        if damage_type == 'heal':
            damage = int(damage*1.5)
        return damage, damage_type