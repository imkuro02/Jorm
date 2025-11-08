import json
import os
# load map.json into trizbort.io and configure it there 
import random
import uuid
def load_map():
    # Path to the JSON file
    file_path = "configuration/map/map.json"
    data = ''
    # Open and read the JSON file
    #with open(file_path, "r") as file:
    #    data = json.load(file)

    rooms = {}
    connectors = {}
    MAP_DIRECTORY = 'configuration/map/'
    for root, dirs, files in os.walk(MAP_DIRECTORY):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    file_path = file_path.replace('configuration/map/','').replace('.json','')
                    
                    objects = {}
                    elems = data ['elements']
                    for i in elems:
                        objects[i['id']] = i

                    for i in objects.values():
                        if i['_type'] == 'Room':
                            #if '#' in i['_subtitle']:
                            #    continue

                            ROOM_ID = file_path+'#'+i['_subtitle']
                            #utils.debug_print(i['_subtitle'] == 'loading',i['_subtitle'] )
                            
                            # skip if this room has already been loaded
                            if ROOM_ID in rooms:
                                continue

                            rooms[ROOM_ID] = {}
                            room = rooms[ROOM_ID]

                            room['id'] = ROOM_ID
                            room['pos'] = {'x':i['_x']*2,'y':i['_y']*2}
                            room['name'] = i['_name']
                            room['description'] = i['_description']
                            room['exits'] = {}
                            room['secret_exits'] = {}
                            room['blocked_exits'] = []
                            room['can_be_recall_site'] = False
                            room['instanced'] = False

                            if '_fillColor' in i:
                                #utils.debug_print(i['_subtitle'], i['_fillColor'])
                                room['can_be_recall_site'] = i['_fillColor'] == 'rgb(213, 229, 214)' or i['_fillColor'] == '#D5E5D6'
                                room['instanced'] = i['_fillColor'] == '#F6D5D5'
                                #utils.debug_print(room['instanced'])

                            room['enemies'] = []
                            for obj in i['objects']:
                                obj_name = obj['_name']
                                if 'enemy:' in obj_name:
                                    enemies = obj_name.replace('enemy:','').split(', ')
                                    #picked_enemy = random.choice(enemies).strip()
                                    room['enemies'].append(enemies)

                            room['items'] = []
                            for obj in i['objects']:
                                obj_name = obj['_name']
                                if 'item:' in obj_name:
                                    items = obj_name.replace('item:','').split(', ')
                                    #item_picked = random.choice(items).strip()
                                    room['items'].append(items)

                            room['npcs'] = []
                            for obj in i['objects']:
                                obj_name = obj['_name']
                                if 'npc:' in obj_name:
                                    npcs = obj_name.replace('npc:','').split(', ')
                                    #npc_picked = random.choice(npcs).strip()
                                    room['npcs'].append(npcs)
                                
                            

                            # work on dis yknow
                            #room['instanced'] = False

                            

                        if i['_type'] == 'Connector':

                            from_id = objects[i['_dockEnd']]['_subtitle']
                            if '#' not in from_id:
                                from_id= file_path+'#'+from_id

                            to_id = objects[i['_dockStart']]['_subtitle']
                            if '#' not in to_id:
                                to_id = file_path+'#'+to_id

                            conn = {
                                    'from':{
                                        'direction': i['_endLabel'],
                                        'room_id': from_id
                                    },
                                    'to': {
                                        'direction': i['_startLabel'],
                                        'room_id': to_id
                                    }
                                }
                            
                            connectors[uuid.uuid4()] = conn
                            
    for conn in connectors.values():
        if conn['from']['direction'] != '':
            rooms[conn['from']['room_id']]['exits'][conn['from']['direction']] = conn['to']['room_id']

        if conn['to']['direction'] != '':
            rooms[conn['to']['room_id']]['exits'][conn['to']['direction']] = conn['from']['room_id']
        
        '''
        if conn['from']['direction'] != '':
            if 'secret:' not in conn['from']['direction']:
                if 'blocked:' in conn['from']['direction']:
                    rooms[conn['from']['room_id']]['exits'][conn['from']['direction'].replace('blocked:','')] = conn['to']['room_id']
                    rooms[conn['from']['room_id']]['blocked_exits'].append(conn['from']['direction'].replace('blocked:',''))
                else:
                    rooms[conn['from']['room_id']]['exits'][conn['from']['direction']] = conn['to']['room_id']
            else:   
                rooms[conn['from']['room_id']]['secret_exits'][conn['from']['direction'].replace('secret:','')] = conn['to']['room_id']

        if conn['to']['direction'] != '':
            if 'secret:' not in conn['to']['direction']:
                if 'blocked:' in conn['to']['direction']:
                    rooms[conn['to']['room_id']]['exits'][conn['to']['direction'].replace('blocked:','')] = conn['from']['room_id']
                    rooms[conn['to']['room_id']]['blocked_exits'].append(conn['to']['direction'].replace('blocked:',''))
                else:
                    rooms[conn['to']['room_id']]['exits'][conn['to']['direction']] = conn['from']['room_id']
            else:
                rooms[conn['to']['room_id']]['secret_exits'][conn['to']['direction'].replace('secret:','')] = conn['from']['room_id']
        '''

    #for r in rooms.values():
    #    if 'tutorial' not in r['id']:
    #        continue 
        #utils.debug_print(r)

    from uuid import uuid4   
    _rooms = {}
    my_dict = {'nodes':{},'edges':{}}

    for r in rooms.values():
        #{"nodes":{"6e904f3a-11d3-4871-889e-bb314cb2a813":{"
        #position":{"x":240,"y":304},"data":{"id":"6e904f3a-11d3-4871-889e-bb314cb2a813","json":{}}}}
        #,"edges":{}}
        PEEID = r['id']#str(uuid4())
        #utils.debug_print(PEEID)
        col = 'red'

        if 'ellinia#' in PEEID:
            col = 'green'
        if 'overworld#' in PEEID:
            col = 'gray'
        if 'tutorial#' in PEEID:
            col = 'yellow'

        #utils.debug_print(r)

        

        # _spawner = '\n'.join([', '.join([r['items']]])+', '.join([r['npcs']]))+'\n'.join(', '.join([r['enemies']]))
        #utils.debug_print(r['items'])

        _i = r['items']  
        _e = r['enemies']    
        _n = r['npcs'] 

        combinator = ''
        for x in _i+_e+_n:
            for y in x:
                combinator += f'{y}, '
            combinator += '\n'

        combinator = combinator[::-1].replace(', \n'[::-1], '', 1)[::-1]

        

        _spawner = combinator
        my_dict['nodes'] = {**my_dict['nodes'], **{PEEID:{'position':r['pos'],"data":{"id":PEEID,"json":{
            'name':r['name'],
            'description':r['description'],
            'color': col,
            'spawner': str(_spawner)
            
        }}}}}

        for ex in r['exits']:
            PEEID = str(uuid4())
            direction = ex
            secret = False
            blocked = False
            if 'secret:' in direction:
                direction = direction.replace('secret:','')
                secret = True
            if 'blocked:' in direction:
                direction = direction.replace('blocked:','')
                blocked = True
            target = r['exits'][ex]
            source = r['id']
            edge = {PEEID:{"data":{'id':PEEID, 'target':target, 'source':source, 'json':{ 
                'direction':direction,
                'secret': secret,
                'blocked': blocked
            }}}}
            
            my_dict['edges'] = {**my_dict['edges'], **edge}


        

    for i in my_dict['nodes'].values():
        utils.debug_print(i['data']['json']['spawner'])

    with open('data.json', 'w') as json_file:
        json.dump(my_dict, json_file, indent=4)
                    
    #return(my_dict)

if __name__ == '__main__':
    w = load_map()
    utils.debug_print(w)