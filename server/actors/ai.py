class AI:
    def __init__(self, actor):
        self.actor = actor

    def get_targets(self):
        actors = self.actor.room.combat.participants.values()
        enemies = [ actor for actor in actors 
                    if actor.party_manager.get_party_id() != self.actor.party_manager.get_party_id() 
                    and actor.status == ActorStatusType.FIGHTING    ]

        allies = [  actor for actor in actors 
                    if actor.party_manager.get_party_id() == self.actor.party_manager.get_party_id() 
                    and actor.status == ActorStatusType.FIGHTING    ]
        return allies, enemies

    def get_skills(self):


    def tick(self):
        # early return if not in combat
    

        match self.actor.status 
            case ActorStatusType.FIGHTING:
                allies, enemies = self.get_targets()
                action = self.get_skills()
        
                if action == None:
                    self.actor.finish_turn()
                    return
                
                use_skill(self.actor, action[1], action[0])
                self.actor.finish_turn()

            case ActorStatusType.NORMAL:
                pass
        

        
        