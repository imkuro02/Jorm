import random
from skills.manager import use_skill, get_user_skill_level_as_index
from configuration.config import ActorStatusType
from configuration.config import StatType, SKILLS, MsgType


class AI:
    def __init__(self, actor):
        self.actor = actor
        #self.target = None
        self.prediction_target = None
        self.prediction_skill = None
        self.prediction_item = None
        self.prediction_override = ''

    def initiative(self):
        self.predict_use_best_skill()
        #debug = f'{self.actor.name}, {self.prediction_skill}, {self.prediction_target}'
        #self.actor.simple_broadcast(debug,debug)

    def die(self):
        pass

    def has_prediction(self):
        if self.prediction_target == None:
            return False
        if self.prediction_skill == None and self.prediction_item == None:
            return False
        return True
    
    def override_prediction(self, prediction_string = ''):
        self.prediction_override = prediction_string

    def get_prediction_string(self, who_checks):
        if self.prediction_override != '':
            return self.prediction_override
        
        aff_appends = []
        include_prediction = True
        for aff in self.actor.affect_manager.affects.values():
            # affects like stun when at 0 will not do anything but display 
            # the aff is over, so when something is at 0 it wont trigger on actor turn
            # and therefor should not display
            if aff.turns == 0:
                continue
            if aff.get_prediction_string_append != None:
                aff_appends.append(aff.get_prediction_string_append)
            if aff.get_prediction_string_clear == True:
                include_prediction = False

        prediction_string = ''
        if include_prediction:
            if type(self.actor).__name__ == 'Player':
                #if self.actor.status == ActorStatusType.DEAD:
                #    line = random.choice(['is cooked','wont get up anytime soon','rests in peace'])
                #else:
                #    line = random.choice(['is angry','will do something maybe','will win probably','wont lose','is ready to kill'])
                #prediction_string = line
                prediction_string = ''
            else:
                if not self.has_prediction():
                    prediction_string = 'will do nothing'
                else:
                    if self.prediction_target == self.actor:
                        prediction_string = f'will use {SKILLS[self.prediction_skill]["name"]}'
                    elif self.prediction_target == who_checks:
                        prediction_string = f'will use {SKILLS[self.prediction_skill]["name"]} on you'
                    else:
                        prediction_string = f'will use {SKILLS[self.prediction_skill]["name"]} on {self.prediction_target.pretty_name()}'
                
            prediction_string = prediction_string + ' '

        
        return prediction_string + f'{" ".join(aff_appends)}'

    def get_targets(self):
        actors = self.actor.room.combat.participants.values()
        enemies = [ actor for actor in actors 
                    if actor.party_manager.get_party_id() != self.actor.party_manager.get_party_id() 
                    and actor.status == ActorStatusType.FIGHTING    ]

        allies = [  actor for actor in actors 
                    if actor.party_manager.get_party_id() == self.actor.party_manager.get_party_id() 
                    and actor.status == ActorStatusType.FIGHTING    ]
        return allies, enemies

    def get_skills(self, for_prediction = False, combat_only_skills = True):
        
        skills = []
        # if for prediction is true, be able to pick skills that are available NEXT TURN
        for skill_id in self.actor.skill_manager.skills:
            if combat_only_skills and not SKILLS[skill_id]['can_use_in_combat']: 
                continue
            if skill_id in self.actor.cooldown_manager.cooldowns:
                if for_prediction and self.actor.cooldown_manager.cooldowns[skill_id] > 1:
                    #print('WHAT,,',self.actor.cooldown_manager.cooldowns[skill_id])
                    continue
                if not for_prediction:
                    #print('not for prediction!_')
                    continue
            if self.actor.skill_manager.skills[skill_id] <= 0:
                #print('WHAT')
                continue
            skills.append(skill_id)
        return skills

   

    def clear_prediction(self):
        #print(self.actor.name, 'prediction cleared')
        self.prediction_target = None
        self.prediction_skill = None
        self.prediction_item = None

    def use_prediction(self):
        target = self.prediction_target

        #if self.prediction_target == self.actor and self.target != None and self.target in self.actor.room.actors.values():
        #    target = self.target
        #else:
        #    self.target = None

        if self.prediction_item != None:
            if self.prediction_item.use(self.actor, target):
                self.clear_prediction()
                #self.predict_use_best_skill()
                self.actor.finish_turn()
                return True

        if self.prediction_skill != None:
            if use_skill(self.actor, target, self.prediction_skill):
                self.clear_prediction()
                #self.predict_use_best_skill()
                
                self.actor.finish_turn()
                return True
            
        #debug = f'skill {self.prediction_skill}, target {self.prediction_target}'
        #self.actor.simple_broadcast(debug,debug)
        return False
        
        

    def predict_use_best_skill(self, offensive_only = False, for_prediction = True):
        self.prediction_target = None
        self.prediction_skill = None

        #if self.prediction_skill != None:
        #    return

        if self.actor.room == None:
            return False
        
        if self.actor.room.combat == None:
            return False
        
        allies, enemies = self.get_targets()
        skills = self.get_skills(for_prediction = for_prediction, combat_only_skills = True)
        #print(self.actor.name,skills)
        # try to use a skill 5 times, if it fails return false
        # return true if you managed to use a skill
        for i in range(0,20):
            
            if skills == []:
                break

            skill_to_use = random.choice(skills)

            targets = []

            if offensive_only:
                if not SKILLS[skill_to_use]['is_offensive']:
                    continue

            if 'swing' == skill_to_use and i<5:
                continue

            if i>15:
                skill_to_use = 'swing'

            if SKILLS[skill_to_use]['is_offensive']:
                targets = enemies
            else:
                targets = allies

            if targets == []:
                continue

            target = self.actor
            
            if SKILLS[skill_to_use]['target_others_is_valid']:
                target = random.choice(targets)
                for t in targets:
                    if t == self.actor:
                        continue
                    if t.stat_manager.stats[StatType.THREAT] >= target.stat_manager.stats[StatType.THREAT]:
                        target = t
            


            #print(self.actor.name, 'prediction target:', target.name)
            
                
                
            
            #print(target, skill_to_use)
            self.prediction_target = target
            self.prediction_skill = skill_to_use
            #for i in self.actor.room.combat.participants.values():
            #    i.sendLine(f'{self.actor.pretty_name()} {self.get_prediction_string(i)}')
            return True
        return False
    '''
    def use_best_skill(self, offensive_only = False):
        if self.actor.room.combat == None:
            return
        
       
        allies, enemies = self.get_targets()
        skills = self.get_skills()
        self.actor.sendLine('use_best_skill, will use these skills ' + str(skills), msg_type = [MsgType.DEBUG])

        # try to use a skill 5 times, if it fails return false
        # return true if you managed to use a skill
        for i in range(0,20):
            
            if skills == []:
                self.actor.sendLine('no valid skills!!', msg_type = [MsgType.DEBUG])
                break

            skill_to_use = random.choice(skills)

            targets = []

            if 'swing' == skill_to_use and i<15:
                self.actor.sendLine('cant swing', msg_type = [MsgType.DEBUG])
                continue

            if i>=15:
                skill_to_use = 'swing'
                self.actor.sendLine('will swing', msg_type = [MsgType.DEBUG])

            if offensive_only:
                if not SKILLS[skill_to_use]['is_offensive']:
                    continue

            if SKILLS[skill_to_use]['is_offensive']:
                targets = enemies
            else:
                targets = allies

            if targets == []:
                self.actor.sendLine('no targets', msg_type = [MsgType.DEBUG])
                continue

            #target = random.choice(targets)
            target = random.choice(targets)
            for t in targets:
                if t.stat_manager.stats[StatType.THREAT] > target.stat_manager.stats[StatType.THREAT]:
                    target = t
            
            if use_skill(self.actor, target, skill_to_use) == True:
                self.actor.finish_turn()
                return True
            else:
                skills.remove(skill_to_use)
                self.actor.sendLine(f'Skill failed: s:{skill_to_use} t:{target.name} ts:{targets}', msg_type = [MsgType.DEBUG])

            self.actor.sendLine('Didnt exit skill properly', msg_type = [MsgType.DEBUG])
            self.actor.sendLine(f's:{skill_to_use} t:{target.name} ts:{targets}', msg_type = [MsgType.DEBUG])

            #skills.remove(skill_to_use)

        self.actor.simple_broadcast(f'You do nothing',f'{self.actor.pretty_name()} does nothing')
        self.actor.finish_turn()
        return False
    '''

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

        if self.actor.room.combat.time_since_turn_finished <= int(10):
            return False
        
        return True

