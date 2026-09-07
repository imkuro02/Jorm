import configuration.config as config
from database.database import Database
from systems.protocol import Protocol
from systems.utils import Table, logging
from systems.world import World
from twisted.internet import protocol, reactor, ssl, task
from systems.delayed_functions import DelayedFunctionsManager
config.load()
import time

import systems.utils
#from systems.ecs_manager import ECSManager
from configuration.constants.tickrate import TICKRATE
import context

#import tracemalloc
#tracemalloc.start(25)   

class ServerFactory(protocol.Factory):
    def __init__(self):
        context.FACTORY = self

        self.time_spent_calculating = 0
        self.ticks_too_slow = 0

        self.ticks_passed = 0
        self.delayed_functions = DelayedFunctionsManager(factory = self)
        self.protocols = set()
        
        #self.ecs_manager = ECSManager(self)
        
        self.db = Database(self)
        
        self.runtime = time.time()
        self.start = time.time()
        self.tickrate: int = TICKRATE * 1
        self.world = World(self)

        tickloop = task.LoopingCall(self.tick)
        tickloop.start(1 / self.tickrate)

        logging.info("Server started")

        # where the actors will be stored for rank command
        self.ranks = self.db.find_all_actors()
        
    def tick(self):

        tick_start = time.time()
        self.ticks_passed += 1
        self.world.tick()
        #self.ecs_manager.tick()
        # for room in self.world.rooms.values():
        #     room.tick()

        if self.ticks_passed % (TICKRATE * 60 * 3) == 0 or self.ticks_passed == 10:
            for i in self.protocols:
                if i.actor != None:
                    # self.db.write_actor(i.actor)
                    i.save_actor()
            self.ranks = self.db.find_all_actors()

        self.delayed_functions.tick()

        '''
        if self.ticks_passed & (TICKRATE * 30) == 0:
            snapshot = tracemalloc.take_snapshot()

            for stat in snapshot.statistics("lineno")[:20]:
                print(stat)
        '''

        self.runtime = time.time() - self.start

        tick_end = time.time()

        self.time_spent_calculating += tick_end-tick_start

        _threashold = 0

        if tick_end-tick_start >= 1 / TICKRATE:
            systems.utils.debug_print(f'tick {self.ticks_passed} spent {(tick_end-tick_start)}s executing')
            self.ticks_too_slow += 1
        if self.ticks_passed % TICKRATE == 0:
            if self.time_spent_calculating >= _threashold:
                _thinking = f'Time thinking: {self.time_spent_calculating}'.ljust(40)
                _ = f'{_thinking}/  TICK: {self.ticks_passed}'
                systems.utils.debug_print(_)

            self.time_spent_calculating = 0


    def buildProtocol(self, addr):
        return Protocol(self)

    def broadcast(self, message):
        for client in self.protocols:
            if client.username != None:
                client.send_line(message)


# for i in config.ICONS:
#    print('\n\n')
#    print(systems.utils.add_color(config.ICONS[i]))
#

if __name__ == "__main__":
    #import tracemalloc
    #tracemalloc.start()

    
    factory = ServerFactory()
    print(context.FACTORY,'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx')


    ssl_context = ssl.DefaultOpenSSLContextFactory("server.key", "server.crt")

    # Listen on SSL port
    reactor.listenSSL(4000, factory, ssl_context)
    # AND NON SSL MUAHHAHA TELNET LETSGOOOO
    reactor.listenTCP(4001, factory)
    systems.utils.debug_print("Server started on port 4000 with SSL and 4001 non SSL")

    from skills.manager import check_for_broken_skills
    check_for_broken_skills()
    from configuration.config import check_for_broken_icons
    check_for_broken_icons()
    from configuration.config import check_for_not_spawnable_enemies
    check_for_not_spawnable_enemies()
    from configuration.config import check_for_not_droppable_or_spawnable_items
    check_for_not_droppable_or_spawnable_items()

    reactor.run()

    factory.world.game_time.save_game_time()
    systems.utils.debug_print("Exiting...")
    systems.utils.debug_print(f"{factory.ticks_too_slow} out of {factory.ticks_passed} ticks spent too long executing")

    #snapshot = tracemalloc.take_snapshot()
    #top_stats = snapshot.statistics("traceback")

    #for stat in top_stats[:10]:
    #    print(stat)
    #    for line in stat.traceback.format():
    #        print(line)
