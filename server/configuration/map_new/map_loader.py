import json
import os
def load_map():
    nodes = {}
    edges = {}
    all_data = {'nodes':{},'edges':{}}
    
    MAP_DIRECTORY = 'configuration/map_new/'
    for root, dirs, files in os.walk(MAP_DIRECTORY):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    all_data['nodes'].update(data['nodes'])
                    all_data['edges'].update(data['edges'])

    for node in all_data['nodes'].values():
        data =      node['data']
        json_data = node['data']['json']

        room_id = data['id']
        room_name = 'somewhere'
        room_desc = 'There is nothing noteworthy here'
        room_safe = False
        room_instanced = False
        room_spawner = []

        if 'id' in json_data:
            new_id = json_data['id']

            skip_loading = False
            if '!' == new_id[0]:
                new_id = new_id.replace('!','')
                skip_loading = True

            room_id = new_id
            for edge in all_data['edges'].values():
                edge_data = edge['data']
                if edge_data['source'] == data['id']:
                    all_data['edges'][edge_data['id']]['data']['source'] = new_id
                if edge_data['target'] == data['id']:
                    all_data['edges'][edge_data['id']]['data']['target'] = new_id

            if skip_loading:
                continue

        if 'name' in json_data:
            room_name = json_data['name']

        if 'description' in json_data:
            if type(json_data['description']) == str:
                room_desc = json_data['description']
            if type(json_data['description']) == list:
                room_desc = '\n'.join(json_data['description'])

        if 'instanced' in json_data:
            room_instanced = json_data['instanced']

        if 'can_be_recall_site' in json_data:
            room_safe = json_data['can_be_recall_site']

        if 'spawner' in json_data:
            for i in [json_data['spawner'].split('\n')]:
                for x in i:
                    room_spawner.append(x.split(', '))

        #print(room_spawner)
        nodes[room_id] = {
            'id': room_id,
            'name': room_name,
            'description': room_desc,
            'exits': [],
            'can_be_recall_site': room_safe,
            'instanced': room_instanced,
            'spawner': room_spawner,
            #'items': room_items
        }


    for edge in all_data['edges'].values():
        edge_data = edge['data']
        json_data = edge_data['json']

        if edge_data['source'] in nodes:
            
            new_exit = {
                'from': edge_data['source'], 
                'to_room_id': edge_data['target'], 
                'direction': 'edge.data.json has no direction',
                'secret': False,
                'blocked': False
            }


            if 'secret' in json_data:
                new_exit['secret'] = json_data['secret']
            if 'blocked' in json_data:
                new_exit['blocked'] = json_data['blocked']
            if 'direction' in json_data:
                new_exit['direction'] = json_data['direction']

            nodes[edge_data['source']]['exits'].append(new_exit)

    return(nodes)

if __name__ == '__main__':
    print(load_map())