class PlayerAI(AI):
    def use_prediction(self):
        if super().use_prediction():
            return True
        #self.actor.simple_broadcast('You do nothing!', f'{self.actor.pretty_name()} does nothing!')
        return False
    
    def initiative(self):
        
        return

    def tick(self):
        # early return if not in combat
        if not super().tick():
           return

        if self.actor.settings_manager.autobattler:
            if self.actor.stat_manager.stats[StatType.HP] <= self.actor.stat_manager.stats[StatType.HPMAX]*0.1:
                self.actor.sendLine(f'Turning off Autobattler; Your HP is below 10%!') 
                self.actor.settings_manager.autobattler = False

        if self.actor.settings_manager.autobattler:
            self.predict_use_best_skill(for_prediction = False)
            self.use_prediction()
            self.clear_prediction()
        else:
            if self.has_prediction():
                self.use_prediction()
                self.clear_prediction()
                #print('using prediction')
                #if self.actor.settings_manager.autobattler:
                #    self.predict_use_best_skill(offensive_only = True)
        

class EnemyAI(AI):

    def use_prediction(self):
        if super().use_prediction():
            return True

        self.actor.simple_broadcast('You do nothing!', f'{self.actor.pretty_name()} does nothing!')
        #self.predict_use_best_skill()
        self.actor.finish_turn()
        return False
    
    def tick(self):
        if not super().tick():
            return
        
        self.use_prediction()
        
        
        
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
            self.use_prediction()
            

    def use_prediction(self):
        if super().use_prediction():
            return True
        self.actor.simple_broadcast('You do nothing!', f'{self.actor.pretty_name()} does nothing!')
        #self.predict_use_best_skill()
        self.actor.finish_turn()
        return False

