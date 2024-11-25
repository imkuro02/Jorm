
import enum

class AffType(enum.Enum):
    Basic = enum.auto()
    DOT1 = enum.auto()
    DOT2 = enum.auto()
    HealAmp = enum.auto()
    PowerUp = enum.auto()
    Ethereal = enum.auto()

class AffectsManager:
    def __init__(self, owner):
        self.owner = owner
        self.affects = {}

    def load_affect(self, affect_id):
        
    
        if affect_id == 'affect':
            return Affect(AffType.Basic, self, 'AffectName', 2)
        if affect_id == 'dot':
            return AffectDOT(AffType.DOT1, self, 'Poisoned', 10, 1, 'pure')
        if affect_id == 'dot2':
            return AffectDOT(AffType.DOT1, self, 'Bleeding', 10, 1, 'pure')
        if affect_id == 'healamp':
            return AffectHealAmp(AffType.HealAmp, self, 'Blessed', 10)
        if affect_id == 'powerup':
            return AffectStatBonus(AffType.PowerUp, self, 'Fortified', 10, {'str':1,'hp':100,'hp_max':100})
        if affect_id == 'ethereal':
            return AffectEthereal(AffType.Ethereal, self, 'Ethereal', 10)
        

    def set_affect(self, affect):
        if affect.aff_type in self.affects:
            #print('overriding')
            self.affects[affect.aff_type].on_finished(silent = True)
        self.affects[affect.aff_type] = affect
        affect.on_applied()

    def pop_affect(self, affect):
        del self.affects[affect.aff_type]

    # called at start of turn
    def set_turn(self):
        for aff in self.affects.values():
            aff.set_turn()

    # called at end of turn
    def finish_turn(self):
        affs_to_pop = []
        for aff in self.affects.values():
            aff.finish_turn()
            if aff.turns <= 0:
                affs_to_pop.append(aff)
        for aff in affs_to_pop:
            self.pop_affect(aff)

        

    # called whenever hp updates in any way
    def take_damage(self, source, damage, damage_type):
        for aff in self.affects.values():
            damage, damage_type = aff.take_damage(source, damage, damage_type)
        return damage, damage_type
        
class Affect:
    def __init__(self, aff_type, affect_manager, name, turns):
        self.aff_type = aff_type
        self.affect_manager = affect_manager

        self.name = name
        self.turns = turns

    def info(self):
        return f'{self.name:<15} {self.turns:<3} \n'

    # called when applied 
    def on_applied(self):
        self.affect_manager.owner.simple_broadcast(
            f'You are {self.name}',
            f'{self.affect_manager.owner.name} is {self.name}',
        )


    # called when effect is over
    def on_finished(self, silent = False):
        if not silent:
            self.affect_manager.owner.simple_broadcast(
                f'You are no longer {self.name}',
                f'{self.affect_manager.owner.name} is no longer {self.name}\n',
            )
        self.affect_manager.pop_affect(self)

    # called at start of turn
    def set_turn(self):
        pass

    # called at end of turn
    def finish_turn(self):
        self.turns -= 1
        #if self.turns <= 0:
        #    self.on_finished()

    # called whenever hp updates in any way
    def take_damage(self, source, damage, damage_type):
        return damage, damage_type
        
class AffectEthereal(Affect):
    def __init__(self, aff_type, affect_manager, name, turns):
        super().__init__(aff_type, affect_manager, name, turns)

    def info(self):
        return super().info().replace('\n', f'You take no physical damage, but take 140% magical damage\n')

    def take_damage(self, source, damage, damage_type):
        if damage_type == 'physical': 
            self.affect_manager.owner.simple_broadcast(
                f'You are Ethereal',
                f'{self.affect_manager.owner.pretty_name()} is Ethereal'
            )
            return 0, 'none'

        if damage_type == 'magical':
            damage = int(damage * 1.4)

        return super().take_damage(source, damage, damage_type)

class AffectDOT(Affect):
    def __init__(self, aff_type, affect_manager, name, turns, damage_per_turn, damage_type):
        super().__init__(aff_type, affect_manager, name, turns)

        self.damage_per_turn = damage_per_turn
        self.damage_type = damage_type
    
    def info(self):
        return super().info().replace('\n',f'You take {self.damage_per_turn} of {self.damage_type} damage \n')

    # called when applied 
    def on_applied(self):
        super().on_applied()

    # called when effect is over
    def on_finished(self, silent = False):
        super().on_finished(silent)

    # called at start of turn
    def set_turn(self):
        super().set_turn()

    # called at end of turn
    def finish_turn(self):
        super().finish_turn()
        self.affect_manager.owner.take_damage(None, self.damage_per_turn, self.damage_type)

    # called whenever hp updates in any way
    def take_damage(self, source, damage, damage_type):
        return super().take_damage(source, damage, damage_type)
        
        
class AffectHealAmp(Affect):
    def __init__(self, aff_type, affect_manager, name, turns, heal_amp = 1.2):
        super().__init__(aff_type, affect_manager, name, turns)
        self.heal_amp = heal_amp


    def info(self):
        return super().info().replace('\n',f'Your healing is amplified by {int(self.heal_amp*100)}%\n')

    # called when applied 
    def on_applied(self):
        super().on_applied()

    # called when effect is over
    def on_finished(self, silent = False):
        super().on_finished(silent)

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
            damage = int(damage*self.heal_amp)
        return damage, damage_type

class AffectStatBonus(Affect):
    def __init__(self, aff_type, affect_manager, name, turns, stats):
        super().__init__(aff_type, affect_manager, name, turns)
        self.stats = stats

    def info(self):
        return super().info().replace('\n','STATS\n')

    def on_applied(self):
        super().on_applied()
        for stat in self.stats:
            self.affect_manager.owner.stats[stat] += self.stats[stat]
    
    def on_finished(self, silent = False):
        for stat in self.stats:
            self.affect_manager.owner.stats[stat] -= self.stats[stat]
        super().on_finished(silent)