import random
from skills.manager import use_skill, get_user_skill_level_as_index
from configuration.config import ActorStatusType
from configuration.config import StatType, SKILLS

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
        
        #s['script_values']['cooldown'][level]
        skills = [  skill_id for skill_id in self.actor.skill_manager.skills
                    if skill_id not in self.actor.cooldown_manager.cooldowns ]

        return skills
                    



    def use_best_skill(self):
        allies, enemies = self.get_targets()
        skills = self.get_skills()

        # try to use a skill 5 times, if it fails return false
        # return true if you managed to use a skill
        for i in range(0,20):
            
            if skills == []:
                break

            skill_to_use = random.choice(skills)

            targets = []
            if SKILLS[skill_to_use]['is_offensive']:
                targets = enemies
            else:
                targets = allies

            if targets == []:
                continue

            target = random.choice(targets)
            
            if use_skill(self.actor, target, skill_to_use):
                self.actor.finish_turn()
                return True

        self.actor.simple_broadcast('You do nothing.',f'{self.actor.pretty_name()} does nothing.')
        self.actor.finish_turn()
        return False

    def tick(self):
        if self.actor.factory.ticks_passed <= 3:
            return False
        
        # if none of these checks exit the loop, then that indicates this enemy is in combat
        if self.actor.room == None:
            return False
            
        if self.actor.status == ActorStatusType.NORMAL:
            #self.wander()
            return False
        
        if self.actor.room.combat == None:
            return False

        if self.actor.room.combat.current_actor != self.actor:
            return False

        if self.actor.room.combat.time_since_turn_finished <= int(30*0.5):
            return False
        
        return True

class PlayerAI(AI):
    def tick(self):
        # early return if not in combat
        #if not super().tick():
        #    return
        if self.actor.room.combat == None:
            return False

        if self.actor.room.combat.current_actor != self.actor:
            return False

        self.use_best_skill()

class EnemyAI(AI):
    def tick(self):
        if not super().tick():
            return
        
        self.use_best_skill()
        