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
    self.protocol.factory.world.rooms[self.recall_site].move_player(self, silent = True)
    self.status = ActorStatusType.NORMAL
    self.simple_broadcast(
        f'You have fled back to {self.room.name}',
        f'{self.pretty_name()} comes running in a panic!'
    )

@check_no_empty_line
@check_not_in_combat
@check_alive
def command_go(self, line):
    if line == '':
        self.sendLine('Go where?')
        return
    world = self.protocol.factory.world
    direction = None

    exits = {**self.room.exits, **self.room.secret_exits}
    for _exit in exits:
        if ' '+line.lower() in ' '+_exit.lower():
            direction = _exit
            break

    if direction == None:
        self.simple_broadcast(
            f'You walk into a wall',
            f'{self.pretty_name()} walks into a wall'
            ) 
        return

    old_room = self.room
    new_room = exits[direction]

    self.simple_broadcast(
        None,
        f'{self.pretty_name()} went {direction}'
        )

    world.rooms[new_room].move_player(self)

    self.simple_broadcast(
        None,
        f'{self.pretty_name()} arrived'
        )
    self.finish_turn(force_cooldown = True)

    if self.party_manager.party != None:
        if self.party_manager.party.owner == self:
            for par in self.party_manager.party.participants.values():
                if par == self:
                    continue
                if par.room != old_room:
                    continue
                par.command_go(line)



