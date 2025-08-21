
from configuration.config import ActorStatusType
import utils

def command_map(self, line):
    setting_render_walls = False
    room_id = self.room.id
    VIEW_RANGE = 7
    START_LOC = f'{VIEW_RANGE},{VIEW_RANGE}'

    class Art:
        # all
        GROUND =         '@yellow#'
        NS =         '@yellow:'
        EW =         '@yellow---'
        EMPTY = ' '
        EMPTYWALL =         '@wall   '
        WALL = '@wall###'
        DOOR ='@yellow/'

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
        if _exit.direction not in offsets:
            continue
        if _exit.secret:
            continue
        if _exit.item_required != None:
            continue
        # do not duplicate if room leads to one that already is placed
        if _exit.to_room_id in grid.values():
            continue

        x = 0
        y = 0
        x += offsets[_exit.direction][1] + VIEW_RANGE
        y += offsets[_exit.direction][0] + VIEW_RANGE
        _loc = f'{x},{y}'

        
        
        if _loc not in grid:
            grid[_loc] = _exit.to_room_id
        

        x += -offsets_path[_exit.direction][1]
        y += -offsets_path[_exit.direction][0]
        _loc = f'{x},{y}'

        if _loc not in grid:
            grid[_loc] = 'PATH'

    _grid = {}
    for r in grid:
        _grid[r] = grid[r]
        
    for r in range(0,VIEW_RANGE*1):
        for room_loc in _grid:
            #print(_grid[room_loc])
            if grid[room_loc] == 'PATH':
                continue

            room = self.protocol.factory.world.rooms[grid[room_loc]]
            
            if room.doorway:
                continue

            _x = int(room_loc.split(',')[0])
            _y = int(room_loc.split(',')[1])

            for _exit in room.exits:
                if _exit.direction not in offsets:
                    continue
                if _exit.secret:
                    continue
                #if _exit.item_required != None:
                #    continue
                
                # do not duplicate if room leads to one that already is placed
                #if _exit.to_room_id in grid.values():
                #    continue
                x = _x
                y = _y
                x += offsets[_exit.direction][1] 
                y += offsets[_exit.direction][0] 
                _loc = f'{x},{y}'

                #if _loc not in grid:
                #    continue

                #print(_exit.to_room_id, grid.values())
                if _exit.to_room_id not in grid.values():
                    if _loc in grid:
                        continue
                    
                    grid[_loc] = _exit.to_room_id 
                                  
                
                x += -offsets_path[_exit.direction][1]
                y += -offsets_path[_exit.direction][0]
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

            _grid = grid


            if loc not in grid:
                __x, __y, = map(int, loc.split(','))
                
                directions = {
                    'w': f'{__x-1},{__y}',
                    'e': f'{__x+1},{__y}',
                    'n': f'{__x},{__y+1}',
                    's': f'{__x},{__y-1}',
                    'ne': f'{__x+1},{__y+1}',
                    'nw': f'{__x-1},{__y+1}',
                    'se': f'{__x+1},{__y-1}',
                    'sw': f'{__x-1},{__y-1}'
                }

                walled = False
                '''
                if any(
                    d in grid and grid[d] in self.room.world.rooms and self.room.world.rooms[grid[d]].doorway is True
                    for d in directions.values()
                ):
                    cell = 'x' * 3
                    t.add_data(cell)
                    walled = True
                    continue
                '''
                if not setting_render_walls:
                    if not walled:
                        #if d['n'] not in grid and d['w'] not in grid and d['e'] not in grid and d['s'] not in grid     and d['sw'] not in grid and d['se'] not in grid and d['nw'] not in grid and d['ne'] not in grid:
                        if all(d not in grid for d in directions.values()):
                            #cell = Art.EMPTYWALL * 1
                            cell = Art.EMPTY * 3
                            t.add_data(cell)
                            walled = True
                            continue
                            
                    if not walled:
                        if directions['w'] not in grid or directions['e'] not in grid:
                            cell = Art.WALL #Art.EMPTY*3
                            t.add_data(cell)  
                            walled = True
                            continue

                    if not walled:
                        if directions['n'] not in grid or directions['s'] not in grid:
                            cell = Art.WALL #Art.EMPTY*3
                            t.add_data(cell)  
                            walled = True
                            continue
                
                if not walled:
                    cell = Art.EMPTY*3
                    t.add_data(cell) 
                continue
            
            #if grid[loc] == 'PATH':
            #    cell = ' '+Art.GROUND+' '
            #    t.add_data(cell)
            #    continue
            

            if grid[loc] == 'PATH':
                __x, __y = loc.split(',')
                __x = int(__x)
                __y = int(__y)
                left  = f'{__x-1},{__y}'
                right = f'{__x+1},{__y}'
                north = f'{__x},{__y+1}'
                south = f'{__x},{__y-1}'
                cell = ' '+Art.GROUND+' '
                _left = left in grid
                _right = right in grid
                _north = north in grid
                _south = south in grid

                if _left or _right:
                    cell = ' '+Art.NS+' '
                if _north or _south:
                    cell = ''+Art.EW+''
                cross = 0
                for i in [_left,_right,_south,_north]:
                    cross += i
                if cross >= 3:
                    cell = ' + '

                t.add_data(cell)
                continue

            room = self.protocol.factory.world.rooms[grid[loc]]
           
            #print(room)
            # left
            if 'up' in [ x.direction for x in room.exits ]:
                cell += Art.STAIRS_UP
            else:
                cell += Art.EMPTY
                
            # mid
            if 100 == 10:
                pass
            
            elif room.can_be_recall_site and loc == START_LOC:
                cell += Art.RECALL_SITE_AND_PLAYER
            #elif len([ x for x in room.exits if x.direction not in offsets ]) != 0 and loc == START_LOC: #set(offsets.keys()) - set(grid[loc].exits.keys()):
            #    cell += Art.SPECIAL_EXIT_AND_PLAYER
            elif loc == START_LOC:
                cell += Art.PLAYER_HERE
            elif room.doorway:
                cell += Art.DOOR
            elif room.can_be_recall_site:
                cell += Art.RECALL_SITE
            #elif len([ x for x in room.exits if x.direction not in offsets ]) != 0:
            #    cell += Art.SPECIAL_EXIT
            else:
                cell += Art.GROUND

            # right
            if 'down' in [ x.direction for x in room.exits ]:
                cell += Art.STAIRS_DOWN
            else:
                cell += Art.EMPTY

            

            t.add_data(cell)

            
            
    # empty space stripper
    '''
    output = t.get_table()
    split_output = output.split('\n')
    combined_output = ''
    left_strip_len = 1000

    for i in split_output[:-1]:
        strip_len = 0
        i = i.replace('\n','')
        x = 0
        while x < len(i):
            if i[x] == ' ':
                strip_len += 1
                x += 1
            elif i.startswith('@normal', x):
                strip_len += len('@normal')
                x += len('@normal')
            else:
                break
        #print(strip_len, left_strip_len)
        if strip_len < left_strip_len:
            left_strip_len = strip_len
            #print(i[x-10:])

    for i in split_output:            
        if (i).replace('@normal','').replace(' ','') != '':
            combined_output = combined_output + i[left_strip_len:] + '\n'
    ##############################################################################
    '''
    combined_output = t.get_table()


    self.sendLine('<Map Start>\n'+combined_output+'<Map End>')

