
from configuration.config import ActorStatusType, Color, get_icon
import utils
import random
random = random.Random()

def command_map(self, line, return_gmcp = False):
    setting_render_walls = False
    if self.room == None:
        return
    room_id = self.room.id
    VIEW_RANGE = 7
    ROOM_AMOUNT = VIEW_RANGE
    PATH_AMOUNT = VIEW_RANGE
    ROOM_WIDTH = 3
    PATH_WIDTH = 2
    MAP_WIDTH = ROOM_WIDTH*VIEW_RANGE + (PATH_WIDTH*(VIEW_RANGE+1)) + 0
    START_LOC = f'{VIEW_RANGE},{VIEW_RANGE}'

    class Art:
        # all
        GROUND =                    f'{Color.MAP_ROOM} '
        GROUND_UNEXPLORED =         f'{Color.MAP_ROOM}?'
        NS =                        ' '#f'{Color.MAP_PATH}|'
        EW =                        ' '#f'{Color.MAP_PATH}-'
        EMPTY =                     f' '
        EMPTYWALL = EMPTY#                f'{Color.MAP_WALL}   '

        DOOR_M =                      f'{Color.MAP_ROOM}^'
        DOOR_L =                      f'{Color.MAP_ROOM}|'
        DOOR_R =                      f'{Color.MAP_ROOM}|'

        QUEST =                     f'{Color.MAP_IMPORTANT}?'

        # middle
        RECALL_SITE =               f'{Color.GOOD}+'
        PLAYER_HERE =               f'{Color.MAP_PLAYER}@'
        #SPECIAL_EXIT =              f'{Color.MAP_NORMAL}?'
        #SPECIAL_EXIT_AND_PLAYER =   f'{Color.MAP_NORMAL}?'
        RECALL_SITE_AND_PLAYER =    f'{Color.MAP_PLAYER}+'

        # right
        STAIRS_DOWN =   f'{Color.MAP_NORMAL}>'
        # left
        STAIRS_UP =     f'{Color.MAP_NORMAL}<'

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

    for _exit in start_room.get_active_exits():
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
            #utils.debug_print(_grid[room_loc])
            if grid[room_loc] == 'PATH':
                continue

            room = self.protocol.factory.world.rooms[grid[room_loc]]


            #if room.doorway:
            #    continue

            _x = int(room_loc.split(',')[0])
            _y = int(room_loc.split(',')[1])

            for _exit in room.get_active_exits():
                if _exit.direction not in offsets:
                    continue
                if _exit.secret:
                    continue
                #if room.get_real_id() not in self.explored_rooms:
                #    continue
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

                if not room.doorway: #and room.get_real_id() in self.explored_rooms:


                    #utils.debug_print(_exit.to_room_id, grid.values())
                    if _exit.to_room_id not in grid.values():
                        if _loc in grid:
                            continue

                        grid[_loc] = _exit.to_room_id


                x += -offsets_path[_exit.direction][1]
                y += -offsets_path[_exit.direction][0]
                _loc = f'{x},{y}'

                #if not room.doorway:
                if _loc not in grid:
                    grid[_loc] = 'PATH'

        _grid = {}
        for r in grid:
            _grid[r] = grid[r]


    #utils.debug_print(grid)
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
                        if all(
                                d not in grid or grid[d] == 'PATH'
                                for d in directions.values()
                            ):
                            cell = Art.EMPTYWALL * PATH_WIDTH
                            #random.seed(self.room.id + loc)
                            #_string = ',.;:-_¨\'"^~`+%&#'+(' '*100)

                            #a = _string[random.randint(0,len(_string)-1)]
                            #b = _string[random.randint(0,len(_string)-1)]
                            #c = _string[random.randint(0,len(_string)-1)]
                            #cell = a+b+c
                            t.add_data('@normal'+cell)
                            walled = True
                            continue


                    cell = ['@red','X','999999999']
                    for d in directions.values():
                        if d in grid:
                            if grid[d] in self.room.world.rooms:
                                wall_data = self.room.world.rooms[grid[d]].get_wall_data()
                                if len(wall_data) == 3:
                                    w_col, w_char, w_prio = wall_data
                                else:
                                    w_col, w_char, w_prio = cell
                                if int(cell[2]) >= int(w_prio):
                                    cell = [w_col, w_char, w_prio]


                    cell = f'{cell[0]}{cell[1]}'


                    if _y % 2 != 0:
                        cell = cell*ROOM_WIDTH
                    else:
                        cell = cell*PATH_WIDTH

                    if not walled:
                        for _dir in directions:
                            if directions[_dir] not in grid:
                                t.add_data(cell)
                                walled = True
                                break


                if not walled:
                    cell = ' '*PATH_WIDTH
                    t.add_data(cell)
                    walled = True
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
                #cell = ' '+Art.GROUND+' '
                _left =  left in grid
                _right = right in grid
                _north = north in grid
                _south = south in grid

                if _left or _right:
                    cell = ' '+Art.NS+' '
                if _north or _south:
                    cell = ''+(Art.EW*PATH_WIDTH)+''


                t.add_data(cell)
                continue

            room = self.protocol.factory.world.rooms[grid[loc]]
            quest_not_started = False
            quest_turn_in = False

            for actor in room.actors.values():
                important_dialog_dict = actor.get_important_dialog(actor_to_compare = self, return_dict = True)
                if important_dialog_dict == False:
                    continue
                if important_dialog_dict['quest_not_started']:
                    quest_not_started = True
                if important_dialog_dict['quest_turn_in']:
                    quest_turn_in = True

            #utils.debug_print(room)
            # left
            cell = ''
            if room.doorway:
                cell += Art.DOOR_L
            elif 'up' in [x.direction for x in room.exits if not x.secret]:
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
            elif room.get_real_id() not in self.explored_rooms:
                cell += Art.GROUND_UNEXPLORED
            elif room.doorway:
                cell += Art.DOOR_M
            elif room.can_be_recall_site:
                cell += Art.RECALL_SITE
            #elif len([ x for x in room.exits if x.direction not in offsets ]) != 0:
            #    cell += Art.SPECIAL_EXIT
            elif quest_not_started or quest_turn_in:
                cell += Art.QUEST # '?'
            else:
                cell += Art.GROUND


            # right
            if room.doorway:
                cell += Art.DOOR_R
            elif 'down' in [x.direction for x in room.exits if not x.secret]:
                cell += Art.STAIRS_DOWN
            else:
                cell += Art.EMPTY



            t.add_data(cell)
            #self.sendLine(t.get_table()+'\n\n\n-----------\n\n\n')



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
        #utils.debug_print(strip_len, left_strip_len)
        if strip_len < left_strip_len:
            left_strip_len = strip_len
            #utils.debug_print(i[x-10:])

    for i in split_output:
        if (i).replace('@normal','').replace(' ','') != '':
            combined_output = combined_output + i[left_strip_len:] + '\n'
    ##############################################################################
    '''
    def pad_lines_to_be_map_width(combined_output):
        lines = combined_output.split('\n')
        first_line_length = len(utils.remove_color(lines[0]))
        #utils.debug_print(first_line_length, f'"{(utils.remove_color(lines[0]))}"')

        if first_line_length < MAP_WIDTH:
            padding_needed = (MAP_WIDTH - first_line_length)
            # Add one space per missing character to **each** line
            import math
            lines = [(f' ' * math.ceil(padding_needed/2)) + line + (f' ' * math.floor(padding_needed/2)) for line in lines]
            #lines += str((math.ceil(padding_needed/2))) + ',.' + str((math.floor(padding_needed/2)))

        return '\n'.join(lines)

    combined_output = t.get_table()#pad_lines_to_be_map_width(t.get_table())

    if not return_gmcp:
        self.sendLine('<Map Start>\n'+combined_output+'<Map End>')
    else:
        return combined_output

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
                see = see + ''+i.pretty_name() + ' is'
                if i.status == ActorStatusType.DEAD:
                    see = see + f' dead' + direction_name + ' from here'
                elif i.status == ActorStatusType.FIGHTING:
                    see = see + f' fighting' + direction_name + ' from here'
                else:
                    see = see + '' + direction_name + ' from here'
                see = see +'\n'
    if see == '':
        self.sendLine('You scan your surroundings but see no one')
        return

    self.sendLine(f'You scan your surroundings and see: \n{see[:-1:]}')

def command_look(self, line, return_gmcp = False, is_glancing = False):
    def look_room(self, room_id, is_glancing = is_glancing):
        room = self.factory.world.rooms[room_id]

        if room_id == self.room.id:
            see = f'You are in {room.pretty_name()}\n'
        else:
            see = f'You look at {room.pretty_name()}\n'
        #see += draw_local_area(self, room_id)
        if not is_glancing:
            see = see + f'{Color.DESCRIPTION}{room.get_description()}{Color.NORMAL}\n'


        exits = self.protocol.factory.world.rooms[room.id].get_active_exits()
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
                    see = see + f' and is dead'
                if i.status == ActorStatusType.FIGHTING:
                    see = see + f' and is fighting'
                see = see +'\n'

        # XD icons
        icons = []
        for i in room.actors.values():
            if type(i).__name__ == 'Player':
                continue
            if len(icons) >= 3:
                continue
            icons.append(get_icon(i.npc_id).split('\n'))

        max_height = 0
        for i in icons:
            if len(i) >= max_height:
                max_height = len(i)

        amount = len(icons)
        if amount != 0:
            t = utils.Table(amount)
            #column = 0
            row = 0
            for row in range(0,max_height):
                for column in range(0,amount):
                    try:
                        t.add_data(icons[column][row])

                    except Exception as e:
                        pass



            see = see +'\n'+t.get_table()









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





        if not return_gmcp:
            self.sendLine(see)
        else:
            return see
        #self.sendLine(see)



    def look_actor(actor, is_glancing = False):
        sheet = actor.get_character_sheet(sheet_getter=self, is_glancing = is_glancing)
        self.sendLine(f'You are looking at {sheet}')
        return

    def look_item(identifier, item, is_glancing = False):
        output = item.identify(identifier = identifier, is_glancing = is_glancing)
        identifier.sendLine('You look at: ' + output)
        return

    if self.room == None:
        return

    list_of_actors =        [actor.name for actor in self.room.actors.values()]
    list_of_directions =    [] #[_exit.direction for _exit in self.room.exits.values()]
    #list_of_items =        [item.name for item in self.inventory_manager.items.values()] + [item.name for item in self.room.inventory_manager.items.values()]
    list_of_items =         [item.name for item in self.room.inventory_manager.items.values()]
    whole_list = list_of_items + list_of_directions + list_of_actors

    look_at = utils.match_word(line, whole_list)
    #print(line,look_at,whole_list)
    #self.sendLine(look_at)

    if line == '':
        see = look_room(self, self.room.id)
        return see

    if look_at in list_of_actors:
        actor = self.get_actor(line)
        if actor == None:
            return
        look_actor(actor, is_glancing = is_glancing)

    if look_at in list_of_items:
        item = self.get_item(line, search_mode = 'room')
        if item == None:
            return
        look_item(self, item)


def command_glance(self, line):
    return self.command_look(line, is_glancing = True)


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

    for _exit in start_room.get_active_exits():
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

            for _exit in room.get_active_exits():
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
        self.update_checker.tick()
    if self.protocol.enabled_gmcp:

        self.update_checker.tick()
