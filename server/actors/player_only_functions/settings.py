from utils import match_word
from actors.player_only_functions.checks import check_no_empty_line
from configuration.config import Color
BANNED_ALIASES = ['settings','help','alias','reset'] # this gets set in actors.player_only_functions.commands

class SETTINGS:
    GMCP = 'gmcp'
    ALIAS = 'alias'
    LOOK = 'look'
    VIEW_ROOM = 'viewroom'
    VIEW_MAP = 'viewmap'
    VIEW_ASCII_ART = 'viewasciiart'
    PVP = 'pvp'
    RESET = 'reset'
    LOGOUT = 'logout'
    DEBUG = 'debug'
    PWD = 'password'
    USR = 'username' # not in LIST_SETTINGS
    EMAIL = 'email'
    AUTO_BATTLER = 'autobattler'
    PROMPT = 'prompt'
    LIST_SETTINGS = [
        GMCP, ALIAS, VIEW_ROOM, VIEW_MAP, VIEW_ASCII_ART, PVP, RESET, LOGOUT, DEBUG, PWD, USR, EMAIL, PROMPT, #AUTO_BATTLER
    ]



LIST_ON  = ['on','true','enabled','enable','1']
LIST_OFF = ['off','false','disabled','disable','0']

class Settings:
    def __init__(self, actor, aliases = None, gmcp = True, email = '', view_room = True, view_ascii_art = True, view_map = True, pvp = False, debug = False, prompt = None):
        self.actor = actor
        if aliases == None:
            self.aliases = {}
        else:
            self.aliases = aliases
        self.gmcp = gmcp
        self.email = email
        self.view_room = view_room
        self.view_map = view_map
        self.view_ascii_art = view_ascii_art
        self.pvp = pvp
        self.debug = debug
        self.autobattler = False

        #self.prompt_default2 = '[@bred#HP#@normal/@bred#HPMAX#@normal | @bred#PHYARM#@normal/@bred#PHYARMMAX#@normal] [@bcyan#MP#@normal/@bcyan#MPMAX#@normal | @bcyan#MAGARM#@normal/@bcyan#MAGARMMAX#@normal]>'
        #self.prompt_default = '[@bred#HP%#@normal% | @bred#PHYARM%#@normal%] [@bcyan#MP%#@normal% | @bcyan#MAGARM%#@normal%]>' + self.prompt_default2
        #self.prompt_default = '[@bred#HP%#@normal%|@bred#PHYARM%#@normal%] [@bcyan#MP%#@normal%|@bcyan#MAGARM%#@normal%]>'
        self.prompt_default = {
            '0': '<@green#HP#@bgreenL@yellow#PHYARM#@byellowH@cyan#MAGARM#@bcyanW@normal>',
            '1': '<@green#HP#@bgreenL @yellow#PHYARM#@byellowH @cyan#MAGARM#@bcyanW @red#THREAT#@bredT@normal>'
        }
        if prompt != None:
            self.prompt = prompt
        else:
            self.prompt = self.prompt_default['0']

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

            case SETTINGS.VIEW_ASCII_ART:
                if len(line) == 1:
                    self.actor.sendLine('View Ascii Art setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.view_ascii_art = self.true_or_false(value)
                self.actor.sendLine(f'View Ascii Art enabled: {self.view_ascii_art}')

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
                succ = proto.register_account_changes(username, password)
                if succ and proto.guest:
                    proto.guest = False
                    proto.actor.sendLine(f'{Color.GOOD}This account is no longer a guest account\n{Color.IMPORTANT}REMEMBER: You should set a password with "settings password <new password>"{Color.NORMAL}')

            case SETTINGS.PWD:
                proto = self.actor.protocol
                if proto.guest:
                    proto.actor.sendLine(f'{Color.BAD}You are currently a guest, you need to set a new username before changing your password{Color.NORMAL}')
                    return

                password = ' '.join(original_line.split()[1:])
                username = proto.username
                #proto.guest = False
                proto.register_account_changes(username, password)

            case SETTINGS.EMAIL:
                proto = self.actor.protocol
                if proto.guest:
                    proto.actor.sendLine(f'{Color.BAD}You are currently a guest, you need to set a new username before changing your email{Color.NORMAL}')
                    return

                print(original_line)
                email = ' '.join(original_line.split()[1:])
                if email == '':
                    self.actor.sendLine(f'Your current email is "{Color.GOOD}{self.email}{Color.NORMAL}".')
                    return
                self.email = email
                password = proto.password
                username = proto.username
                succ = proto.register_account_changes(username, password)
                self.actor.sendLine(f'Your email is now "{Color.GOOD}{self.email}{Color.NORMAL}".')


            case SETTINGS.AUTO_BATTLER:
                if len(line) == 1:
                    self.actor.sendLine('Autobattler setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.autobattler = self.true_or_false(value)
                self.actor.sendLine(f'Autobattler enabled: {self.autobattler}')

            case SETTINGS.PROMPT:
                prompt = ' '.join(original_line.split()[1:])
                if prompt == ' ' or prompt == '':
                    self.actor.sendLine(f'Current prompt is: {self.prompt}', color = False)
                    return
                if prompt in self.prompt_default:
                    self.prompt = self.prompt_default[prompt]
                else:
                    self.prompt = prompt
                #proto.register_account_changes(username, password)



@check_no_empty_line
def command_settings(self, line):
    self.settings_manager.command_settings(line)
