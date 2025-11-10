
from configuration.config import ActorStatusType


def check_is_admin(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
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
        return func(*args, **kwargs)
    return wrapper
            
def check_not_spamming(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
        self.recently_send_message_count += 100
        if self.recently_send_message_count >= 1000: 
            self.recently_send_message_count = 1500
            return
        else:
            return func(*args, **kwargs)
    return wrapper

def check_not_trading(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
        if self.trade_manager.trade != None:
            self.sendLine(f'You can\'t do this while trading')
            return
        else:
            return func(*args, **kwargs)
    return wrapper

def check_no_empty_line(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
        line = args[1] if args else kwargs.get('line')
        if line == '':
            self.sendLine(f'Command "{self.last_command_used}" needs arguments, try "help {self.last_command_used}".')
            return
        else:
            return func(*args, **kwargs)
    return wrapper

def check_your_turn(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
        if self.status != ActorStatusType.FIGHTING:
            return func(*args, **kwargs)
        if self.room.combat != None:
            if self.room.combat.current_actor != self:
                self.sendLine('Not your turn to act.')
                return
        return func(*args, **kwargs)
    return wrapper

def check_alive(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
        if self.status == ActorStatusType.DEAD:
            self.sendLine(f'@redYou are dead, use "rest home" command to respawn.@normal')
            return 
        return func(*args, **kwargs)
    return wrapper

def check_not_in_combat(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
        if self.status == ActorStatusType.FIGHTING:
            self.sendLine(f'You can\'t use command "{self.last_command_used}" in combat, try "help {self.last_command_used}".')
            return
        return func(*args, **kwargs)
    return wrapper

def check_no_combat_in_room(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
        if self.room.combat != None:
            self.sendLine('You can\'t do that while there is a fight going on!')
            return
        return func(*args, **kwargs)
    return wrapper

def check_not_in_party_or_is_party_leader(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
        if not self.is_not_in_party_or_is_party_leader():
            self.sendLine('Only party leader can do this')
            return
        return func(*args, **kwargs)
    return wrapper

def check_not_in_party(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
        if self.party_manager.party != None:
            self.sendLine('You can\'t do this while in a party')
            return
        return func(*args, **kwargs)
    return wrapper

def check_no_unfriendlies_present_in_room(func):
    def wrapper(*args, **kwargs):
        self = args[0] if args else kwargs.get('self')
        enemy_found = False
        for i in self.room.actors.values():
            if type(i).__name__ != 'Player':
                enemy_found = True
        if enemy_found:
            self.sendLine(f'You can\'t do this while enemies are nearby')
            return
        return func(*args, **kwargs)
    return wrapper