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
    COLOR = 'color'
    LIST_SETTINGS = [
        GMCP, ALIAS, VIEW_ROOM, VIEW_MAP, VIEW_ASCII_ART, PVP, RESET, LOGOUT, DEBUG, PWD, USR, EMAIL, PROMPT, COLOR, #AUTO_BATTLER
    ]




LIST_ON  = ['on','true','enabled','enable','1']
LIST_OFF = ['off','false','disabled','disable','0']

class Settings:
    def __init__(self, actor):
        self.actor = actor
        self.defaults = {
            SETTINGS.GMCP: True,
            SETTINGS.ALIAS: {},
            SETTINGS.VIEW_ROOM: True,
            SETTINGS.VIEW_MAP: True,
            SETTINGS.VIEW_ASCII_ART: True,
            SETTINGS.EMAIL: '',
            SETTINGS.PROMPT: '0',
            SETTINGS.DEBUG: False,
            SETTINGS.COLOR: {
                '@normal':               '',
                '@back':                 '\x1b[0;00x',
                '@error':                '',
                '@important':            '',
                '@tooltip':              '',
                '@description':          '',

                '@name_player':          '',
                '@name_admin':           '',
                '@name_enemy':           '',
                '@name_npc':             '',

                '@room_name':            '',
                '@room_description':     '',
                '@room_name_safe':       '',
                '@room_name_instanced':  '',

                '@quest_name':           '',
                '@quest_description':    '',

                '@map_player':           '',
                '@map_important':        '',
                '@map_normal':           '',
                '@map_room':             '',
                '@map_path':             '',

                '@item_keep':            '',
                '@item_equipped':        '',
                '@item_trading':         '',
                '@item_new':             '',
                '@item_material':        '',

                '@damage_pure':          '',
                '@damage_physical':      '',
                '@damage_magical':       '',
                '@damage_healing':       '',
                
                '@combat_turn':          '',

                '@stat_life':            '',
                '@stat_hold':            '',
                '@stat_ward':            '',
            },
        }

        #self.prompt_default2 = '[@bred#HP#@normal/@bred#HPMAX#@normal | @bred#PHYARM#@normal/@bred#PHYARMMAX#@normal] [@bcyan#MP#@normal/@bcyan#MPMAX#@normal | @bcyan#MAGARM#@normal/@bcyan#MAGARMMAX#@normal]>'
        #self.prompt_default = '[@bred#HP%#@normal% | @bred#PHYARM%#@normal%] [@bcyan#MP%#@normal% | @bcyan#MAGARM%#@normal%]>' + self.prompt_default2
        #self.prompt_default = '[@bred#HP%#@normal%|@bred#PHYARM%#@normal%] [@bcyan#MP%#@normal%|@bcyan#MAGARM%#@normal%]>'
        self.prompt_default = {
            '2': '<@green#LIFE#/#LLIFEMAX#@bgreenL@yellow#HOLD#/#LHOLDMAX#@byellowH@cyan#WARD#/#LWARDMAX#@bcyanW@normal>',
            '1': '<@green#LIFE%#@bgreen% @yellow#HOLD%#@byellow% @cyan#WARD%#@bcyan%@normal>',
            '0': '<@green#LIFE#@bgreenL@yellow#HOLD#@byellowH@cyan#WARD#@bcyanW@normal>'
        }

        self.settings = {}
        
   

    def true_or_false(self, value):
        if value.lower() in LIST_ON:
            return True
        if value.lower() in LIST_OFF:
            return False
        return False

    def true_or_false_or_str(self, value):
        _value = value
        if _value.lower() in LIST_ON:
            return True
        if _value.lower() in LIST_OFF:
            return False
        return value

    def get_value(self, key):
        if key not in self.settings:
            val = self.defaults[key]
        else:
            val = self.settings[key]
        return val

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

            case SETTINGS.COLOR:
                if len(line) == 1: # view aliases
                    self.actor.sendLine('View colors')
                    output = ''
                    if SETTINGS.COLOR not in self.settings:
                        self.actor.sendLine('No colors')
                        return
                    for alias in self.settings[SETTINGS.COLOR]:
                        output += f'{alias} = {self.settings[SETTINGS.COLOR][alias]}\n'
                    self.actor.sendLine(output)
                    return
                if len(line) == 2: # clear an alias
                    alias = line[1]
                    if alias in self.settings[SETTINGS.COLOR]:
                        self.actor.sendLine(f'Clear color "{alias}"')
                        del self.settings[SETTINGS.COLOR][alias]
                    return
                if len(line) >= 3: # set an alias
                    alias = line[1]
                    string = ' '.join(line[2::]).strip()
                    self.actor.sendLine(f'{alias} = {string}')
                    if SETTINGS.COLOR not in self.settings:
                        self.settings[SETTINGS.COLOR] = {}
                    self.settings[SETTINGS.COLOR][alias] = string
                    return

            case SETTINGS.ALIAS:
                if len(line) == 1: # view aliases
                    self.actor.sendLine('View aliasses')
                    output = ''
                    if SETTINGS.ALIAS not in self.settings:
                        self.actor.sendLine('No aliases')
                        return

                    for alias in self.settings[SETTINGS.ALIAS]:
                        output += f'{alias} = {self.settings[SETTINGS.ALIAS][alias]}\n'
                    self.actor.sendLine(output)
                    return
                if len(line) == 2: # clear an alias
                    alias = line[1]
                    if alias in self.settings[SETTINGS.ALIAS]:
                        self.actor.sendLine(f'Clear alias "{alias}"')
                        del self.settings[SETTINGS.ALIAS][alias]
                    return
                if len(line) >= 3: # set an alias
                    alias = line[1]
                    if alias in BANNED_ALIASES:
                        self.actor.sendLine(f'You can\'t set {alias} as an alias')
                        return

                    string = ' '.join(line[2::]).strip()
                    self.actor.sendLine(f'{alias} = {string}')
                    if SETTINGS.ALIAS not in self.settings:
                        self.settings[SETTINGS.ALIAS] = {}
                    self.settings[SETTINGS.ALIAS][alias] = string
                    return

            case SETTINGS.GMCP:
                if len(line) == 1:
                    self.actor.sendLine('GMCP setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.settings[SETTINGS.GMCP] = self.true_or_false(value)
                self.actor.protocol.enabled_gmcp = self.true_or_false(value)
                self.actor.sendLine(f'GMCP enabled: {self.true_or_false(value)}')

            case SETTINGS.VIEW_MAP:
                if len(line) == 1:
                    self.actor.sendLine('View Map setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.settings[SETTINGS.VIEW_MAP] = self.true_or_false(value)
                self.actor.sendLine(f'View Map enabled: {self.settings[SETTINGS.VIEW_MAP]}')

            case SETTINGS.VIEW_ASCII_ART:
                if len(line) == 1:
                    self.actor.sendLine('View Ascii Art setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.settings[SETTINGS.VIEW_ASCII_ART] = self.true_or_false(value)
                self.actor.sendLine(f'View Ascii Art enabled: {self.settings[SETTINGS.VIEW_ASCII_ART]}')

            case SETTINGS.VIEW_ROOM:
                if len(line) == 1:
                    self.actor.sendLine('View Room setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.settings[SETTINGS.VIEW_ROOM] = self.true_or_false(value)
                self.actor.sendLine(f'View Room enabled: {self.settings[SETTINGS.VIEW_ROOM]}')

            case SETTINGS.DEBUG:
                if len(line) == 1:
                    self.actor.sendLine('Debug setting needs an argument (on or off?)')
                    return
                value = line[1]
                self.settings[SETTINGS.DEBUG] = self.true_or_false(value)
                self.actor.sendLine(f'Debug enabled: {self.settings[SETTINGS.DEBUG]}')

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

                #print(original_line)
                email = ' '.join(original_line.split()[1:])
                if email == '':
                    if SETTINGS.EMAIL in self.settings:
                        self.actor.sendLine(f'Your current email is "{Color.GOOD}{self.settings[SETTINGS.EMAIL]}{Color.NORMAL}".')
                    else:
                        self.actor.sendLine(f'You dont have email set, please set your email with "{Color.GOOD}settings email [your@email.com]{Color.NORMAL}".')
                    return
                self.settings[SETTINGS.EMAIL] = email
                password = proto.password
                username = proto.username
                succ = proto.register_account_changes(username, password)
                self.actor.sendLine(f'Your email is now "{Color.GOOD}{self.settings[SETTINGS.EMAIL]}{Color.NORMAL}".')

            case SETTINGS.PROMPT:
                prompt = ' '.join(original_line.split()[1:])
                if prompt == ' ' or prompt == '':
                    self.actor.sendLine(f'Current prompt is: {self.prompt}', color = False)
                    return
                if prompt in self.prompt_default:
                    self.prompt = self.prompt_default[prompt]
                else:
                    self.settings[SETTINGS.PROMPT] = prompt
                #proto.register_account_changes(username, password)



@check_no_empty_line
def command_settings(self, line):
    self.settings_manager.command_settings(line)
