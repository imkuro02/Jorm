from actors.player_only_functions.checks import check_your_turn, check_alive, check_no_empty_line, check_not_in_combat
from configuration.config import ActorStatusType

@check_your_turn
def command_flee(self, line):
    if self.room.combat == None:
        self.sendLine('You are not in combat, you don\'t need to flee')
        return
    self.simple_broadcast(
        None,
        f'{self.pretty_name()} flees!'
    )
    self.protocol.factory.world.rooms[self.recall_site].move_actor(self, silent = True)
    self.status = ActorStatusType.NORMAL
    self.simple_broadcast(
        f'You have fled back to {self.room.name}',
        f'{self.pretty_name()} comes running in a panic!'
    )

@check_no_empty_line
@check_not_in_combat
@check_alive
def command_go(self, line):

    if self.room.is_an_instance():
        can_move = True
        for e in self.room.actors.values():
            if type(e).__name__ == 'Enemy':
                can_move = False
                break

        if not can_move:
            self.sendLine('Its not safe to go further.')
            return
        
    if line == '':
        self.sendLine('Go where?')
        return
    world = self.protocol.factory.world
    direction = None

    exits = self.room.exits
    for _exit in exits:
        if ' '+line.lower() in ' '+_exit.direction.lower(): 
            room_obj = _exit.get_room_obj()
            if room_obj != None:
                direction = _exit
    '''
    exits = {**self.room.exits, **self.room.secret_exits}
    for _exit in exits:
        if ' '+line.lower() in ' '+_exit.lower():
            direction = _exit
            break


    if direction in self.room.blocked_exits:
        e = self.room.is_enemy_present() # this returns the enemy or False if none
        if e != False: 
            self.sendLine(f'{e.pretty_name()} is blocking the path.')
            return

    '''
    if direction == None:
        self.simple_broadcast(
            f'You walk into a wall',
            f'{self.pretty_name()} walks into a wall'
            ) 
        return
        
    if direction.blocked and self.room.is_enemy_present():
        self.sendLine(f'{self.room.is_enemy_present().pretty_name()} is blocking the path.')
        return

    
    

    old_room = self.room
    new_room = direction.get_room_obj().id

    

    world.rooms[new_room].move_actor(self)
    self.command_look('')

    if self.recall_site == 'tutorial' and self.room.can_be_recall_site:
        self.command_rest('set')
   
    self.finish_turn(force_cooldown = True)

    if self.party_manager.party != None:
        if self.party_manager.party.actor == self:
            for par in self.party_manager.party.participants.values():
                if par == self:
                    continue
                if par.room != old_room:
                    continue
                #par.command_go(line)
                self.room.move_actor(par, silent = True)
                par.sendLine('You follow.')
                par.command_look('')



