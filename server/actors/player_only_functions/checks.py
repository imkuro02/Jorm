
from configuration.config import ActorStatusType

def check_is_admin(func):
    def wrapper(self, line):
        #with open('admins.txt', 'r') as file:
        #    lines = file.readlines()  # Read all lines into a list
        # Check if the target string is in any of the lines
        #found = any(self.protocol.id in admin for admin in lines)
        #if not found:
        #    self.sendLine('You are not an admin')
        #    return
        if self.admin == 0:
            self.sendLine('You are not an admin')
            return
        return func(self, line)
    return wrapper
            
def check_not_trading(func):
    def wrapper(self, line):
        if self.trade_manager.trade != None:
            self.sendLine(f'You can\'t do this while trading')
            return
        else:
            return func(self, line)
    return wrapper

def check_no_empty_line(func):
    def wrapper(self, line):
        if line == '':
            self.sendLine(f'Command "{self.last_command_used}" needs arguments, try "help {self.last_command_used}".')
            return
        else:
            return func(self, line)
    return wrapper

def check_your_turn(func):
    def wrapper(self, line):
        if self.status != ActorStatusType.FIGHTING:
            return func(self, line)
        if self.room.combat != None:
            if self.room.combat.current_actor != self:
                self.sendLine('Not your turn to act.')
                return
        return func(self, line)
    return wrapper

def check_alive(func):
    def wrapper(self, line):
        if self.status == ActorStatusType.DEAD:
            self.sendLine(f'@redYou are dead, use "rest" command to respawn.@normal')
            return 
        return func(self, line)
    return wrapper

def check_not_in_combat(func):
    def wrapper(self, line):
        if self.status == ActorStatusType.FIGHTING:
            self.sendLine(f'You can\'t use command "{self.last_command_used}" in combat, try "help {self.last_command_used}".')
            return
        return func(self, line)
    return wrapper

def check_no_combat_in_room(func):
    def wrapper(self, line):
        if self.room.combat != None:
            self.sendLine('You can\'t do that while there is a fight going on!')
            return
        return func(self, line)
    return wrapper

def check_not_in_party_or_is_party_leader(func):
    def wrapper(self, line):
        if self.party_manager.party != None:
            if self.party_manager.party.actor != self:
                self.sendLine('Only party leader can do this')
                return
        return func(self, line)
    return wrapper

def check_not_in_party(func):
    def wrapper(self, line):
        if self.party_manager.party != None:
            self.sendLine('You can\'t do this while in a party')
            return
        return func(self, line)
    return wrapper