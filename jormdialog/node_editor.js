
const Cy = document.createElement("div");
Cy.id = 'cy';
document.body.appendChild(Cy)


const Editor = document.createElement("div");
Editor.id = 'editor';
document.body.appendChild(Editor)

const FileInput = document.createElement("input");
FileInput.id = 'fileInput';
FileInput.type = 'file';
Editor.appendChild(FileInput)

const BtnUp = document.createElement("button");
BtnUp.onclick = handleFileUpload;
BtnUp.textContent = 'Load';
Editor.appendChild(BtnUp)

const BtnDown = document.createElement("button");
BtnDown.onclick = export_json;
BtnDown.textContent = 'Save';
Editor.appendChild(BtnDown)

const JsonEditor = document.createElement("textarea");
JsonEditor.id = 'json-editor';
Editor.appendChild(JsonEditor)


var selectedNode = null; // Track the currently selected node or edge
var selectedEdge = null;
var copiedData = null;

function NODEsetSelectedNode(node){
    if (selectedNode == node){
        guiNodeSetSelectedNode(node);
    }
    selectedNode = node;
}

function NODEsetSelectedEdge(edge){
    if (selectedEdge == edge){
        guiEdgeSetSelectedEdge(edge);
    }
    selectedEdge = edge;
}

function new_node(data = null, position = null) {
    var node_template = { 
    group: 'nodes',
    position: { x: 0, y: 0 },
    data: { 
        id: generateUUID4(), 
        json: {} 
    }
    };

    if (data !== null) {
    node_template.data = data;
    }

    if (position !== null) {
        //position.x = Math.round(position.x / 16) * 16;
        //position.y = Math.round(position.y / 16) * 16;
        node_template.position = position;
    }

    cy.add(node_template);
}

function new_edge(data = null) {

    console.log(data);
    var edge_template = {
    group: 'edges',
    data: {
        id: generateUUID4(),
        source: null,
        target: null,
        json: {}
    }
    };

    if (data !== null) {
    edge_template.data = data;
    }

    if(data['source'] === data['target']){
    return;
    }

    cy.add(edge_template);
}

var cy = cytoscape({
    container: document.getElementById('cy'),
    elements: [],
    style: [
    {
        selector: 'node',
        style: {
        'shape': 'square',
        'background-color': function(ele) {
            let _empty = Object.keys(ele.data('json')).length === 0 && ele.data('json').constructor === Object;
            if (ele.data('json') && ele.data('json').color) {
            return ele.data('json').color;
            } else if (ele.data('json') && _empty){
            return 'black';
            } else {
            return 'gray';
            }
        },
        'label': function(ele) {
            if (ele.data('json') && ele.data('json').id) { 
            return ele.data('json').id;
            } else {
            return '';
            }
        },
        'border-width': 0,
        'width': '64px',
        'height': '64px',
        'text-halign': 'center',        // Horizontal alignment of the text
        'text-valign': 'center'        // Vertical alignment of the text
        }
    },
    {
        selector: 'node:selected',
        style: {
        'background-color': '#FF6347',
        'border-width': 4,
        'border-color': '#FF4500',
        }
    },
    {
        selector: 'edge',
        style: {
        'width': 4,
        'line-color': function(ele) {
            let _empty = Object.keys(ele.data('json')).length === 0 && ele.data('json').constructor === Object;
            if (ele.data('json') && ele.data('json').color) {
                return ele.data('json').color;
            } else if (ele.data('json') && _empty){
                return 'black';
            } else {
                return '#ccc';
            }
            },
        //'source-arrow-shape': 'circle',
        //'source-arrow-color': 'red',
        'target-arrow-color': '#ccc',
        'target-arrow-shape': 'triangle',
        'target-arrow-color': 'red',
        'label': function(ele) {
            if (ele.data('json') && ele.data('json').direction) { 
            return ele.data('json').direction;
            } else {
            return '';
            }
        },
        
        'font-size': '12px',
        'curve-style': 'bezier',
        'control-point-step-size': 10,
        'control-point-distance': 10
        }
    },
    {
        selector: 'edge:selected',
        style: {
        'line-color': '#FF6347',
        
        'width': 4,
        'target-arrow-color': 'red',
        'target-arrow-shape': 'triangle-tee',
        'control-point-step-size': 10,
        'control-point-distance': 10
        }
    }
    ],
    layout: { name: 'grid' }
});
cy.gridGuide({
    snapToGridDuringDrag: true,
    gridSpacing: 32,
    snapToAlignmentLocationOnRelease: true
  });
function generateUUID4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
    });
}

// Right-click to create new node or delete a node
cy.on('cxttap', function(event) {
    if (!event.target || event.target === cy) {
    // Right-click on empty space or the Cytoscape container itself
    //selectedNode = null;
    NODEsetSelectedNode(null);
    NODEsetSelectedEdge(null);
    document.getElementById('editor').classList.remove('no-pointer-events'); // Enable pointer events

    new_node(data = null, position = event.position);
    document.getElementById('json-editor').value = ''; // Clear editor on empty space click
    } /* else {
    if (event.target.isNode()) {
        var node = event.target;
        node.remove();
        selectedNode = null;
        NODEsetSelectedEdge(null);
        document.getElementById('editor').classList.remove('no-pointer-events'); // Enable pointer events
        document.getElementById('json-editor').value = ''; // Clear editor on node removal
    } else if (event.target.isEdge()) {
        var edge = event.target;
        edge.remove();
        selectedNode = null;
        NODEsetSelectedEdge(null);
        document.getElementById('editor').classList.remove('no-pointer-events'); // Enable pointer events
        document.getElementById('json-editor').value = ''; // Clear editor on edge removal
    }
    } */
});

