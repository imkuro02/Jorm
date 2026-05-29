




''' send_to usecase


send_to = [i for i in self.room.actors.values() if type(i).__name__ == 'Player' and 
            i.recall_site != RoomConstant.TAVERN]
_utils.greet_message(
    self = self, 
    message = f'{self.id} says "You should check out the tavern, if you have not yet"',
    send_to = send_to
    )

not using send_to argument will just try to broadcast message to all, 
but sending a list of "players" will have it only broadcast to those players

having multiple greet_message() functions will execute only the first one that runs succesfully
if player is not in send_to they will be ignored and another greet_message might execute for them
'''


def greet_message(self, message, send_to: list = [None]):
    if self.factory.ticks_passed % (30 * 4) == 0:
        if not hasattr(self,'actors_in_room'):
            self.actors_in_room = {}
        
        for i in self.room.actors.values():
            if i.id in self.actors_in_room:
                continue
            if i not in send_to and send_to != [None]:
                continue
            self.actors_in_room[i.id] = i

        _to_del = []
        for i in self.actors_in_room:
            if i not in self.room.actors:
                _to_del.append(i)

        for i in _to_del:
            del self.actors_in_room[i]

        for i in self.actors_in_room.values():
            if type(i).__name__ != 'Player':
                continue
            if i == None:
                continue
            if i.current_dialog != None:
                continue
            i.pretty_broadcast(message, None, list_pretty_name_objects = [self])

        for i in self.actors_in_room:
            self.actors_in_room[i] = None