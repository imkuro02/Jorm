
class AffectsManager:
    def __init__(self, actor):
        self.actor = actor
        self.affects = {}

    def get_all_afflictions(self):
        affs = {}
        for i in self.affects.values():
            affs[i.name] = i
        #print(i)
        return affs

    def unload_all_affects(self, silent = False, forced = True):
        # REMOVE ALL AFFECTS VERY IMPORTANT
        aff_to_delete = []
        for aff in self.get_all_afflictions().values():
            if forced == True:
                #self.actor.sendLine(f'forced unload of affects true: {aff.name}')
                aff_to_delete.append(aff)
                continue
            
            if not aff.custom_go_away:
                #self.actor.sendLine(f'not custom go away of affects true: {aff.name}')
                aff_to_delete.append(aff)
                continue
                
        for aff in aff_to_delete:
            aff.on_finished(silent)

    def set_affect_object(self, affect):

        # send a request to merge, if it fails that means 
        # the new affect will override current
        # merging logic of turns and whatnot happens in merge_request
        merged = False
        affs = self.affects
        if affect.name in affs:
            merged = self.affects[affect.name].merge_request(affect)
            if not merged:
                self.affects[affect.name].on_finished()

        if not merged:
            self.affects[affect.name] = affect
            affect.on_applied()

    #def set_affect(self, affect_id, turns_override = None):
    #    aff = self.load_affect(affect_id, turns_override)
    #    self.set_affect_object(aff)

    def pop_affect(self, affect):
        if affect.name not in self.affects:
            return
        del self.affects[affect.name]

    # called at start of turn
    def set_turn(self):
        # pop affects that are expired
        affs_to_pop = []
        for aff in self.get_all_afflictions().values():
            aff.finish_turn()
            if aff.turns <= 0:
                affs_to_pop.append(aff)
        for aff in affs_to_pop:
            aff.on_finished(False)

        # run all affects
        aff_to_set_turn = []
        for aff in self.get_all_afflictions().values():
            aff_to_set_turn.append(aff)
        for aff in aff_to_set_turn:
            aff.set_turn()

    # called at end of turn
    def finish_turn(self):
        pass

    # called whenever hp updates in any way
    def take_damage_before_calc(self, damage_obj: 'Damage'):
        for aff in self.get_all_afflictions().values():
            damage_obj = aff.take_damage_before_calc(damage_obj)
        return damage_obj

    def take_damage_after_calc(self, damage_obj: 'Damage'):
        for aff in self.get_all_afflictions().values():
            damage_obj = aff.take_damage_after_calc(damage_obj)
        return damage_obj
    
    def deal_damage(self, damage_obj: 'Damage'):
        for aff in self.get_all_afflictions().values():
            damage_obj = aff.deal_damage(damage_obj)
        return damage_obj
    
    def dealt_damage(self, damage_obj: 'Damage'):
        for aff in self.get_all_afflictions().values():
            damage_obj = aff.dealt_damage(damage_obj)
        return damage_obj
        
        
