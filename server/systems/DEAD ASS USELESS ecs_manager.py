from configuration.constants.tickrate import TICKRATE
from systems.utils import REFTRACKER, TOUNLOAD, get_object_parent
import random

class ECSManager:
    def __init__(self, factory):
        self.factory = factory
        self.ambience = []#{'object': None, 'message': 'this is template text'}

    def add_ambience(self, obj, message):
        self.ambience.append({'obj': obj, 'message': message})

    def tick_ambience(self):
        to_del = []
        if self.factory.ticks_passed % TICKRATE * 30 == 0:
            for i in self.ambience:
                roll = random.randint(0,100)
                if roll >= 1:
                    continue
                try:
                    obj = i['obj']
                    msg = i['message']

                    # code here
                    owner = obj.inventory_manager.owner
                    if get_object_parent(owner) == "Room":
                        owner = owner
                    else:
                        owner = owner.room

                    if len(owner.actors) >= 1:
                        
                        ac = random.choice(list(owner.actors.values()))
                        ac.simple_broadcast(
                            msg, msg
                        )
                except Exception as e:
                    to_del.append(i)
                    print(e)
                    continue

            for i in to_del:
                self.ambience.remove(i)


    def tick(self):
        self.tick_ambience()
