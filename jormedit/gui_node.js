
function label(text){
    const label = document.createElement("label");
    label.textContent = text;
    return label;
}

function br(){
    const br = document.createElement('br');
    return br;
}

const nodeFormContainer = document.createElement("div");

//document.body.appendChild(formContainer)
container = document.getElementById('containers');
container.appendChild(nodeFormContainer)
nodeFormContainer.id = 'node-form-container';

//const formContainer = document.getElementById("form-container");
nodeFormContainer.innerHTML = '';

const nodeGroup = document.createElement("div");
nodeGroup.classList.add("input-nodeGroup");

const nodeSaveBtn = document.createElement("button");
nodeSaveBtn.textContent = 'Save';
nodeSaveBtn.onclick = save_json;
nodeGroup.appendChild(nodeSaveBtn);
nodeGroup.appendChild(br());

nodeGroup.appendChild(label('id'));
nodeGroup.appendChild(br());
const nodeIdInput = document.createElement("input");
nodeGroup.appendChild(nodeIdInput);
nodeGroup.appendChild(br());

const nodeSaveIdInput = document.createElement("input");
nodeSaveIdInput.type = 'checkbox';
nodeGroup.appendChild(nodeSaveIdInput);
nodeGroup.appendChild(label('save_id'));
nodeGroup.appendChild(br());



nodeGroup.appendChild(label('label'));
nodeGroup.appendChild(br());
const nodeLabelInput = document.createElement("input");
nodeGroup.appendChild(nodeLabelInput);
nodeGroup.appendChild(br());

const nodeSaveLabelInput = document.createElement("input");
nodeSaveLabelInput.type = 'checkbox';
nodeGroup.appendChild(nodeSaveLabelInput);
nodeGroup.appendChild(label('save_label'));
nodeGroup.appendChild(br());




nodeGroup.appendChild(label('color'));
nodeGroup.appendChild(br());
const nodeColorInput = document.createElement("input");
nodeGroup.appendChild(nodeColorInput);
nodeGroup.appendChild(br());

const nodeSaveColorInput = document.createElement("input");
nodeSaveColorInput.type = 'checkbox';
nodeGroup.appendChild(nodeSaveColorInput);
nodeGroup.appendChild(label('save_color'));
nodeGroup.appendChild(br());




nodeGroup.appendChild(label('name'));
nodeGroup.appendChild(br());
const nodeNameInput = document.createElement("input");
nodeGroup.appendChild(nodeNameInput);
nodeGroup.appendChild(br());

const nodeSaveNameInput = document.createElement("input");
nodeSaveNameInput.type = 'checkbox';
nodeGroup.appendChild(nodeSaveNameInput);
nodeGroup.appendChild(label('save_name'));
nodeGroup.appendChild(br());




nodeGroup.appendChild(label('desc'));
nodeGroup.appendChild(br());
const nodeDescInput = document.createElement("textarea");
nodeGroup.appendChild(nodeDescInput);
nodeGroup.appendChild(br());

const nodeSaveDescInput = document.createElement("input");
nodeSaveDescInput.type = 'checkbox';
nodeGroup.appendChild(nodeSaveDescInput);
nodeGroup.appendChild(label('save_desc'));
nodeGroup.appendChild(br());




const nodeCanBeRecallSiteInput = document.createElement("input");
nodeCanBeRecallSiteInput.type = 'checkbox';
nodeGroup.appendChild(nodeCanBeRecallSiteInput);
nodeGroup.appendChild(label('safe'));
nodeGroup.appendChild(br());

const nodeSaveSafeInput = document.createElement("input");
nodeSaveSafeInput.type = 'checkbox';
nodeGroup.appendChild(nodeSaveSafeInput);
nodeGroup.appendChild(label('save_safe'));
nodeGroup.appendChild(br());




const nodeInstancedInput = document.createElement("input");
nodeInstancedInput.type = 'checkbox';
nodeGroup.appendChild(nodeInstancedInput);
nodeGroup.appendChild(label('instanced'));
nodeGroup.appendChild(br());

const nodeSaveInstancedInput = document.createElement("input");
nodeSaveInstancedInput.type = 'checkbox';
nodeGroup.appendChild(nodeSaveInstancedInput);
nodeGroup.appendChild(label('save_instanced'));
nodeGroup.appendChild(br());




const nodeDoorwayInput = document.createElement("input");
nodeDoorwayInput.type = 'checkbox';
nodeGroup.appendChild(nodeDoorwayInput);
nodeGroup.appendChild(label('doorway'));
nodeGroup.appendChild(br());