// Select a node for edge creation
cy.on('tap', 'node', function(event) {
    var node = event.target;
    if (!event.originalEvent.shiftKey) {
        if (node == selectedNode){
            NODEsetSelectedNode(node);
        }
        NODEsetSelectedNode(null);
        NODEsetSelectedEdge(null);
    }
    
    

    // If the Ctrl key is pressed, don't create an edge
    if (event.originalEvent.ctrlKey) {
    return; // Prevent edge creation
    }

    
    if (!selectedNode) {
    // First node is selected
    NODEsetSelectedNode(node);
    NODEsetSelectedEdge(null); // Clear edge selection
    console.log('Node selected: ' + node.id());
    document.getElementById('json-editor').value = JSON.stringify(node.data().json, null, 2); // Display node data
    document.getElementById('json-editor').focus();
    } else {
    console.log('edge');

    let data = {
        'id': generateUUID4(),
        'source': selectedNode.id(), 
        'target': node.id(), 
        'json': {}
    }
    
    cy.nodes(':selected').unselect();
    new_edge(data);
    selectedNode = node; // Reset selection
    }
});

// Select an edge
cy.on('tap', 'edge', function(event) {
    var edge = event.target;
    NODEsetSelectedEdge(edge);
    NODEsetSelectedNode(null); // Clear node selection
    console.log('Edge selected: ' + edge.id());
    document.getElementById('json-editor').value = JSON.stringify(edge.data().json, null, 2); // Display edge data
    document.getElementById('json-editor').focus();
});

// Deselect node or edge on tapping elsewhere
cy.on('tap', function(event) {
    cy.resize();
    if (!event.target || event.target === cy) {
    // Tap happened on empty space (or the Cytoscape container itself)
    if (selectedNode || selectedEdge) {
        NODEsetSelectedNode(null);
        NODEsetSelectedEdge(null);
        document.getElementById('json-editor').value = ''; // Clear editor
        console.log('Deselected');
    }
    }
});

// Save the edited JSON back to the node or edge
document.getElementById('json-editor').addEventListener('input', function() {
const editor = this;  // Reference to the editor element

if (selectedNode) {
try {
    selectedNode.data().json=(JSON.parse(editor.value)); // Update the node's JSON data
    editor.style.backgroundColor = 'white';  // Set background to white if JSON is valid
} catch (e) {
    console.error('Invalid JSON');
    editor.style.backgroundColor = 'lightgray';  // Set background to light gray if JSON is invalid
}
} else if (selectedEdge) {
try {
    selectedEdge.data().json=(JSON.parse(editor.value)); // Update the edge's JSON data
    editor.style.backgroundColor = 'white';  // Set background to white if JSON is valid
} catch (e) {
    console.error('Invalid JSON');
    editor.style.backgroundColor = 'lightgray';  // Set background to light gray if JSON is invalid
}
}
});


// Allow Tab key to insert spaces in the textarea
document.getElementById('json-editor').addEventListener('keydown', function(event) {
    if (event.key === 'Tab') {
    event.preventDefault();
    var cursorPos = this.selectionStart;
    var text = this.value;
    this.value = text.substring(0, cursorPos) + '    ' + text.substring(cursorPos);
    this.selectionStart = this.selectionEnd = cursorPos + 1; // Move cursor after the tab
    }
});

// Create a bunch of nodes for testing
//for (let x = 0; x < 64; x++) {
//  for (let y = 0; y < 64; y++) {
//   new_node(data = null, position = {'x': x * 100, 'y': y * 100});
// }
//}

function download_json(jsonObject) {
    const blob = new Blob([jsonObject], { type: 'application/json' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.download = 'edging_my_nodes.json';
    link.href = url;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function export_json(){
    let j = {'nodes':{}, 'edges':{}};
    cy.nodes().forEach(n => {
        let id = n.data().id;
        j.nodes[id] = {'position': n.position(), 'data': n.data()};
    });
    cy.edges().forEach(e => {
        let id = e.data().id;
        j.edges[id] = {'data': e.data()};
    });
    jsonObject = JSON.stringify(j);
    download_json(jsonObject);
    
}

function handleFileUpload() {
    
    const fileInput = document.getElementById('fileInput');
    console.log(fileInput.files[0])
    // Ensure a file is selected
    if (fileInput.files.length === 0) {
        alert('Please select a file to upload.');
        return;
    }

    const file = fileInput.files[0];  // Get the selected file

    // Check if the file is a JSON file
    if (file.type !== 'application/json') {
        alert('Please upload a JSON file.');
        return;
    }

    // Create a FileReader to read the content of the file
    const reader = new FileReader();
    
    // Set up the onload function to handle when the file is read
    reader.onload = function(event) {
        try {
            // Parse the JSON content
            import_json(event.target.result);
            alert('loaded ');
        } catch (error) {
            alert('Error parsing JSON: ' + error.message);
        }
    };

    reader.readAsText(file);
}

function import_json(input = '{}'){
    let json = JSON.parse(input);
    cy.nodes().remove();
    cy.edges().remove();
    for (let key in json.nodes) {
        //console.log(json.nodes[key]);
        new_node(json.nodes[key].data, json.nodes[key].position);
    };

    for (let key in json.edges) {
        new_edge(data = json.edges[key].data);
        // Code to be executed for each element
    };
    cy.fit();
}

// Handle Ctrl + something keys
document.addEventListener('keydown', function(event) {
    if (event.key === "Delete") { // Check if Ctrl + X is pressed
    let selectedNodes = cy.$(':selected'); // Get all selected nodes

    if (selectedNodes.length > 0) {
        selectedNodes.remove(); // Remove selected nodes
        console.log(selectedNodes.length + ' nodes deleted');
    }
    }
    
});

window.selectedNode = selectedNode;
window.NODEsetSelectedNode = NODEsetSelectedNode;