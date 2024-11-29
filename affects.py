

from config import AffDict, AffType, DamageType



class AffectsManager:
    def __init__(self, owner):
        self.owner = owner
        self.affects = {}

    def load_affect(self, affect_id):
        aff_dict = AffDict[affect_id]
        Aff = globals()[aff_dict['object']]
        aff = Aff(aff_dict['id'], self, aff_dict['name'], aff_dict['description'], aff_dict['turns']+1, aff_dict['args'])
        return aff

    def set_affect(self, affect):
        if affect.id in self.affects:
            #print('overriding')
            self.affects[affect.id].on_finished(silent = True)
        self.affects[affect.id] = affect
        affect.on_applied()

    def pop_affect(self, affect):
        del self.affects[affect.id]

    # called at start of turn
    def set_turn(self):
        aff_to_set_turn = []
        for aff in self.affects.values():
            aff_to_set_turn.append(aff)
        for aff in aff_to_set_turn:
            aff.set_turn()

    # called at end of turn
    def finish_turn(self):
        affs_to_pop = []
        for aff in self.affects.values():
            aff.finish_turn()
            if aff.turns <= 0:
                affs_to_pop.append(aff)
        for aff in affs_to_pop:
            aff.on_finished(False)

    # called whenever hp updates in any way
    def take_damage(self, source, damage, damage_type):
        for aff in self.affects.values():
            source, damage, damage_type = aff.take_damage(source, damage, damage_type)
        return source, damage, damage_type
        
class Affect:
    def __init__(self, _id, affect_manager, name, description, turns, args):
        self.id = _id
        self.affect_manager = affect_manager
        self.owner = self.affect_manager.owner
        self.name = name
        self.description = description
        self.turns = turns

    def info(self):
        return f'{self.name:<15} {self.turns:<3} {self.description}\n'

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
                f'{self.affect_manager.owner.pretty_name()} is no longer {self.name}\n',
            )
        self.affect_manager.pop_affect(self)

    # called at start of turn
    def set_turn(self):
        pass

    # called at end of turn
    def finish_turn(self):
        self.turns -= 1

    # called whenever hp updates in any way
    def take_damage(self, source, damage, damage_type):
        return source, damage, damage_type

class AffectEthereal(Affect):
    def __init__(self, _id, affect_manager, name, description, turns, args):
        super().__init__(_id, affect_manager, name, description, turns, args)
        self.dmg_amp = args[0]
        print(args)
    
    def take_damage(self, source, damage, damage_type):

        if damage_type == DamageType.PHYSICAL:
            damage_type = DamageType.CANCELLED
            self.owner.sendLine(
                'The attack goes straight thru you as you are ethereal!',
                f'The attack goes straight thru {self.owner.pretty_name()} as they are ethereal!')

        if damage_type == DamageType.MAGICAL:
            damage = int(damage * self.dmg_amp)

        return source, damage, damage_type