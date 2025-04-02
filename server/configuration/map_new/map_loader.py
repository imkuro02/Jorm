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
                print(file_path)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    all_data['nodes'].update(data['nodes'])
                    all_data['edges'].update(data['edges'])

    for node in all_data['nodes'].values():
        data =      node['data']
        json_data = node['data']['json']

        room_id = data['id']
        room_name = data['name']
        room_desc = 'no desc'
        room_safe = False
        room_instanced = False
        room_npcs = []
        room_items = []

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

                print(all_data['edges'][edge_data['id']])

            if skip_loading:
                continue

        if 'description' in json_data:
            room_desc = json_data['description']

        if 'npcs' in json_data:
            room_npcs= json_data['npcs']

        if 'items' in json_data:
            room_items = json_data['items']

        nodes[room_id] = {
            'id': room_id,
            'name': room_name,
            'description': room_desc,
            'exits': [],
            'can_be_recall_site': room_safe,
            'instanced': room_instanced,
            'npcs': room_npcs,
            'items': room_items
        }


    for edge in all_data['edges'].values():
        edge_data = edge['data']
        if edge_data['source'] in nodes:
            
            new_exit = {
                'from': edge_data['source'], 
                'to_room_id': edge_data['target'], 
                'direction': edge_data['name'],
                'secret': False,
                'blocked': False
            }

            if 'secret' in edge_data['json']:
                new_exit['secret'] = edge_data['json']['secret']
            if 'blocked' in edge_data['json']:
                new_exit['blocked'] = edge_data['json']['secret']

            nodes[edge_data['source']]['exits'].append(new_exit)

    return(nodes)

if __name__ == '__main__':
    print(load_map())