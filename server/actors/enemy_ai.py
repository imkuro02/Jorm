import random
from skills.manager import use_skill
from configuration.config import ActorStatusType
from configuration.config import StatType, SKILLS

import random

class Targets:
    SELF =                  'S'     #
    ENEMY_RANDOM =          'ER'    #
    ENEMY_HIGHEST_HP =      'EHH'   #
    ENEMY_LOWEST_HP =       'ELH'
    ENEMY_HIGHEST_MP    =   'EHM'
    ENEMY_LOWEST_MP     =   'ELM'
    ENEMY_HIGHEST_THREAT =  'EHT'   #
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
        self.wandered = 0

    def wander(self):
        room = self.actor.room
        l = [*room.exits.values()]

        x = 1
        if self.actor.factory.ticks_passed % (30 * 1) == 0:
            x = random.randrange(0,500)

        if x >= 1:
            return
        if len(l) == 0:
            return

        ex_id = random.randrange(0,len(l))
        ex_id = l[ex_id]
        
        new_room = self.actor.factory.world.rooms[ex_id]

        # not allowed to come into recall sites
        if new_room.can_be_recall_site:
            return
        
        # not allowed to come into instanced rooms
        if new_room.instanced:
            return
        
        new_room.move_entity(self.actor)

        #print(self.actor.id,'i wandered!',self.actor.name)

    def tick(self):
        if self.actor.factory.ticks_passed <= 3:
            return False
        
        # if none of these checks exit the loop, then that indicates this enemy is in combat
        if self.actor.room == None:
            return False
            
        if self.actor.status == ActorStatusType.NORMAL:
            self.wander()
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
        enemies = [entity for entity in entities if entity.party_manager.get_party_id() != self.actor.party_manager.get_party_id() and entity.status == ActorStatusType.FIGHTING]
        allies =  [entity for entity in entities if entity.party_manager.get_party_id() == self.actor.party_manager.get_party_id()  and entity.status == ActorStatusType.FIGHTING]

        match target:

            case Targets.ENEMY_RANDOM:
                return random.choice(enemies)
            case Targets.ALLY_RANDOM:
                return random.choice(allies)
            case Targets.ENEMY_HIGHEST_HP:
                return max(enemies, key=lambda char: char.stat_manager.stats[StatType.HP])
            case Targets.ENEMY_HIGHEST_THREAT:
                return max(enemies, key=lambda char: char.stat_manager.stats[StatType.THREAT])
            #case Targets.LOWEST_ENEMY:

            #case Targets.LOWEST_ALLY:

            #case Targets.HIGHEST_ENEMY:

            #case Targets.HIGHEST_ALLY:

        return False
    
    def get_best_skill(self):
        ally = self.get_target(Targets.ALLY_RANDOM)
        enemy = self.get_target(Targets.ENEMY_HIGHEST_THREAT)

        best_skill = None
        best_score = -1000000

        for skill in self.actor.skills:
            s = SKILLS[skill]

            # skip if on cooldown
            if skill in self.actor.cooldown_manager.cooldowns:
                continue

            # dont try to use a skill on an ally if you cant use it on them
            if ally != self and not s['target_others_is_valid']:
                continue
            
            ally_stats =    ally.stat_manager.stats
            enemy_stats =   enemy.stat_manager.stats
            
            score = 0

            score_low_hp_ally   = s['weight_low_hp_ally']   * (((ally_stats[StatType.HPMAX] - ally_stats[StatType.HP])/ally_stats[StatType.HPMAX])* 100)
            score_high_hp_ally  = s['weight_high_hp_ally']  * ((ally_stats[StatType.HP] / ally_stats[StatType.HPMAX]) * 100)                                 
            score_low_hp_enemy  = s['weight_low_hp_enemy']  * (((enemy_stats[StatType.HPMAX] - enemy_stats[StatType.HP])/enemy_stats[StatType.HPMAX])* 100)
            score_high_hp_enemy = s['weight_high_hp_enemy'] * ((enemy_stats[StatType.HP] / enemy_stats[StatType.HPMAX]) * 100)                          

            print([score_low_hp_ally , score_high_hp_ally , score_low_hp_enemy , score_high_hp_enemy])
            score = score_low_hp_ally + score_high_hp_ally + score_low_hp_enemy + score_high_hp_enemy
            print(skill, score)
            if score > best_score:
                best_score = score
                best_skill = skill
                

        if best_skill == None:
            return None
        
        if SKILLS[best_skill]['is_offensive']:
            target = enemy
        else:
            target = ally

        return (best_skill, target)





        

class AIBasic(AI):
    def tick(self):
        # early return if not in combat
        if not super().tick():
            return
        

        action = self.get_best_skill()
        
        if action == None:
            return
        
        use_skill(self.actor, action[1], action[0])

        self.actor.finish_turn()

        '''
        self_missing_hp = (self.actor.stat_manager.stats[StatType.HP]/self.actor.stat_manager.stats[StatType.HPMAX])
        self_missing_hp = abs(1-self_missing_hp)
        print(self_missing_hp)
        skills_to_pick_from = {}
        for skill in self.actor.skills:
            s = {
                'id':skill, 
                'is_healing': SKILLS[skill]['is_healing'],
                'is_damage': SKILLS[skill]['is_damage'],
                'is_buff': SKILLS[skill]['is_buff']
                }
            skills_to_pick_from[s['id']] = s

        for s in skills_to_pick_from.values():
            print(s)
        
        #random_target = random.choice([entity for entity in self.actor.room.combat.participants.values() if type(entity).__name__ != type(self.actor).__name__])
        skill_to_use = self.actor.combat_loop[0]

        target = self.get_target(skill_to_use['target'])
        if target == False:
            return

        use_skill(self.actor, target, skill_to_use['skill'])

        self.actor.combat_loop.append(skill_to_use)
        self.actor.combat_loop.pop(0)

        
        '''

