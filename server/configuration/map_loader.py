import json

# load map.json into trizbort.io and configure it there 

def load_map():
    # Path to the JSON file
    file_path = "configuration/map.json"
    data = ''
    # Open and read the JSON file
    with open(file_path, "r") as file:
        data = json.load(file)

    objects = {}
    elems = data['elements']
    for i in elems:
        objects[i['id']] = i

    rooms = {}
    connectors = {}
    for i in objects.values():
        if i['_type'] == 'Room':
            rooms[i['_subtitle']] = {}
            room = rooms[i['_subtitle']]

            room['id'] = i['_subtitle']
            room['name'] = i['_name']
            room['description'] = i['_description']
            room['exits'] = {}
            room['secret_exits'] = {}

            room['enemies'] = []
            for obj in i['objects']:
                obj_name = obj['_name']
                if 'enemy:' in obj_name:
                    room['enemies'].append(obj['_name'].replace('enemy:',''))
            

            # work on dis yknow
            #room['instanced'] = False

            

        if i['_type'] == 'Connector':
            connectors[i['id']] = i

    for i in connectors.values():
        
        #if i['_dockStart'] == i['_dockEnd']:
        #    print('THIS CONNECTOR HAS NO START NOR END', i)
        
        e1 = objects[i['_dockStart']]['_subtitle']
        e2 = objects[i['_dockEnd']]['_subtitle']
        
        #print(i['_startLabel'], '->' ,objects[i['_dockStart']]['_subtitle'])
        #print(i['_endLabel'], '->' ,objects[i['_dockEnd']]['_subtitle'])

        room_from_exit = i['_startLabel']
        room_to_exit = i['_endLabel']
        room_from_id = objects[i['_dockStart']]['_subtitle']
        room_to_id = objects[i['_dockEnd']]['_subtitle']

        #print(room_from_id, room_from_exit)

        if room_to_exit != '':
            if 'secret:' in room_to_exit:
                room_to_exit = room_to_exit.split(':')[1]
                rooms[room_to_id]['secret_exits'][room_to_exit] = room_from_id
            else:
                rooms[room_to_id]['exits'][room_to_exit] = room_from_id

        if room_from_exit != '':
            if 'secret:' in room_from_exit:
                room_from_exit = room_from_exit.split(':')[1]
                rooms[room_from_id]['secret_exits'][room_from_exit] = room_to_id
            else:
                rooms[room_from_id]['exits'][room_from_exit] = room_to_id

        #if i['_startLabel'] != '': 
        #   rooms[e1]['exits'][i['_startLabel']] = e2
        #if i['_endLabel'] != '': 
        #   rooms[e2]['exits'][i['_endLabel']] = e1

        

        
        

    #for i in rooms.values():
    #    print(i['name'],i['exits'])

    return(rooms)

if __name__ == '__main__':
    w = load_map()
    #print(w)
