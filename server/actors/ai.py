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

            #target = random.choice(targets)
            target = random.choice(targets)
            for t in targets:
                if t.stat_manager.stats[StatType.THREAT] > target.stat_manager.stats[StatType.THREAT]:
                    target = t
            
            if use_skill(self.actor, target, skill_to_use):
                self.actor.finish_turn()
                return True
            skills.remove(skill_to_use)
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
        
class SlimeAI(AI):
    def tick(self):
        if not super().tick():
            return
        
        stats = self.actor.stat_manager.stats
        if stats[StatType.HP] < stats[StatType.HPMAX]*.75 and stats[StatType.HPMAX] > 10 :
            stats[StatType.HP] = int(stats[StatType.HP]*.5)
            stats[StatType.HPMAX] = stats[StatType.HP]

            # create npc is assigned in actors.npcs script
            clone = create_npc(self.actor.room, self.actor.npc_id)
            clone.stat_manager.stats[StatType.HPMAX] = stats[StatType.HP]
            clone.stat_manager.stats[StatType.HP] = stats[StatType.HP]
            clone.simple_broadcast('',f'{self.actor.pretty_name()} splits!')
            clone.room.join_combat(clone)
            self.actor.finish_turn()
        else:
            self.use_best_skill()

class CowardAI(AI):
    def tick(self):
        if not super().tick():
            return
    
        if len(self.actor.room.exits) >= 1:
            stats = self.actor.stat_manager.stats
            roll = (100 - (stats[StatType.HP] / stats[StatType.HPMAX] * 100)) / 5 
            print(roll)
            if roll > random.randint(1,100):
                random_dir = random.choice(self.actor.room.exits)
                self.actor.simple_broadcast('',f'{self.actor.pretty_name()} flees {random_dir.direction}!')
                new_room = random_dir.get_room_obj().id

                
                world = self.actor.room.world
                world.rooms[new_room].move_actor(self.actor, silent = True)
                self.actor.finish_turn()
                return
            self.use_best_skill()
    
def get_ai(ai_name):
    match ai_name:
        case 'Slime':
            return SlimeAI
        case 'Enemy':
            return EnemyAI
        case 'Coward':
            return CowardAI
        case _:
            return EnemyAI