class CowardAI(AI):
    def tick(self):
        if not super().tick():
            return
    
        if len(self.actor.room.exits) >= 1:
            stats = self.actor.stat_manager.stats
            roll = (100 - (stats[StatType.HP] / stats[StatType.HPMAX] * 100)) / 5 
            #print(roll)
            if roll > random.randint(1,100):
                random_dir = random.choice(self.actor.room.exits)
                self.actor.simple_broadcast('',f'{self.actor.pretty_name()} flees {random_dir.direction}!')
                new_room = random_dir.get_room_obj().id

                
                world = self.actor.room.world
                self.actor.status = ActorStatusType.NORMAL
                world.rooms[new_room].move_actor(self.actor, silent = True)
                self.actor.finish_turn()
                return
                
        self.use_prediction()

    def use_prediction(self):
        if super().use_prediction():
            return True
        self.actor.simple_broadcast('You do nothing!', f'{self.actor.pretty_name()} does nothing!')
        #self.predict_use_best_skill()
        self.actor.finish_turn()
        return False

class BossRatAI(AI):
    def __init__(self, actor):
        super().__init__(actor)
        self.turn = 0
    
    def initiative(self):
        self.predict_use_best_skill()
        self.turn += 1
        match self.turn:
            case 3:
                self.override_prediction('is scheming')
            case 6:
                self.override_prediction('licks their snout in anticipation')
            case _:
                self.override_prediction()
                
        
        if self.turn == 7:
            self.turn = 0

    def tick(self):
        if not super().tick():
            return
        
        
        
        if self.turn == 6:

            heal = 0
            to_devour = []
            for par in self.actor.room.combat.participants.values():
                if type(par).__name__ != 'Player':
                    if par.npc_id == 'rat':
                        to_devour.append(par)

            #if to_devour == []:
            #    self.turn = 0
            #    self.use_prediction()
            #    return

            for par in to_devour:
                par.die()
                heal += 10

            self.actor.simple_broadcast('',f'{self.actor.pretty_name()} Devours the rats! healing for {heal}')
            self.actor.heal(value=heal, silent = True)
                
            self.actor.finish_turn()
            return

        if self.turn == 3:
            self.actor.simple_broadcast('',f'{self.actor.pretty_name()} roars loudly!')
            for i in range(0,random.randint(1,3)):
                rat = create_npc(self.actor.room, 'rat')
                rat.room.join_combat(rat)
            self.actor.finish_turn()
            return
            
        self.use_prediction()
        return

    def use_prediction(self):
        if super().use_prediction():
            return True
        self.actor.simple_broadcast('You do nothing!', f'{self.actor.pretty_name()} does nothing!')
        #self.predict_use_best_skill()
        self.actor.finish_turn()
        return False

