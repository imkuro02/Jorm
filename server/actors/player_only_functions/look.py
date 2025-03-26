
from configuration.config import ActorStatusType
import utils
def command_look(self, line):

    def draw_local_area(self, room_id):

        VIEW_RANGE = 4
        START_LOC = f'{VIEW_RANGE},{VIEW_RANGE}'

        class Art:
            # all
            GROUND =         '@yellow.'
            EMPTY =         ' '

            # middle
            RECALL_SITE =   '@green+'
            PLAYER_HERE =   '@cyan@'
            SPECIAL_EXIT =  '@normal?'
            SPECIAL_EXIT_AND_PLAYER = '@cyan?'
            RECALL_SITE_AND_PLAYER = '@cyan+'
            
            # right
            STAIRS_DOWN =   '@normal>'

            # left
            STAIRS_UP =     '@normal<'
            
        offsets = {
            'north': [ 0  ,  -2 ],
            'west':  [ -2 ,  0 ],
            'south': [ 0  , 2 ],
            'east':  [ 2  ,  0 ],
            #'left':  [ -2 ,  0 ],
            #'right': [ 2  ,  0 ],
            # up and down need to FUCK OFF
            # otherwise they mess up and override other rooms they are on top of or under of
            'up':    [0,0+1000],
            'down':  [0,0+1000]
        }

        offsets_path = {
            'north': [ 0  ,  -1 ],
            'west':  [ -1 ,  0 ],
            'south': [ 0  , 1 ],
            'east':  [ 1  ,  0 ],
            #'left':  [ -1 ,  0 ],
            #'right': [ 1  ,  0 ],
            # up and down need to FUCK OFF
            # otherwise they mess up and override other rooms they are on top of or under of
            'up':    [0,0+1000],
            'down':  [0,0+1000]
        }

        t = utils.Table((VIEW_RANGE*2)+1,0)


        
        grid = {}
        start_room = self.protocol.factory.world.rooms[room_id]
        grid[START_LOC] = room_id

        for _exit in start_room.exits:
            if _exit not in offsets:
                continue
            x = 0
            y = 0
            x += offsets[_exit][1] + VIEW_RANGE
            y += offsets[_exit][0] + VIEW_RANGE
            _loc = f'{x},{y}'
            if _loc not in grid:
                grid[_loc] = start_room.exits[_exit]
            x += -offsets_path[_exit][1]
            y += -offsets_path[_exit][0]
            _loc = f'{x},{y}'
            if _loc not in grid:
                grid[_loc] = 'PATH'

        _grid = {}
        for r in grid:
            _grid[r] = grid[r]
            
        for r in range(0,1):
            for room_loc in _grid:
                if grid[room_loc] == 'PATH':
                    continue
                room = self.protocol.factory.world.rooms[grid[room_loc]]
                _x = int(room_loc.split(',')[0])
                _y = int(room_loc.split(',')[1])
                for _exit in room.exits:
                    if _exit not in offsets:
                        continue
                    x = _x
                    y = _y
                    x += offsets[_exit][1] 
                    y += offsets[_exit][0] 
                    _loc = f'{x},{y}'

                    grid[_loc] = room.exits[_exit]
                    x += -offsets_path[_exit][1]
                    y += -offsets_path[_exit][0]
                    _loc = f'{x},{y}'
                    if _loc not in grid:
                        grid[_loc] = 'PATH'

            _grid = {}
            for r in grid:
                _grid[r] = grid[r]


        #print(grid)
        for _x in range(0,(VIEW_RANGE*2)+1):
            for _y in range(0,(VIEW_RANGE*2)+1):
                """
                cords = f'{_x},{_y}'
                if cords not in grid:
                    t.add_data('...','@red')
                    continue
                if grid[cords] == 'PATH':
                    t.add_data('XXX')
                    continue
                if cords in grid:
                    #t.add_data(grid[cords])
                    t.add_data('!!!')
                    continue
                t.add_data('ERR','@red')
                """
                loc = f'{_x},{_y}'
                
                cell = ''

                if loc not in grid:
                    cell = Art.EMPTY*3
                    t.add_data(cell)
                    continue
                
                if grid[loc] == 'PATH':
                    cell = ' '+Art.GROUND+' '
                    t.add_data(cell)
                    continue

                room = self.protocol.factory.world.rooms[grid[loc]]
                #print(room)
                # left
                if 'up' in room.exits:
                    cell += Art.STAIRS_UP
                else:
                    cell += Art.EMPTY
                    
                # mid
                if 100 == 10:
                    pass
                elif room.can_be_recall_site and loc == START_LOC:
                    cell += Art.RECALL_SITE_AND_PLAYER
                elif len([ x for x in room.exits if x not in offsets ]) != 0 and loc == START_LOC: #set(offsets.keys()) - set(grid[loc].exits.keys()):
                    cell += Art.SPECIAL_EXIT_AND_PLAYER
                elif loc == START_LOC:
                    cell += Art.PLAYER_HERE
                elif room.can_be_recall_site:
                    cell += Art.RECALL_SITE
                elif len([ x for x in room.exits if x not in offsets ]) != 0:
                    cell += Art.SPECIAL_EXIT
                else:
                    cell += Art.GROUND

                # right
                if 'down' in room.exits:
                    cell += Art.STAIRS_DOWN
                else:
                    cell += Art.EMPTY

                if grid[loc] == 'PATH':
                    cell = ' '+Art.GROUND+' '
                    t.add_data(cell)
                    continue

                t.add_data(cell)

                
                

        output = t.get_table()
        #output = str(offsets)

            
            

        '''
        x = 0
        y = 0
        start_room = self.protocol.factory.world.rooms[room_id]
        loc = f'{x},{y}'
        grid = {}
        path = {}
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
                print(loc)

        _grid = {}
        _path = {}
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
                    _x += offsets_path[direction][0]
                    _y += offsets_path[direction][1]
                    _loc = f'{_x},{_y}'
                    _path[_loc] = True
                   
        print(_path)
        for _loc in _grid:
            if _loc not in grid:
                grid[_loc] = _grid[_loc]

        for _loc in _path:
            if _loc not in path:
                path[_loc] = _path[_loc]
            #_grid_ = grid | _grid
            #grid = _grid_


            
        
        _grid = grid
        grid = {}
        for _loc in _grid:
            _x = int(_loc.split(',')[0])
            _y = int(_loc.split(',')[1])
            loc = f'{_x+VIEW_RANGE},{_y+VIEW_RANGE}'
            grid[loc] = _grid[_loc]       

        _path = path
        path = {}
        for _loc in _path:
            _x += int(_loc.split(',')[0])
            _y += int(_loc.split(',')[1])
            loc = f'{_x+VIEW_RANGE},{_y+VIEW_RANGE}'
            path[loc] = _path[_loc] 


        t = utils.Table((VIEW_RANGE*2)+1,0)

        for _y in range(0,(VIEW_RANGE*2)+1):
            for _x in range(0,(VIEW_RANGE*2)+1):
                loc = f'{_x},{_y}'
                
                cell = ''
                
                if loc not in grid and loc not in path:
                    t.add_data('   ')
                    continue

                if loc in path:
                    t.add_data('---')
                    continue
                    
                # left
                if 'up' in grid[loc].exits:
                    cell += Art.STAIRS_UP
                else:
                    cell += Art.GROUND
                    

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
                    cell += Art.GROUND

                # right
                if 'down' in grid[loc].exits:
                    cell += Art.STAIRS_DOWN
                else:
                    cell += Art.GROUND
                
                #self.sendLine(f'{loc}, {grid[loc].exits.keys()}')
                t.add_data(cell)
               
        output = t.get_table()
        '''
        return output
        #self.sendLine(output)


    def look_room(self, room_id):
        room = self.factory.world.rooms[room_id]

        if room_id == self.room.id:
            see = f'You are in @yellow{room.name}@normal\n'
        else:
            see = f'You look at @yellow{room.name}@normal\n'
        #see += draw_local_area(self, room_id)
        see = see + f'@cyan{room.description}@normal\n'


        if len(room.actors) == 1:
            see = see + 'You are alone.\n'
        else:
            see = see + 'there are others here:\n'
            for i in room.actors.values():
                if i == self:
                    pass
                else:
                    see = see + i.pretty_name() 
                    if i.status == ActorStatusType.DEAD:
                        see = see + f' @yellow(DEAD)@normal'
                    if i.status == ActorStatusType.FIGHTING:
                        see = see + f' @yellow(FIGHTING)@normal'
                    see = see +'\n'

        exits = self.protocol.factory.world.rooms[room.id].exits
        #blocked_exits = self.protocol.factory.world.rooms[room.id].blocked_exits
        see = see + f'You can go: '
        for _exit in exits:
            #if exit_name not in blocked_exits:
            if _exit.secret:
                continue
            #if _exit.blocked and self.room.is_enemy_present():
            #    continue
            see = see + f'@yellow{_exit.pretty_direction()}@normal, '
            #else:
            #    see = see + f'@red{exit_name}@normal, '

        #see = see + f'You can go: @yellow{"@normal, @yellow".join([name for name in exits])}@normal.'
        see = see + '\n'

        if not room.inventory_manager.is_empty():
            see = see + 'On the ground you see:\n'
            for i in room.inventory_manager.items.values():
                see = see + f'{i.pretty_name()}' + '\n'
        
        
        
        


        self.sendLine(see)

    def look_actor(actor):
        sheet = actor.get_character_sheet()
        self.sendLine(f'You are looking at {sheet}')
        return 

    if line == '':
        look_room(self, self.room.id)
        return

    if line != '':
        actor = self.get_actor(line)
        if actor == None:
            return
        look_actor(actor)

