from twisted.internet import reactor, protocol, ssl, task
from protocol import Protocol
from world import World
from database import Database
import config
from use_manager import UseManager

class ServerFactory(protocol.Factory):
    def __init__(self):
        self.config = config.Config()
        self.use_manager = UseManager(self)

        self.protocols = set()
        self.world = World(self)
        self.db = Database()

        self.tickrate: int = 30
        tickloop = task.LoopingCall(self.tick)
        tickloop.start(1 / self.tickrate)

        

    def tick(self):
        self.world.tick()
        #for room in self.world.rooms.values():
        #    room.tick()

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