class VoreAI(AI):
    def __init__(self, actor):
        super().__init__(actor)
        self.rooms = self.actor.room.world.rooms 
        self.vore_room_id = f'{self.actor.room.id}-vored-by-{self.actor.id}'
        self.vore_room = None
        self.original_room = self.actor.room
        self.turn = 0
        #self.vore_room_open()

        self.vore_room_name = 'Vore room name'
        self.vore_room_description = 'Vore room description'
        self.vore_room_spawns = ''


        self.turn_max = 7
        self.turn_vore = 6
        self.turn_vore_text = 'Looks hungry'


    def initiative(self):
        self.predict_use_best_skill()
        self.turn += 1
        match self.turn:
            case self.turn_vore:
                self.override_prediction(self.turn_vore_text)
            case _:
                self.override_prediction()
        if self.turn == self.turn_max:
            self.turn = 0

    def tick(self):
        if not super().tick():
            return
        
        if self.turn == self.turn_vore:
            if self.vore_room == None:
                self.vore_room_open()
            self.vore_room_grab_party()
            self.actor.finish_turn()
            return
            
        self.use_prediction()
        return

    def create_vore_room_from_template(self):
        return Room(self.actor.room.world, self.vore_room_id, 
            name =          self.vore_room_name, # 'Vore room name', 
            description =   self.vore_room_description, # 'Vore room description', 
            from_file =    'vore_room', 
            exits = [], can_be_recall_site = False, doorway = False, instanced = False, no_spawner = True) 

     # create new vore room
    def vore_room_open(self):
        vore_room = self.create_vore_room_from_template()
        self.rooms[self.vore_room_id] = vore_room
        self.vore_room = vore_room
        vore_room_exit = Exit(self.vore_room, 'out', self.original_room.id, blocked = True)
        self.vore_room.exits.append(vore_room_exit)

        for line in self.vore_room_spawns.split('\n'):
            for val in line.split(','):
                to_spawn = create_npc(self.vore_room, val)
                #to_spawn.room.join_combat(val)

    # close vore room, kick all player parties back into the room
    def vore_room_close(self):
        if self.vore_room == None:
            return
        #print(self.vore_room.__dict__)
        self.actor.room.world.rooms_to_unload.append(self.vore_room.id)
        #del self.rooms[self.vore_room_id]
        
    # grab a party and add it to vore room
    def vore_room_grab_party(self):
        print('grabbing party')
        to_move = []
        for i in self.original_room.actors.values():
            if type(i).__name__ != 'Player':
                print('not player', i.name)
                continue
            if i.status != ActorStatusType.FIGHTING:
                print('not fighting', i.name)
                continue
            to_move.append(i)

        for i in to_move:
            i.simple_broadcast( f'{self.actor.pretty_name()} vores you!', 
                                f'{self.actor.pretty_name()} vores {i.pretty_name()}!')
        for i in to_move:
            self.vore_room.move_actor(i, silent = True, dont_unload_instanced = True)
            i.status = ActorStatusType.NORMAL

        #for i in to_move:
        #    i.command_look('')
            

    def vore_room_kick_all_parties(self):
        if self.vore_room == None:
            return

        to_move = []
        for i in self.vore_room.actors.values():
            if type(i).__name__ != 'Player':
                continue
            to_move.append(i)

        for i in to_move:
             i.simple_broadcast( f'{self.actor.pretty_name()} spits you out!', 
                                f'{self.actor.pretty_name()} spits out {i.pretty_name()}!')
        for i in to_move:                     
            self.original_room.move_actor(i, silent = True, dont_unload_instanced = True)
            i.status = ActorStatusType.NORMAL


    def die(self):
        self.vore_room_kick_all_parties()
        self.vore_room_close()

class VoreDragonLesserAI(VoreAI):
    def __init__(self, actor):
        super().__init__(actor)
        self.turn_max = 7
        self.turn_vore = 2

        self.turn_vore_text =           'Looks hungry'
        self.vore_room_name =           'Mouth of the dragon'
        self.vore_room_description =    'The smell of charcoal mixed with burnt flesh overwhelms you\nIt is hot, wet, and dark here.'
        self.vore_room_spawns =         'dragon_tongue_0\ndragon_tooth_0\ndragon_tooth_0\ndragon_tooth_0\ndragon_tooth_0'
                                        

def get_ai(ai_name):
    match ai_name:
        case 'Slime':
            return SlimeAI
        case 'Enemy':
            return EnemyAI
        case 'Coward':
            return CowardAI
        case 'BossRat':
            return BossRatAI
        case 'Vore':
            return VoreAI
        case 'VoreDragonLesser':
            return VoreDragonLesserAI
        case _:
            return EnemyAI