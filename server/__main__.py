from twisted.internet import reactor, protocol, ssl, task
from protocol import Protocol
from world import World
from database import Database
from utils import logging, Table
import configuration.config as config
config.load()
import time
import utils


class ServerFactory(protocol.Factory):
    def __init__(self):
        self.protocols = set()
        
        self.db = Database()
        self.ticks_passed = 0
        self.runtime = time.time()
        self.start = time.time()
        self.tickrate: int = 30*1
        self.world = World(self)
        tickloop = task.LoopingCall(self.tick)
        tickloop.start(1 / self.tickrate)

        logging.info('Server started')
        

        # where the actors will be stored for rank command
        self.ranks = {}
        
    def tick(self):
        
        # kick afk users after 16 min, notified at min 15
        to_disconnect = []
        for i in self.protocols:
            if i.tick_since_last_message == (self.ticks_passed - (30*60*30)):
                i.sendLine('@yellow!!!@normal You are @redAFK@normal and will be logged out soon @yellow!!!@normal')
            if i.tick_since_last_message == (self.ticks_passed - (30*60*31)):
                to_disconnect.append(i)
        for i in to_disconnect:
            i.disconnect()
            #i.connectionLost('AFK')
            

        self.ticks_passed += 1
        self.world.tick()
        #for room in self.world.rooms.values():
        #    room.tick()
        if self.ticks_passed % (30 * 120) == 0 or self.ticks_passed == 10:
            for i in self.protocols:
                if i.actor != None:
                    self.db.write_actor(i.actor)
            self.ranks = self.db.find_all_accounts()

        self.runtime = time.time() - self.start
        #if self.runtime > self.ticks_passed/30:
        #utils.debug_print(self.ticks_passed, self.runtime, self.ticks_passed/30 , '\r')

    def buildProtocol(self, addr):
        return Protocol(self)

    def broadcast(self, message):
        for client in self.protocols:
            if client.username != None:
                client.sendLine(message)

if __name__ == '__main__':
    factory = ServerFactory()

    ssl_context = ssl.DefaultOpenSSLContextFactory('server.key', 'server.crt')

    # Listen on SSL port
    reactor.listenSSL(4000, factory, ssl_context) 
    # AND NON SSL MUAHHAHA TELNET LETSGOOOO 
    reactor.listenTCP(4001, factory)
    utils.debug_print("Server started on port 4000 with SSL and 4001 non SSL")
    reactor.run()

    factory.world.game_time.save_game_time()
    utils.debug_print('Exiting...')