const nodeSaveDoorwayInput = document.createElement("input");
nodeSaveDoorwayInput.type = 'checkbox';
nodeGroup.appendChild(nodeSaveDoorwayInput);
nodeGroup.appendChild(label('save_doorway'));
nodeGroup.appendChild(br());





nodeGroup.appendChild(label('spawner syntax'));
nodeGroup.appendChild(br());
const nodeSpawnGroupInput = document.createElement("textarea");
nodeGroup.appendChild(nodeSpawnGroupInput);
nodeGroup.appendChild(br());

const nodeSaveSpawnGroupInput = document.createElement("input");
nodeSaveSpawnGroupInput.type = 'checkbox';
nodeGroup.appendChild(nodeSaveSpawnGroupInput);
nodeGroup.appendChild(label('save_spawngroup'));
nodeGroup.appendChild(br());




nodeFormContainer.appendChild(nodeGroup);

function guiNodeSetSelectedNode(node){
    if(node !== null){
        data = node.data().json;

        if (typeof data['id'] !== "undefined"){
            nodeIdInput.value = data['id'];
        } else {
            nodeIdInput.value = '';
        }

        if (typeof data['label'] !== "undefined"){
            nodeLabelInput.value = data['label'];
        } else {
            nodeLabelInput.value = '';
        }

        if (typeof data['color'] !== "undefined"){
            nodeColorInput.value = data['color'];
        } else {
            nodeColorInput.value = '';
        }

        if (typeof data['name'] !== "undefined"){
            nodeNameInput.value = data['name'];
        } else {
            nodeNameInput.value = '';
        }

        if (typeof data['description'] !== "undefined"){
            nodeDescInput.value = data['description'];
        } else {
            nodeDescInput.value = '';
        }

        if (typeof data['can_be_recall_site'] !== "undefined"){
            nodeCanBeRecallSiteInput.checked = data['can_be_recall_site'];
        } else {
            nodeCanBeRecallSiteInput.checked = false;
        }

        if (typeof data['instanced'] !== "undefined"){
            nodeInstancedInput.checked = data['instanced'];
        } else {
            nodeInstancedInput.checked = false;
        }

        if (typeof data['doorway'] !== "undefined"){
            nodeDoorwayInput.checked = data['doorway'];
        } else {
            nodeDoorwayInput.checked = false;
        }

        if (typeof data['spawner'] !== "undefined"){
            nodeSpawnGroupInput.value = data['spawner'];
        } else {
            nodeSpawnGroupInput.value = '';
        }
    }
}
  
function save_json() {
    const data = {
        'id': nodeIdInput.value,
        'label': nodeLabelInput.value,
        'color': nodeColorInput.value,
        'name': nodeNameInput.value,
        'description': nodeDescInput.value,
        'can_be_recall_site': nodeCanBeRecallSiteInput.checked,
        'instanced': nodeInstancedInput.checked,
        'doorway': nodeDoorwayInput.checked,
        'spawner': nodeSpawnGroupInput.value

    };

    if (!nodeSaveIdInput.checked){delete data['id'];}
    if (!nodeSaveLabelInput.checked){delete data['label'];}
    if (!nodeSaveColorInput.checked){delete data['color'];}
    if (!nodeSaveNameInput.checked){delete data['name'];}
    if (!nodeSaveDescInput.checked){delete data['description'];}
    if (!nodeSaveSafeInput.checked){delete data['safe'];}
    if (!nodeSaveInstancedInput.checked){delete data['instanced'];}
    if (!nodeSaveDoorwayInput.checked){delete data['doorway'];}
    if (!nodeSaveSpawnGroupInput.checked){delete data['spawner'];}


    /*
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            if (data[key] === false || data[key] === '' || (typeof data[key] === "undefined")) {
                delete data[key];
            }
        }
    }
    */

    

    //console.log(JSON.stringify(data, null, 2));

    const textToCopy = JSON.stringify(data, null, 2);
    
    //navigator.clipboard.writeText(textToCopy)
    //    .then(() => {
    //        //alert("Text copied to clipboard!");
    //    })
    //    .catch(err => {
    //        console.error("Failed to copy text: ", err);
    //    });

    cy.nodes(':selected').forEach(function(node) {
        const nodeData = node.data().json;
        
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                nodeData[key] = data[key];
            }
        }
    
        node.data(nodeData);
    });
    //if (window.selectedNode!=null){
    //    window.selectedNode.data().json = data
    //} 
}

window.guiNodeSetSelectedNode = guiNodeSetSelectedNode;