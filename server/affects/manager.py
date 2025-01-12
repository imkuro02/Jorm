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
        # pop affects that are expired
        affs_to_pop = []
        for aff in self.affects.values():
            aff.finish_turn()
            if aff.turns <= 0:
                affs_to_pop.append(aff)
        for aff in affs_to_pop:
            aff.on_finished(False)

        # run all affects
        aff_to_set_turn = []
        for aff in self.affects.values():
            aff_to_set_turn.append(aff)
        for aff in aff_to_set_turn:
            aff.set_turn()

    # called at end of turn
    def finish_turn(self):
        pass

    # called whenever hp updates in any way
    def take_damage(self, damage_obj: 'Damage'):
        for aff in self.affects.values():
            damage_obj = aff.take_damage(damage_obj)
        return damage_obj
    
    def deal_damage(self, damage_obj: 'Damage'):
        for aff in self.affects.values():
            damage_obj = aff.deal_damage(damage_obj)
        return damage_obj
        
        
