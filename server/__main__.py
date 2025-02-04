from twisted.internet import reactor, protocol, ssl, task
from protocol import Protocol
from world import World
from database import Database
from utils import logging 
import configuration.config as config
config.load()


class ServerFactory(protocol.Factory):
    def __init__(self):
        self.protocols = set()
        self.world = World(self)
        self.db = Database()
        self.ticks_passed = 0
        self.tickrate: int = 30
        tickloop = task.LoopingCall(self.tick)
        tickloop.start(1 / self.tickrate)

        logging.info('Server started')

        # where the actors will be stored for rank command
        self.ranks = {}
        
    def tick(self):
        self.ticks_passed += 1
        self.world.tick()
        #for room in self.world.rooms.values():
        #    room.tick()
        if self.ticks_passed % (30 * 120) == 0 or self.ticks_passed == 10:
            for i in self.protocols:
                if i.actor != None:
                    self.db.write_actor(i.actor)
            self.ranks = self.db.find_all_accounts()

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
    print("Server started on port 4000 with SSL and 4001 non SSL")
    reactor.run()
