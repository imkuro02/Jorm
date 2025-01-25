from twisted.internet import protocol
from actors.player import Player
from items.manager import load_item, save_item
import utils
from configuration.config import StatType, ItemType
import uuid
import copy

IAC = b'\xff'     # Interpret as Command
WILL = b'\xfb'    # Will Perform
WONT = b'\xfc'    # Will Not Perform
DO = b'\xfd'      # Please Do
DONT = b'\xfe'    # Please Don’t
ECHO = b'\x01'    # Echo
LINEMODE = b'\x22' # Line mode
#GMCP = b'\x'

class Protocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.state: callable = self.LOGIN_OR_REGISTER
        
        self.actor = None

        self.account = None
        self.username = None
        self.password = None

        self.id = str(uuid.uuid4())
        

    def clear_screen(self):
        self.sendLine('\x1b[0m')
        self.sendLine('\u001B[2J')

    def splash_screen(self):
        splash = f'''
 _    _      _                            _            ___                      
| |  | |    | |                          | |          |_  |                     
| |  | | ___| | ___ ___  _ __ ___   ___  | |_ ___       | | ___  _ __ _ __ ___  
| |/\| |/ _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \      | |/ _ \| '__| '_ ` _ \ 
\  /\  /  __/ | (_| (_) | | | | | |  __/ | || (_) | /\__/ / (_) | |  | | | | | |
 \/  \/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/  \____/ \___/|_|  |_| |_| |_|

                       .-'~~~-.
                     .'o  oOOOo`.       CURRENTLY ONLINE: {len(self.factory.protocols)}
                    :~~~-.oOo   o`.     DISCORD: https://discord.gg/AZ98axtXc6
                     `. \ ~-.  oOOo.
                       `.; / ~.  OO:
                       .'  ;-- `.o.'
                      ,'  ; ~~--'~
                      ;  ;
_______\|/__________\\\\;_\\\\//___\|/___________________\|/_______________________                                               
        '''
        self.clear_screen()
        splash = f'@bwhite{splash}@normal'
        self.sendLine(splash)

    def change_state(self, state):
        match state:
            case self.LOGIN_OR_REGISTER:
                self.id = str(uuid.uuid4())
                self.account = None
                self.username = None
                self.password = None
                self.sendLine('type @bgreennew@normal to register, type @bgreenlogin@normal to log in.')

            case self.LOGIN_USERNAME:
                self.sendLine('Your @bgreenusername@normal:')

            case self.LOGIN_PASSWORD:
                self.sendLine('Your @bgreenpassword@normal:')

            case self.REGISTER_USERNAME:
                self.sendLine('Please use a unique username, not linking your Jorm account to anything private')
                self.sendLine('Creating new account. enter your @bgreenusername@normal:')

            case self.REGISTER_PASSWORD1:
                self.sendLine('Please use a unique password, only for Jorm')
                self.sendLine('Enter your @bgreenpassword@normal:')

            case self.REGISTER_PASSWORD2:
                self.sendLine('Enter @bgreenpassword@normal again:')

            case self.PLAY_OR_SETTINGS:
                self.sendLine(f'You are now logged in as @bcyan{self.username}@normal')
                self.sendLine(f'Type @bgreenplay@normal to enter the game')
                self.sendLine(f'Type @bgreenback@normal to log out')
                self.sendLine(f'...')
                #self.sendLine(f'To set new username or password type:')
                #self.sendLine(f'username "new_username" "current_password"\n(This is NOT your in game name)')
                #self.sendLine(f'username "new_username" "current_password"')
                self.sendLine(f'Set new password with:\npassword "new_password" "current_password"')
                

        self.state = state
            

    def PLAY(self, line):
        self.actor.handle(line)
        return
            
    def REGISTER_USERNAME(self, line):
        self.account = self.factory.db.find_account_from_username(line)
        if self.account != None:
            self.sendLine('This username is already taken')
            self.change_state(self.REGISTER_USERNAME)
            return
        
        if len(line) >= 21 or len(line) <= 5:
            self.sendLine('Username must be between 4 and 20 characters long')
            self.change_state(self.REGISTER_USERNAME)
            return

        if not line.isalnum():
            self.sendLine('Username can only contain letters and numbers')
            self.change_state(self.REGISTER_USERNAME)
            return

        self.username = line
        self.change_state(self.REGISTER_PASSWORD1)

    def REGISTER_PASSWORD1(self, line):
        if len(line) < 6:
            self.sendLine('Your password must be a minimum of 6 character')
            self.change_state(self.REGISTER_PASSWORD1)
            return

        self.password = line
        self.change_state(self.REGISTER_PASSWORD2)

    def REGISTER_PASSWORD2(self, line):
        if line != self.password:
            self.sendLine('Passwords do not match')
            self.change_state(self.LOGIN_OR_REGISTER)
            return
        
        self.factory.db.create_new_account(self.id, self.username, self.password)
        self.sendLine('Account created! you can now log in!')
        self.change_state(self.LOGIN_OR_REGISTER)

    def LOGIN_PASSWORD(self, line):
        self.password = line
        if self.account == None:
            self.sendLine('Wrong username or password')
            self.change_state(self.LOGIN_OR_REGISTER)
            return

        if self.account[2] != line:
            self.sendLine('Wrong username or password')
            self.change_state(self.LOGIN_OR_REGISTER)
            return

        utils.logging.debug(self.id + ' -> ' + self.account[0])
        self.id = self.account[0]
        self.username = self.account[1]
        self.password = self.account[2]

        for online_account in self.factory.protocols:
            if self.id == online_account.id and self != online_account:
                self.sendLine('@redYou are already logged in on another device@normal')
                self.change_state(self.LOGIN_OR_REGISTER)
                return
            #print(online_account.id)
        self.change_state(self.PLAY_OR_SETTINGS)
        #self.sendLine(str(self.account))
        
        
    def LOGIN_USERNAME(self, line):
        self.account = self.factory.db.find_account_from_username(line)
        self.username = line
        self.change_state(self.LOGIN_PASSWORD)
        return

    def LOGIN_OR_REGISTER(self, line):
        if line.lower() == 'login'.lower():
            self.change_state(self.LOGIN_USERNAME)
            return
        if line.lower() == 'new'.lower():
            self.change_state(self.REGISTER_USERNAME)
            return
        self.change_state(self.LOGIN_OR_REGISTER)
        return

    def PLAY_OR_SETTINGS(self, line):
        if line == 'back' or line == 'b':
            self.change_state(self.LOGIN_OR_REGISTER)
            return

        if line == 'play' or line == 'p':
            self.load_actor()
            self.change_state(self.PLAY)
            return

        
        try:
            vals = line.split('"')
            setting = vals[0].strip()
            new_val = vals[1]
            cur_pwd = vals[3]
        except IndexError:
            return

        
        if setting.lower() not in 'username password'.split():
            self.change_state(self.PLAY_OR_SETTINGS)
            return

        if cur_pwd != self.password:
            self.sendLine('Wrong password')
            return

        '''
        if setting.lower() == 'username':
            acc = self.factory.db.find_account_from_username(new_val)
            #print(acc)
            if acc != None:
                self.sendLine('@redThis login username is taken@normal')
                return
            self.username = new_val
        '''
        if setting.lower() == 'password':
            self.password = new_val
        

        self.factory.db.create_new_account(self.id, self.username, self.password)
        self.sendLine('@bgreenAccount updated@normal')
    # override
    def connectionMade(self):
        utils.logging.debug(self.id + 'Connection made')
        self.factory.protocols.add(self)
        self.splash_screen()
        self.change_state(self.LOGIN_OR_REGISTER)
        
    def compare_slots_to_items(self):
        for i in self.actor.slots_manager.slots.values():
            if i not in self.actor.inventory_manager.items:
                if i == None: continue
                print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!{i} is not in inventory?')

    def load_actor(self):
        actor = self.factory.db.read_actor(self.account[0])
        #print('>>>',actor)

        if actor == None: # new actor
            self.actor = Player(self, _id = None, name = self.username, room = self.factory.world.rooms['loading'])
        else: # load an existing actor
            self.actor = Player(self, _id = actor['actor_id'], name = actor['actor_name'], room = self.factory.world.rooms['loading'])
            self.actor.recall_site = actor['actor_recall_site'] 

            self.actor.stats.update(actor['stats'])
            self.actor.skills = actor['skills']

            for item in actor['inventory'].values():
                new_item = load_item(item['premade_id'])
                new_item.keep =         item['item_keep']
                new_item.id =           item['item_id']

                self.actor.inventory_manager.add_item(new_item)
            self.compare_slots_to_items()

            # actor is loaded without equipment stats on
            # add them back here
            for item_id in actor['equipment']:
                # skip if item is somehow not in inventory
                if item_id not in self.actor.inventory_manager.items:
                    print(item_id, 'is equiped but not in inventory?')
                    continue
                if self.actor.inventory_manager.items[item_id].item_type != ItemType.EQUIPMENT:
                    print(item_id, 'is equiped but not ItemType.EQUIPMENT')
                    continue
                item = self.actor.inventory_manager.items[item_id]
                self.actor.inventory_equip(item, forced = True)

        self.state = self.PLAY

        if actor == None:
            self.save_actor()
            self.actor.recall_site = 'tutorial'
        else:
            if self.actor.recall_site not in self.actor.room.world.rooms:
                self.actor.recall_site = 'tutorial'

        self.actor.room.world.rooms[self.actor.recall_site].move_player(self.actor)
        
    def save_actor(self):
        self.factory.db.write_actor(self.actor)
        a = self.factory.db.read_actor(self.id)

    def disconnect(self):
        self.transport.abortConnection()

    # override
    def connectionLost(self, reason):
        utils.logging.debug(self.id + ' >> Connection lost')
        if self.actor != None:

            self.actor.simple_broadcast(None, f'{self.actor.pretty_name()} Disconnected.')
            self.actor.affect_manager.unload_all_affects(silent = True)
            self.actor.trade_manager.trade_stop()
            self.actor.party_manager.party_leave()
            self.save_actor()
            

            # teleport player to loading to remove them safely
            self.factory.world.rooms['loading'].move_player(self.actor)
            # remove player from combat
            del self.actor.room.entities[self.actor.id]
            
        self.factory.protocols.remove(self)

    # override
    def dataReceived(self, data):
        

        # interrupt
        if data == b'\xff\xf4\xff\xfd\x06':
            self.disconnect()
            return

        # decode and process input data
        line = data.decode('utf-8', errors='ignore').strip()

        # log account unique ID and what message was sent
        if self.state == self.PLAY:
            utils.logging.debug(self.account[0] + ' -> ' + line)

        #if line:  # skip empty lines
        if '@' in line:
            line = line + '@normal'
        self.state(line)
        return

    def sendLine(self, line):
        line = utils.add_color(line)
        self.transport.write(f'{line}\n'.encode('utf-8'))