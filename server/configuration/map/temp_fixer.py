'''
all this script does is fix ids for the map loader so everything is of uuid4

'''

import json
import uuid
# Replace 'data.json' with the path to your JSON file
filename = 'map.json'

# Open and load the JSON file
with open(filename, 'r') as file:
    data = json.load(file)
    new_data = {}
    for i in data['nodes']:
        new_id = str(uuid.uuid4())
        new_data[new_id] = data['nodes'][i]
        new_data[new_id]['data']['id'] = new_id
        for e in data['edges']:
            if i == data['edges'][e]['data']['target']:
                data['edges'][e]['data']['target'] = data['edges'][e]['data']['target'].replace(i,new_id)
            if i == data['edges'][e]['data']['source']: 
                data['edges'][e]['data']['source'] = data['edges'][e]['data']['source'].replace(i,new_id)
            
        

    data['nodes'] = new_data
    #for i in data['nodes'].values():
        #utils.debug_print(i)
    #for i in data['edges'].values():
        #utils.debug_print(i)

    with open('output.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)  # `indent=4` makes it pretty-utils.debug_printed


# utils.debug_print the loaded data
#utils.debug_print(data)