def command_scan(self, line):
    see = ''
    nearby_actors = {}
    nearby_rooms = self.get_nearby_rooms(view_range = 1)
    if '0,0,0' in nearby_rooms:
        del nearby_rooms['0,0,0']

    for r in nearby_rooms:
        nearby_actors[r] = self.room.world.rooms[nearby_rooms[r]].actors.values()
    if len(nearby_actors) >= 1:
        
        location_translations = {
            'x': {
                '-1':   'west',
                '1':    'east',
                '0': ''
            },
            'y': {
                '-1':   'north',
                '1':    'south',
                '0': ''
            },
            'z': {
                '-1':   'down',
                '1':    'up',
                '0': ''
            }
        }

        
        for a in nearby_actors:
            x, y, z = a.split(',')
            x = location_translations['x'][str(max(-1, min(1, int(x))))]
            y = location_translations['y'][str(max(-1, min(1, int(y))))]
            z = location_translations['z'][str(max(-1, min(1, int(z))))]

            EMPTY = ''
            if x == EMPTY and y == EMPTY and z == EMPTY: 
                direction_name = f'What the fuck?'
            elif x == EMPTY and y != EMPTY and z != EMPTY:
                direction_name = f' {y} and {z}'
            elif x != EMPTY and y == EMPTY and z != EMPTY:
                direction_name = f' {x} and {z}'
            elif x != EMPTY and y != EMPTY and z == EMPTY:
                direction_name = f' {y}-{x}'
            elif x == EMPTY and y == EMPTY and z != EMPTY:
                direction_name = f' {z}'
            elif x != EMPTY and y == EMPTY and z == EMPTY:
                direction_name = f' {x}'
            elif x == EMPTY and y != EMPTY and z == EMPTY:
                direction_name = f' {y}'
            elif x != EMPTY and y != EMPTY and z != EMPTY:
                direction_name = f' {y}-{x} and {z}'
            
            for i in nearby_actors[a]:
                see = see + ''+i.pretty_name() + ''
                if i.status == ActorStatusType.DEAD:
                    see = see + f' is dead' + direction_name + ' from here'
                elif i.status == ActorStatusType.FIGHTING:
                    see = see + f' is fighting' + direction_name + ' from here'
                else:
                    see = see + '' + direction_name + ' from here'
                see = see +'\n'
    if see == '':
        self.sendLine('You scan your surroundings but see no one')
        return
    
    self.sendLine(f'You scan your surroundings and see: \n{see[:-1:]}')

