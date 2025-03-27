
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
            if _exit.direction not in offsets:
                continue
            if _exit.secret:
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
            
        for r in range(0,1):
            for room_loc in _grid:
                if grid[room_loc] == 'PATH':
                    continue
                room = self.protocol.factory.world.rooms[grid[room_loc]]
                _x = int(room_loc.split(',')[0])
                _y = int(room_loc.split(',')[1])
                for _exit in room.exits:
                    if _exit.direction not in offsets:
                        continue
                    if _exit.secret:
                        continue
                    # do not duplicate if room leads to one that already is placed
                    if _exit.to_room_id in grid.values():
                        continue
                    x = _x
                    y = _y
                    x += offsets[_exit.direction][1] 
                    y += offsets[_exit.direction][0] 
                    _loc = f'{x},{y}'

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
                if 'up' in [ x.direction for x in room.exits ]:
                    cell += Art.STAIRS_UP
                else:
                    cell += Art.EMPTY
                    
                # mid
                if 100 == 10:
                    pass
                elif room.can_be_recall_site and loc == START_LOC:
                    cell += Art.RECALL_SITE_AND_PLAYER
                elif len([ x for x in room.exits if x.direction not in offsets ]) != 0 and loc == START_LOC: #set(offsets.keys()) - set(grid[loc].exits.keys()):
                    cell += Art.SPECIAL_EXIT_AND_PLAYER
                elif loc == START_LOC:
                    cell += Art.PLAYER_HERE
                elif room.can_be_recall_site:
                    cell += Art.RECALL_SITE
                elif len([ x for x in room.exits if x.direction not in offsets ]) != 0:
                    cell += Art.SPECIAL_EXIT
                else:
                    cell += Art.GROUND

                # right
                if 'down' in [ x.direction for x in room.exits ]:
                    cell += Art.STAIRS_DOWN
                else:
                    cell += Art.EMPTY

                if grid[loc] == 'PATH':
                    cell = ' '+Art.GROUND+' '
                    t.add_data(cell)
                    continue

                t.add_data(cell)

                
                

        output = t.get_table()
        #output = str(grid)

            
            

        return output
        #self.sendLine(output)


    def look_room(self, room_id):
        room = self.factory.world.rooms[room_id]

        if room_id == self.room.id:
            see = f'You are in @yellow{room.name}@normal\n'
        else:
            see = f'You look at @yellow{room.name}@normal\n'
        see += draw_local_area(self, room_id)
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

