import random
from skills.manager import use_skill

class Targets:
    SELF =          's'
    RANDOM_ENEMY =  're'
    RANDOM_ALLY =   'ra'
    LOWEST_ENEMY =  'le'
    LOWEST_ALLY =   'la'
    HIGHEST_ENEMY = 'he'
    HIGHEST_ALLY =  'ha'

class AI:
    def __init__(self, actor):
        self.actor = actor

    def tick(self):
        # if none of these checks exit the loop, then that indicates this enemy is in combat
        if self.actor.room == None:
            return False
            
        if self.actor.room.combat == None:
            return False

        if self.actor.room.combat.current_actor != self.actor:
            return False

        if self.actor.room.combat.time_since_turn_finished <= 30*1:
            return False
        return True
    
    def get_target(self, target = Targets.RANDOM_ENEMY):
        
        if target == Targets.SELF:
            return self.actor
        
        entities = self.actor.room.combat.participants.values()
        enemies = [entity for entity in entities if type(entity).__name__ != type(self.actor).__name__]
        allies =  [entity for entity in entities if type(entity).__name__ == type(self.actor).__name__]

        match target:

            case Targets.RANDOM_ENEMY:
                return random.choice(enemies)
            case Targets.RANDOM_ALLY:
                return random.choice(allies)

            #case Targets.LOWEST_ENEMY:

            #case Targets.LOWEST_ALLY:

            #case Targets.HIGHEST_ENEMY:

            #case Targets.HIGHEST_ALLY:

        return False

        

class AIBasic(AI):
    def tick(self):
        # early return if not in combat
        if not super().tick():
            return

        
        #random_target = random.choice([entity for entity in self.actor.room.combat.participants.values() if type(entity).__name__ != type(self.actor).__name__])
        skill_to_use = self.actor.combat_loop[0]

        target = self.get_target(skill_to_use['target'])
        if target == False:
            return

        use_skill(self.actor, target, skill_to_use['skill'])

        self.actor.combat_loop.append(skill_to_use)
        self.actor.combat_loop.pop(0)

        self.actor.finish_turn()

