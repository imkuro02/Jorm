
from configuration.config import ActorStatusType
import utils
def command_look(self, line):

    def draw_local_area(self, room_id):

        VIEW_RANGE = 3

        class Art:
            # all
            GROUD =         '@yellow.'

            # middle
            RECALL_SITE =   '@green+'
            PLAYER_HERE =   '@cyan@'
            SPECIAL_EXIT =  '@normal?'
            SPECIAL_EXIT_AND_PLAYER = '@cyan?'
            
            # right
            STAIRS_DOWN =   '@normal>'

            # left
            STAIRS_UP =     '@normal<'
            
        offsets = {
            'north': [ 0  ,  -1 ],
            'west':  [ -1 ,  0 ],
            'south': [ 0  , 1 ],
            'east':  [ 1  ,  0 ],
            'left':  [ -1 ,  0 ],
            'right': [ 1  ,  0 ],
            # up and down need to FUCK OFF
            # otherwise they mess up and override other rooms they are on top of or under of
            'up':    [0,0+1000],
            'down':  [0,0+1000]
        }

        x = 0
        y = 0
        start_room = self.protocol.factory.world.rooms[room_id]
        loc = f'{x},{y}'
        grid = {}
        grid[loc] = start_room
        cur_room = start_room
        mapped_rooms = []


        for direction in cur_room.exits:
            if direction in offsets:
                _x = x
                _y = y
                _x += offsets[direction][0]
                _y += offsets[direction][1]
                loc = f'{_x},{_y}'
                grid[loc] = self.protocol.factory.world.rooms[cur_room.exits[direction]]
                    
        for _ in range(0,VIEW_RANGE):
            _grid = {}
            for loc in grid:
                for direction in grid[loc].exits:
                    if direction not in offsets:
                        continue

                    _x = x
                    _y = y
                    _x = int(loc.split(',')[0])
                    _y = int(loc.split(',')[1])

                    _x += offsets[direction][0]
                    _y += offsets[direction][1]
                    _loc = f'{_x},{_y}'
                    if _loc not in grid:
                        _grid[_loc] = self.protocol.factory.world.rooms[grid[loc].exits[direction]]

            
            for _loc in _grid:
                if _loc not in grid:
                    grid[_loc] = _grid[_loc]
            #_grid_ = grid | _grid
            #grid = _grid_
        


            
        
        _grid = grid
        grid = {}
        for _loc in _grid:
            _x = int(_loc.split(',')[0])
            _y = int(_loc.split(',')[1])
            loc = f'{_x+VIEW_RANGE},{_y+VIEW_RANGE}'
            grid[loc] = _grid[_loc]       

        '''
        name_grid = {}
        for i in grid:
            name_grid[i] = grid[i].uid
        '''

        t = utils.Table((VIEW_RANGE*2)+1,0)

        for _y in range(0,(VIEW_RANGE*2)+1):
            for _x in range(0,(VIEW_RANGE*2)+1):
                loc = f'{_x},{_y}'
                
                cell = ''
                
                if loc not in grid:
                    t.add_data('   ')
                    continue


                # left
                if 'up' in grid[loc].exits:
                    cell += Art.STAIRS_UP
                else:
                    cell += Art.GROUD
                    

                # mid
                if 100 == 10:
                    pass
                #elif len([ x for x in grid[loc].exits.keys() if x not in offsets.keys() ]) != 0 and loc == f'{VIEW_RANGE},{VIEW_RANGE}': #set(offsets.keys()) - set(grid[loc].exits.keys()):
                #    cell += Art.SPECIAL_EXIT_AND_PLAYER
                elif loc == f'{VIEW_RANGE},{VIEW_RANGE}':
                    cell += Art.PLAYER_HERE
                elif grid[loc].can_be_recall_site:
                    cell += Art.RECALL_SITE
                elif len([ x for x in grid[loc].exits.keys() if x not in offsets.keys() ]) != 0:
                    cell += Art.SPECIAL_EXIT
                else:
                    cell += Art.GROUD

                # right
                if 'down' in grid[loc].exits:
                    cell += Art.STAIRS_DOWN
                else:
                    cell += Art.GROUD
                
                #self.sendLine(f'{loc}, {grid[loc].exits.keys()}')
                t.add_data(cell)
               
        output = t.get_table()
        self.sendLine(output)


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
        
        
        draw_local_area(self, room_id)
        


        self.sendLine(see)

    def look_entity(entity):
        sheet = entity.get_character_sheet()
        self.sendLine(f'You are looking at {sheet}')
        return 

    if line == '':
        look_room(self, self.room.uid)
        return

    if line != '':
        entity = self.get_entity(line)
        if entity == None:
            return
        look_entity(entity)

