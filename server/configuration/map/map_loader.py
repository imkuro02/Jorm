import json
import os
# load map.json into trizbort.io and configure it there 
import random
import uuid
def load_map():
    # Path to the JSON file
    #file_path = "configuration/map/map.json"
    #data = ''
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
                print(file_path)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    file_path = file_path.replace('configuration/map/','').replace('.json','')
                    
                    objects = {}
                    elems = data ['elements']
                    for i in elems:
                        objects[i['id']] = i

                    for i in objects.values():
                        if i['_type'] == 'Room':
                            if '#' in i['_subtitle']:
                                continue

                            ROOM_ID = file_path+'#'+i['_subtitle']
                            #print(i['_subtitle'] == 'loading',i['_subtitle'] )
                            
                            # skip if this room has already been loaded
                            if ROOM_ID in rooms:
                                continue

                            rooms[ROOM_ID] = {}
                            room = rooms[ROOM_ID]

                            room['id'] = ROOM_ID
                            room['name'] = i['_name']
                            room['description'] = i['_description']
                            room['exits'] = {}
                            room['secret_exits'] = {}
                            room['can_be_recall_site'] = False
                            room['instanced'] = False

                            if '_fillColor' in i:
                                #print(i['_subtitle'], i['_fillColor'])
                                room['can_be_recall_site'] = i['_fillColor'] == 'rgb(213, 229, 214)' or i['_fillColor'] == '#D5E5D6'
                                room['instanced'] = i['_fillColor'] == '#F6D5D5'
                                #print(room['instanced'])

                            room['enemies'] = []
                            for obj in i['objects']:
                                obj_name = obj['_name']
                                if 'enemy:' in obj_name:
                                    enemies = obj_name.replace('enemy:','').split(',')
                                    picked_enemy = random.choice(enemies).strip()
                                    room['enemies'].append(picked_enemy)

                            room['items'] = []
                            for obj in i['objects']:
                                obj_name = obj['_name']
                                if 'item:' in obj_name:
                                    items = obj_name.replace('item:','').split(',')
                                    item_picked = random.choice(items).strip()
                                    room['items'].append(item_picked)

                            room['npcs'] = []
                            for obj in i['objects']:
                                obj_name = obj['_name']
                                if 'npc:' in obj_name:
                                    npcs = obj_name.replace('npc:','').split(',')
                                    npc_picked = random.choice(npcs).strip()
                                    room['npcs'].append(npc_picked)
                                
                            

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
        #if 'tutorial' in conn['from']['room_id'] or 'tutorial'  in conn['from']['room_id']:
            #print(conn)

        if conn['from']['direction'] != '':
            if 'secret:' not in conn['from']['direction']:
                rooms[conn['from']['room_id']]['exits'][conn['from']['direction']] = conn['to']['room_id']
            else:
                rooms[conn['from']['room_id']]['secret_exits'][conn['from']['direction'].replace('secret:','')] = conn['to']['room_id']

        if conn['to']['direction'] != '':
            if 'secret:' not in conn['to']['direction']:
                rooms[conn['to']['room_id']]['exits'][conn['to']['direction']] = conn['from']['room_id']
            else:
                rooms[conn['to']['room_id']]['secret_exits'][conn['to']['direction'].replace('secret:','')] = conn['from']['room_id']

    #for r in rooms.values():
    #    if 'tutorial' not in r['id']:
    #        continue 
        #print(r)
            
                    
    return(rooms)

if __name__ == '__main__':
    w = load_map()
    #print(w)