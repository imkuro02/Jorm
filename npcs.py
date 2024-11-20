from actor import Actor
from player import Player

class Enemy(Actor):
    def __init__(self, name, room):
        super().__init__(name, room)
        self.room.move_enemy(self)
        self.inventory = {}    

    def tick(self):
        if self.room == None:
            return
            
        if self.room.combat == None:
            return

        if self.room.combat.current_actor != self:
            return

        if self.room.combat.time_since_turn_finished <= 30*1:
            return

        #print('MY TURN')
        for player in self.room.entities.values():
            if isinstance(player, Player):
                player.protocol.sendLine(f'{self.pretty_name()} just groans and stands there...')

        self.finish_turn()

    def set_turn(self):
        pass