def command_look(self, line):
    def look_room(self, room_id):
        room = self.factory.world.rooms[room_id]

        if room_id == self.room.id:
            see = f'You are in @yellow{room.pretty_name()}@normal\n'
        else:
            see = f'You look at @yellow{room.pretty_name()}@normal\n'
        #see += draw_local_area(self, room_id)
        see = see + f'@cyan{room.get_description()}@normal\n'


        exits = self.protocol.factory.world.rooms[room.id].exits
        #blocked_exits = self.protocol.factory.world.rooms[room.id].blocked_exits
        exit_count = 0
        see_exits = ''
        for _exit in exits:
            #if exit_name not in blocked_exits:
            if _exit.secret:
                continue
            #if _exit.blocked and self.room.is_enemy_present():
            #    continue
            see_exits = see_exits + f'You can go {_exit.pretty_direction()}\n'
            exit_count += 1
            #else:
            #    see = see + f'@red{exit_name}@normal, '
        
        if exit_count == 0:
            see = see + 'You don\'t see any exits\n'
        else:
            see = see + '' + see_exits
            #see = see + '\n'

        #see = see + f'You can go: @yellow{"@normal, @yellow".join([name for name in exits])}@normal.'
        
        for i in room.actors.values():
            if i == self:
                pass
            else:
                see = see + ''+i.pretty_name() + ' is here'
                if i.status == ActorStatusType.DEAD:
                    see = see + f' is dead here'
                if i.status == ActorStatusType.FIGHTING:
                    see = see + f' is fighting here'
                see = see +'\n'

        



        
        

        if not room.inventory_manager.is_empty():
            see_items = ''
            for i in room.inventory_manager.items.values():
                #see = see + f'{i.pretty_name()} @cyan{i.description}@back' + '\n'
                if i.invisible:
                    continue

                #see_items = see_items + f'   {i.pretty_name()}' + '\n'
                if i.can_pick_up:
                    see_items = see_items + f'{i.pretty_name()} is here' + '\n'
                #else:
                #    see_items = see_items + f'   {i.description}' + '\n'

            if see_items != '':
               see = see + '' + see_items
        
        
        
        


        self.sendLine(see)



    def look_actor(actor):
        sheet = actor.get_character_sheet()

        important_dialog = actor.get_important_dialog(actor_to_compare = self)
        if important_dialog != False:
            sheet = sheet + f'@yellow{important_dialog}@normal'

        self.sendLine(f'You are looking at {sheet}')
        return 

    def look_item(identifier, item):
        output = item.identify(identifier = identifier)
        identifier.sendLine('You look at: ' + output)
        return

    
    list_of_actors =        [actor.name for actor in self.room.actors.values()]
    list_of_directions =    [] #[_exit.direction for _exit in self.room.exits.values()]
    #list_of_items =        [item.name for item in self.inventory_manager.items.values()] + [item.name for item in self.room.inventory_manager.items.values()]
    list_of_items =         [item.name for item in self.room.inventory_manager.items.values()]
    whole_list = list_of_items + list_of_directions + list_of_actors

    look_at = utils.match_word(line, whole_list)
    #self.sendLine(look_at)

    if line == '':
        look_room(self, self.room.id)
        return
    
    if look_at in list_of_actors:
        actor = self.get_actor(line)
        if actor == None:
            return
        look_actor(actor)

    if look_at in list_of_items:
        item = self.get_item(line, search_mode = 'room')
        if item == None:
            return
        look_item(self, item)


