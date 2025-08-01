from utils import match_word
from actors.player_only_functions.checks import check_no_empty_line

BANNED_ALIASES = ['settings','help','alias','reset'] # this gets set in actors.player_only_functions.commands

class SETTINGS:
    GMCP = 'gmcp'
    ALIAS = 'alias'
    LOOK = 'look'
    VIEW_ROOM = 'viewroom'
    VIEW_MAP = 'view_map'
    PVP = 'pvp'
    RESET = 'reset'
    LOGOUT = 'logout'
    DEBUG = 'debug'
    PWD = 'password'
    USR = 'username' # not in LIST_SETTINGS
    LIST_SETTINGS = [
        GMCP, ALIAS, VIEW_ROOM, VIEW_MAP, PVP, RESET, LOGOUT, DEBUG, PWD, USR 
    ]



LIST_ON  = ['on','true','enabled','enable','1']
LIST_OFF = ['off','false','disabled','disable','0']

class Settings:
    def __init__(self, actor, aliases = None, gmcp = True, view_room = True, view_map = True, pvp = False, debug = False):
        self.actor = actor
        if aliases == None:
            self.aliases = {}
        else:
            self.aliases = aliases
        self.gmcp = gmcp

        self.view_room = view_room
        self.view_map = view_map
        self.pvp = pvp
        self.debug = debug
        
    def true_or_false(self, value):
        if value in LIST_ON:
            return True
        if value in LIST_OFF:
            return False
        return False

    
    def command_settings(self, line):
        original_line = line
        line = line.split()

        command = match_word(line[0], SETTINGS.LIST_SETTINGS)

        #self.actor.sendLine(f'{line}, {command}')
        match command:
            case SETTINGS.RESET:
                self.actor.sendLine('All settings reset to default')
                self.actor.settings_manager = Settings(self.actor)
                return
            case SETTINGS.ALIAS:
                if len(line) == 1: # view aliases
                    self.actor.sendLine('View aliasses')
                    output = ''
                    for alias in self.aliases:
                        output += f'{alias} = {self.aliases[alias]}\n'
                    self.actor.sendLine(output)
                    return
                if len(line) == 2: # clear an alias
                    alias = line[1]
                    if alias in self.aliases:
                        self.actor.sendLine(f'Clear alias "{alias}"')
                        del self.aliases[alias]
                    return
                if len(line) >= 3: # set an alias
                    alias = line[1]
                    if alias in BANNED_ALIASES:
                        self.actor.sendLine(f'You can\'t set {alias} as an alias')
                        return

                    string = ' '.join(line[2::]).strip()
                    self.actor.sendLine(f'{alias} = {string}')
                    self.aliases[alias] = string
                    return

            case SETTINGS.GMCP:
                if len(line) == 1:
                    self.actor.sendLine('GMCP setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.gmcp = self.true_or_false(value)
                self.actor.protocol.enabled_gmcp = self.gmcp
                self.actor.sendLine(f'GMCP enabled: {self.gmcp}')

            case SETTINGS.VIEW_MAP:
                if len(line) == 1:
                    self.actor.sendLine('View Map setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.view_map = self.true_or_false(value)
                self.actor.sendLine(f'View Map enabled: {self.view_map}')

            case SETTINGS.VIEW_ROOM:
                if len(line) == 1:
                    self.actor.sendLine('View Room setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.view_room = self.true_or_false(value)
                self.actor.sendLine(f'View Room enabled: {self.view_room}')

            case SETTINGS.PVP:
                if len(line) == 1:
                    self.actor.sendLine('PVP setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.view_room = self.true_or_false(value)
                self.actor.sendLine(f'PVP enabled: {self.pvp}')

            case SETTINGS.DEBUG:
                if len(line) == 1:
                    self.actor.sendLine('Debug setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.debug = self.true_or_false(value)
                self.actor.sendLine(f'Debug enabled: {self.debug}')

            case SETTINGS.LOGOUT:
                proto = self.actor.protocol
                proto.unload_actor()
                proto.change_state(proto.LOGIN_OR_REGISTER)

            case SETTINGS.USR:
                proto = self.actor.protocol
                password = proto.password
                username = ' '.join(original_line.split()[1:])
                proto.register_account_changes(username, password)
        
            case SETTINGS.PWD:
                proto = self.actor.protocol
                password = ' '.join(original_line.split()[1:])
                username = proto.username
                proto.register_account_changes(username, password)
        
@check_no_empty_line
def command_settings(self, line):
    self.settings_manager.command_settings(line)