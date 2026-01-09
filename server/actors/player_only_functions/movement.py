from actors.player_only_functions.checks import check_not_in_party, check_not_in_party_or_is_party_leader, check_your_turn, check_alive, check_no_empty_line, check_not_in_combat
from configuration.config import ActorStatusType, Audio, ITEMS, StatType
from affects.affects import Affect
import random
@check_not_in_party_or_is_party_leader
@check_your_turn
@check_alive
def command_flee(self, line):
    #self.sendLine('@redFleeing is temporarely disabled in game sorry...@normal')
    #return

    if self.room.combat == None:
        self.sendLine('You are not in combat, you don\'t need to flee')
        return
    #self.simple_broadcast(
    #    None,
    #    f'{self.pretty_name()} flees!'
    #)
    #self.protocol.factory.world.rooms[self.recall_site].move_actor(self, silent = True)
    self.status = ActorStatusType.NORMAL
    #self.simple_broadcast(
    #    f'You have fled back to {self.room.pretty_name()}',
    #    f'{self.pretty_name()} comes running in a panic!',
    #    sound = Audio.BUFF
    #)

    #if self.status != ActorStatusType.FIGHTING:
    #    self.sendLine('You must be fighting to flee!')
    #    return

    self.simple_broadcast('You flee!', f'{self.pretty_name()} flees!', sound = Audio.BUFF)
    self.status = ActorStatusType.NORMAL
    if self.party_manager.party != None:
        if self.party_manager.party.actor == self:
            for par in self.party_manager.party.participants.values():

                if par == self:
                    continue
                # if dead, they get ressed afterwards so dont need to set status to normal
                # if fighting, set to normal otherwise combat will continue even without being there
                if par.status == ActorStatusType.FIGHTING:
                    par.status = ActorStatusType.NORMAL
                par.sendLine('You flee too!')
                #par.protocol.factory.world.rooms[self.recall_site].move_actor(par, silent = True)






@check_not_in_combat
@check_alive
@check_not_in_party_or_is_party_leader
def command_go(self, line = '', room_id = None):
    #if room_id is not none, skip checks, this means that its probably a teleport
    world = self.protocol.factory.world
    if room_id == None:
        if line == '':
            self.sendLine('Go where?')
            return

        direction = None

        exits = self.room.get_active_exits()
        for _exit in exits:
            if ' '+line.lower() in ' '+_exit.direction.lower():
                room_obj = _exit.get_room_obj()
                if room_obj != None:
                    direction = _exit

        if direction == None:
            self.simple_broadcast(
                f'You walk into a wall',
                f'{self.pretty_name()} walks into a wall',
                sound = Audio.ERROR, send_to = 'room'
                )
            roll = random.randint(0,100)
            if roll == 0:
                aff = Affect(
                    affect_source_actor = self,
                    affect_target_actor = self,
                    name='Bumpy',
                    description='You have a large stupid bump on your head',
                    turns=100
                    )
                self.affect_manager.set_affect_object(aff)
            return

        # check for combat
        yes_any_can_start_fights = False
        highest_can_start_fights_level = 0
        for actor in self.room.actors.values():
            if type(actor).__name__ in 'Npc Enemy'.split():
                yes_npcs = True
                if actor.can_start_fights and actor.status == ActorStatusType.NORMAL:
                    yes_any_can_start_fights = True
                    if highest_can_start_fights_level < actor.stat_manager.stats[StatType.LVL]:
                        highest_can_start_fights_level = actor.stat_manager.stats[StatType.LVL]



        # if aggressive enemies are present while you cannot go to a new room, but you can still return to previous room
        if yes_any_can_start_fights and direction.get_room_obj().get_real_id() != self.room_previous:
            roll = 0
            if self.stat_manager.stats[StatType.LVL] - (highest_can_start_fights_level+3) <= 0:
                roll = 1#random.randint(0,5)
            if self.room.is_an_instance():
                roll = 1
            #if self.room.world.game_time.TIME_OF_DAY['night']:
            #    roll = random.randint(0,2)

            if roll == 1:
                if self.party_manager.party != None:
                    if self.party_manager.party.actor == self:
                        self.sendLine(f'{self.room.is_enemy_present().pretty_name()} is in the way', sound=Audio.ERROR) #self.command_fight('')
                        return
                else:
                    self.sendLine(f'{self.room.is_enemy_present().pretty_name()} is in the way', sound=Audio.ERROR) #self.command_fight('')
                    return

        if direction.blocked and self.room.is_enemy_present() and self.room.combat == None:
            self.sendLine(f'{self.room.is_enemy_present().pretty_name()} is blocking the path', sound=Audio.ERROR)
            return

        if direction.item_required != None:
            item = self.inventory_manager.get_item_by_premade_id(direction.item_required)
            if item == None:
                self.sendLine(f'You need {ITEMS[direction.item_required]["name"]}',sound=Audio.ERROR)
                return
            else:
                if direction.item_required_consume == True:
                    self.sendLine(f'{item.name} crumbles to dust')
                    self.inventory_manager.remove_item(item,1)



        old_room = self.room
        new_room = direction.get_room_obj().id
    else:
        old_room = self.room
        new_room = room_id


    self.simple_broadcast(None,f'You follow {self.pretty_name()}', send_to = 'room_party', sound = Audio.walk())

    world.rooms[new_room].move_actor(self)
    self.sendSound(Audio.walk())


    if self.recall_site not in [room.id for room in self.room.world.rooms.values() if room.can_be_recall_site] and self.room.can_be_recall_site:
        #self.command_rest('set')
        self.rest_set('')




    # move party members
    if self.party_manager.party != None:
        if self.party_manager.party.actor == self:
            for par in self.party_manager.party.participants.values():
                if par == self:
                    continue
                if par.room != old_room:
                    continue
                #par.command_go(line)
                self.room.move_actor(par, silent = True)
                #par.sendLine(f'You follow {self.pretty_name()}', sound = Audio.walk())
                #par.finish_turn(force_cooldown = True)
                par.sendSound(Audio.walk())


    # move followers (currently moves EVERYTHING)
    '''
    potential_followers = old_room.actors.copy()

    for par in potential_followers.values():
        if par == self:
            continue
        if par.room != old_room:
            continue
        self.room.move_actor(par, silent = True)
        par.finish_turn(force_cooldown = True)
        par.sendSound(Audio.walk())
        utils.debug_print(par)
    '''

    # show participants and or yourself the room
    if self.party_manager.party != None:
        if self.party_manager.party.actor == self:
            for par in self.party_manager.party.participants.values():
                if par == self:
                    par.new_room_look()
                if par.room.get_real_id() not in par.explored_rooms:
                    par.explored_rooms.append(self.room.get_real_id())

    else:
        self.new_room_look()
        if self.room.get_real_id() not in self.explored_rooms:
            self.explored_rooms.append(self.room.get_real_id())

    # finish turns
    self.finish_turn(force_cooldown = True)
    if self.party_manager.party != None:
        if self.party_manager.party.actor == self:
            for par in self.party_manager.party.participants.values():
                if par == self:
                    continue
                #if par.room != old_room:
                #    continue
                par.finish_turn(force_cooldown = True)
