

from config import AffType, DamageType
#from affects.affects 

class AffectsManager:
    def __init__(self, owner):
        self.owner = owner
        self.affects = {}

    def unload_all_affects(self, silent = False):
        # REMOVE ALL AFFECTS VERY IMPORTANT
        aff_to_delete = []
        for aff in self.affects.values():
            aff_to_delete.append(aff)
        for aff in aff_to_delete:
            aff.on_finished(silent)

    '''
    def load_affect(self, affect_id, turns_override = None):
        if affect_id not in AffDict:
            print('affect does not exist? ',affect_id, AffDict)
            return

        aff_dict = AffDict[affect_id]

        if turns_override == None:
            turns = aff_dict['turns']
        else:
            turns = turns_override

        Aff = globals()[aff_dict['object']]
        aff = Aff(aff_dict['id'], self, aff_dict['name'], aff_dict['description'], turns+1, aff_dict['args'])
        return aff
    '''

    def set_affect_object(self, affect):
        if affect.id in self.affects:
            #print('overriding')
            self.affects[affect.id].on_finished(silent = True)
        self.affects[affect.id] = affect
        affect.on_applied()

    def set_affect(self, affect_id, turns_override = None):
        aff = self.load_affect(affect_id, turns_override)
        self.set_affect_object(aff)


    def pop_affect(self, affect):
        del self.affects[affect.id]

    # called at start of turn
    def set_turn(self):
        # run all affects
        aff_to_set_turn = []
        for aff in self.affects.values():
            aff_to_set_turn.append(aff)
        for aff in aff_to_set_turn:
            aff.set_turn()

        # pop affects that are expired
        affs_to_pop = []
        for aff in self.affects.values():
            aff.finish_turn()
            if aff.turns <= 0:
                affs_to_pop.append(aff)
        for aff in affs_to_pop:
            aff.on_finished(False)

    # called at end of turn
    def finish_turn(self):
        pass

    # called whenever hp updates in any way
    def take_damage(self, source, damage, damage_type):
        for aff in self.affects.values():
            source, damage, damage_type = aff.take_damage(source, damage, damage_type)
        return source, damage, damage_type
        
