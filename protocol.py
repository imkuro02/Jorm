from twisted.internet import protocol
from actors.player import Player
from items.manager import load_item, save_item
import utils
from config import StatType

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
        self.state: callable = self.LOGIN
        self.actor = None
        self.username = None
        

    def clear_screen(self):
        self.sendLine('\x1b[0m')
        self.sendLine('\u001B[2J')


    def splash_screen(self):
        self.clear_screen()
        self.sendLine('Type "b" to restart login / register process.')
        self.sendLine('Welcome! Please enter your username:')


    def PLAY(self, line):
        if line == 'save':
            self.save_actor()
            return
        if line == 'load':
            self.load_actor()
            return
        if line == 'logout':
            self.disconnect()
            return
        if line == 'clear':
            self.clear_screen()
            return
        self.actor.handle(line)
        return
            
    def REGISTER(self, line):
        if line == 'b':
            self.username = None
            self.splash_screen()
            self.state = self.LOGIN
            return

        password = line
        self.factory.db.write_user(self.username, password)
        self.sendLine(f'Account "{self.username}" registered! input password:')
        self.state = self.LOGIN
        #self.username = None

    def LOGIN(self, line):
        if line == 'b':
            self.username = None
            self.splash_screen()
            self.state = self.LOGIN
            return

        if self.username == None:
            self.username = line
            user = self.factory.db.read_user(self.username)
            if user == None:
                self.sendLine(f'Creating a new account with name "{self.username}", input password: ')
                self.state = self.REGISTER
            else:
                self.sendLine(f'Account exists, input password: \n')
        else:
            user = self.factory.db.read_user(self.username)
            if user[1] == line:
                self.clear_screen()
                self.load_actor()
                
                     
                
                
            else:
                self.splash_screen()
                self.sendLine(f'Wrong password.')

    # override
    def connectionMade(self):
        self.factory.protocols.add(self)
        self.splash_screen()
        
    def compare_slots_to_items(self):
        for i in self.actor.slots.values():
            if i not in self.actor.inventory:
                if i == None: continue
                print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!{i} is not in inventory?')

    def load_actor(self):
        
        actor = self.factory.db.read_actor(self.username)

        if actor == None: # new actor
            self.actor = Player(self, _id = None, name = self.username, room = self.factory.world.rooms['loading'])
        else: # load an existing actor
            self.actor = Player(self, _id = actor['id'], name = self.username, room = self.factory.world.rooms['loading'])
            self.actor.stats = actor['stats']
            self.actor.skills = actor['skills']
            self.actor.slots = actor['slots']
            for item in actor['inventory'].values():
                new_item = load_item(item)
                self.actor.inventory[new_item.id] = new_item
            self.compare_slots_to_items()

        self.state = self.PLAY
        
        if actor == None:
            self.save_actor()
            self.actor.room.world.rooms['tutorial'].move_player(self.actor)
        else:
            self.actor.room.world.rooms['home'].move_player(self.actor)
        
    def save_actor(self):
        self.sendLine('saving..')
        inventory = {}
        for i in self.actor.inventory:
            inventory[i] = save_item(self.actor.inventory[i])

        self.factory.db.write_actor(self.actor.name ,{
            'id':   self.actor.id,
            'name': self.actor.name,
            'stats': self.actor.stats,
            'skills': self.actor.skills,
            'slots': self.actor.slots,
            'inventory': inventory
        })
        self.compare_slots_to_items()

        actor = self.factory.db.read_actor(self.username)
        #print(actor)

    def disconnect(self):
        self.transport.abortConnection()

    # override
    def connectionLost(self, reason):
        if self.actor != None:

            self.actor.affect_manager.unload_all_affects(silent = True)
                
            self.save_actor()

            # teleport player to town to remove them safely
            self.factory.world.rooms['home'].move_player(self.actor)
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

        #if line:  # skip empty lines
        if '@' in line:
            line = line + '@normal'
        self.state(line)
        return

    def sendLine(self, line):
        line = utils.add_color(line)
        self.transport.write(f'{line}\n'.encode('utf-8'))