def get_nearby_rooms(self, view_range = 1):
    split = ','
    offsets = {
        'north': [ 0  ,  -1 , 0],
        'west':  [ -1 ,  0 , 0],
        'south': [ 0  , 1 , 0],
        'east':  [ 1  ,  0 , 0],
        'up':    [0,0,1],
        'down':  [0,0,-1]
    }
    room_id = self.room.id
    VIEW_RANGE = view_range
    START_LOC = f'{0}{split}{0}{split}{0}'
    start_room = self.protocol.factory.world.rooms[room_id]
    grid = {}
    grid[START_LOC] = room_id

    for _exit in start_room.exits:
        if _exit.direction not in offsets:
            continue
        if _exit.secret:
            continue
        if _exit.item_required != None:
            continue
        if _exit.to_room_id in grid.values():
            continue

        x = 0
        y = 0
        z = 0
        x += offsets[_exit.direction][0] #+ VIEW_RANGE
        y += offsets[_exit.direction][1] #+ VIEW_RANGE
        z += offsets[_exit.direction][2] 

        _loc = f'{x}{split}{y}{split}{z}'

        
        
        if _loc not in grid:
            grid[_loc] = _exit.to_room_id
        



    _grid = {}
    for r in grid:
        _grid[r] = grid[r]
        
    for r in range(0,VIEW_RANGE*1):
        for room_loc in _grid:

            room = self.protocol.factory.world.rooms[grid[room_loc]]
            
            if room.doorway:
                continue

            _x = int(room_loc.split(f'{split}')[0])
            _y = int(room_loc.split(f'{split}')[1])
            _z = int(room_loc.split(f'{split}')[2])

            for _exit in room.exits:
                if _exit.direction not in offsets:
                    continue
                if _exit.secret:
                    continue
                

                x = _x + offsets[_exit.direction][0] 
                y = _y + offsets[_exit.direction][1] 
                z = _z + offsets[_exit.direction][2] 

                # basically, viewrange of 1 will do this
                #
                #         X
                #        XXX
                #       XXXXX
                #        XXX
                #         X
                #
                # so uh dont do that 

                if abs(x) > VIEW_RANGE or abs(y) > VIEW_RANGE or abs(y) > VIEW_RANGE:
                    continue

                _loc = f'{x}{split}{y}{split}{z}'

                if _exit.to_room_id in grid.values():
                    continue
        

                if _loc not in grid:
                    grid[_loc] = _exit.to_room_id

        _grid = {}
        for r in grid:
            _grid[r] = grid[r]

    for r in _grid:
        room = self.room.world.rooms[_grid[r]]
        _grid[r] = room.id

    return _grid

def new_room_look(self):
    
    
    if self.settings_manager.view_room:
        self.command_look('')
    if self.settings_manager.view_map:
        self.command_map('')
    if self.protocol.enabled_gmcp:
        self.update_checker.tick_show_map()