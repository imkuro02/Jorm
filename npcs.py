from actor import Actor
import random
import yaml
import copy
import items
import copy
import skills

with open('config/enemies.yaml', 'r') as file:
    ENEMIES = {}
    ALL_ENEMIES = yaml.safe_load(file)
    for i in ALL_ENEMIES:
        if 'template' not in i:
            ENEMIES[i] = ALL_ENEMIES[i]

    #print(ENEMIES)

def create_enemy(room, enemy_id):
    if enemy_id not in ENEMIES:
        print(f'error creating enemy: {enemy_id}')
        return

    names = 'Redpot Kuro Christine Adne Ken Thomas Sandra Erling Viktor Wiktor Sam Dan Arr\'zTh-The\'RchEndrough'
    name = random.choice(names.split())
    name = name + ' The ' + ENEMIES[enemy_id]['name']
    stats = ENEMIES[enemy_id]['stats']
    skills = ENEMIES[enemy_id]['skills']
    combat_loop = ENEMIES[enemy_id]['combat_loop']
    loot = ENEMIES[enemy_id]['loot']
    Enemy(name, room, stats, skills, combat_loop, loot)


class Enemy(Actor):
    def __init__(self, name, room, stats, skills, combat_loop, loot):
        super().__init__(name, room)
        self.stats = copy.deepcopy(stats)
        self.stats['hp_max'] = self.stats['hp']
        self.stats['mp_max'] = self.stats['mp']
        self.skills = copy.deepcopy(skills)
        self.combat_loop = copy.deepcopy(combat_loop)
        self.loot = copy.deepcopy(loot)
        self.room.move_enemy(self)
        #self.inventory = {}    

    def tick(self):
        if self.room == None:
            return
            
        if self.room.combat == None:
            return

        if self.room.combat.current_actor != self:
            return

        if self.room.combat.time_since_turn_finished <= 30*1:
            return

        random_target = random.choice([entity for entity in self.room.combat.participants.values() if type(entity).__name__ != type(self).__name__])
        skill_to_use = self.combat_loop[0]
        skills.use_skill(self, random_target, self.combat_loop[0]['skill'])

        self.combat_loop.append(self.combat_loop[0])
        self.combat_loop.pop(0)

        #for player in self.room.entities.values():
        #    if type(player).__name__ ==  "Player":
        #        player.sendLine(f'{self.pretty_name()} just groans and stands there...')

        self.finish_turn()

    def drop_loot(self,entity):
        with open("config/items.yaml", "r") as file:
            data = yaml.safe_load(file)
        
        for item in self.loot: 
            roll = random.random()
            if roll >= self.loot[item]:
                continue

            new_item = items.load_item(data[item])

            if new_item.item_type == 'equipment':
                for i in range(random.randint(0,new_item.requirements['level'])):
                    stat = random.choice([s for s in new_item.stats.keys()])
                    new_item.stats[stat] = new_item.stats[stat] + 1
                    #print(stat)
                    
            
            entity.inventory_add_item(new_item)   
        

    def die(self):
        if self.room.combat == None:
            print('no combat')
            return
        if self not in self.room.combat.participants.values():
            print('not in combat')
            return
        for entity in self.room.combat.participants.values():
            if type(entity).__name__ == "Player":
                entity.stats['exp'] += self.stats['exp']
                self.drop_loot(entity)
        super().die()


    def set_turn(self):
        pass