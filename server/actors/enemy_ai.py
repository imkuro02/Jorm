import random
from skills.manager import use_skill
from configuration.config import ActorStatusType
from configuration.config import StatType
class Targets:
    SELF =                  'S'     #
    ENEMY_RANDOM =          'ER'    #
    ENEMY_HIGHEST_HP =      'EHH'   #
    ENEMY_LOWEST_HP =       'ELH'
    ENEMY_HIGHEST_MP    =   'EHM'
    ENEMY_LOWEST_MP     =   'ELM'
    ENEMY_HIGHEST_THREAT =  'EHT'
    ENEMY_LOWEST_THREAT =   'ELT'

    ALLY_RANDOM =           'AR'
    ALLY_HIGHEST_HP =       'AHH'   
    ALLY_LOWEST_HP =        'ALH'
    ALLY_HIGHEST_MP =       'AHM'
    ALLY_LOWEST_MP =        'ALM'
    ALLY_HIGHEST_THREAT =   'AHT'
    ALLY_LOWEST_THREAT =    'ALT'
  
    
   
    
    
    
    

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
    
    def get_target(self, target = Targets.ENEMY_RANDOM):

        if target == Targets.SELF:
            return self.actor
        
        entities = self.actor.room.combat.participants.values()
        enemies = [entity for entity in entities if type(entity).__name__ != type(self.actor).__name__ and entity.status == ActorStatusType.FIGHTING]
        allies =  [entity for entity in entities if type(entity).__name__ == type(self.actor).__name__ and entity.status == ActorStatusType.FIGHTING]

        match target:

            case Targets.ENEMY_RANDOM:
                return random.choice(enemies)
            case Targets.ALLY_RANDOM:
                return random.choice(allies)
            case Targets.ENEMY_HIGHEST_HP:
                return max(enemies, key=lambda char: char.stats[StatType.HP])
            case Targets.ENEMY_HIGHEST_THREAT:
                return max(enemies, key=lambda char: char.stats[StatType.THREAT])
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

