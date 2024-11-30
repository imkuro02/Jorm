
from config import ActorStatusType

def check_is_admin(func):
    def wrapper(self, line):
        with open('admins.txt', 'r') as file:
            lines = file.readlines()  # Read all lines into a list
        # Check if the target string is in any of the lines
        found = any(self.name in admin for admin in lines)
        if not found:
            self.sendLine('You are not an admin')
            return
        return func(self, line)
    return wrapper
            

def check_no_empty_line(func):
    def wrapper(self, line):
        if line == '':
            self.sendLine('This command needs arguments')
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
            self.sendLine('@redYou are dead@normal')
            return 
        return func(self, line)
    return wrapper

def check_not_in_combat(func):
    def wrapper(self, line):
        if self.status == ActorStatusType.FIGHTING:
            self.sendLine('You can\'t do this in combat')
            return
        return func(self, line)
    return wrapper