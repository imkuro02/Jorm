
from configuration.config import ActorStatusType
import utils
def command_look(self, line):
    def look_room(self, room_id):
        room = self.factory.world.rooms[room_id]

        if room_id == self.room.uid:
            see = f'You are in @yellow{room.name}@normal\n'
        else:
            see = f'You look at @yellow{room.name}@normal\n'
        see = see + f'@cyan{room.description}@normal\n'


        if len(room.entities) == 1:
            see = see + 'You are alone.\n'
        else:
            see = see + 'there are others here:\n'
            for i in room.entities.values():
                if i == self:
                    pass
                else:
                    see = see + i.pretty_name() 
                    if i.status == ActorStatusType.DEAD:
                        see = see + f' @yellow(DEAD)@normal'
                    if i.status == ActorStatusType.FIGHTING:
                        see = see + f' @yellow(FIGHTING)@normal'
                    see = see +'\n'

        exits = self.protocol.factory.world.rooms[room.uid].exits
        see = see + f'You can go: @yellow{"@normal, @yellow".join([name for name in exits])}@normal.'
        see = see + '\n'

        if not room.inventory_manager.is_empty():
            see = see + 'On the ground you see:\n'
            for i in room.inventory_manager.items.values():
                see = see + f'{i.name}' + '\n'
        '''
        index = 0
        if not room.inventory_manager.is_empty():
            
            see = see + 'On the ground you see:\n'
            for i in room.inventory_manager.items.values():
                index += 1
                see = see + f'{index}. {i.name}' + '\n'
        '''
        self.sendLine(see)

    if line == '':
        look_room(self, self.room.uid)
        return

    if line != '':
        #exits = self.protocol.factory.world.rooms[self.room.uid].exits
        
        #for _exit in exits:
        #    if line in _exit:
        #        room_id = self.protocol.factory.world.rooms[exits[_exit]].uid
        #        look_room(self, room_id)
        #        return

        entity = self.get_entity(line)
        if entity == None:
            return
        sheet = entity.get_character_sheet()
        self.sendLine(f'You are looking at {sheet}')

