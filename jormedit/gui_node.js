
function label(text){
    const label = document.createElement("label");
    label.textContent = text;
    return label;
}

function br(){
    const br = document.createElement('br');
    return br;
}

const formContainer = document.createElement("div");
document.body.appendChild(formContainer)
formContainer.id = 'form-container';

//const formContainer = document.getElementById("form-container");
formContainer.innerHTML = '';

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

nodeGroup.appendChild(label('label'));
nodeGroup.appendChild(br());
const nodeLabelInput = document.createElement("input");
nodeGroup.appendChild(nodeLabelInput);
nodeGroup.appendChild(br());

nodeGroup.appendChild(label('color'));
nodeGroup.appendChild(br());
const nodeColorInput = document.createElement("input");
nodeGroup.appendChild(nodeColorInput);
nodeGroup.appendChild(br());

nodeGroup.appendChild(label('name'));
nodeGroup.appendChild(br());
const nodeNameInput = document.createElement("input");
nodeGroup.appendChild(nodeNameInput);
nodeGroup.appendChild(br());

nodeGroup.appendChild(label('desc'));
nodeGroup.appendChild(br());
const nodeDescInput = document.createElement("textarea");
nodeGroup.appendChild(nodeDescInput);
nodeGroup.appendChild(br());

const nodeCanBeRecallSiteInput = document.createElement("input");
nodeCanBeRecallSiteInput.type = 'checkbox';
nodeGroup.appendChild(nodeCanBeRecallSiteInput);
nodeGroup.appendChild(label('safe'));
nodeGroup.appendChild(br());

const nodeInstancedInput = document.createElement("input");
nodeInstancedInput.type = 'checkbox';
nodeGroup.appendChild(nodeInstancedInput);
nodeGroup.appendChild(label('instanced'));
nodeGroup.appendChild(br());

nodeGroup.appendChild(label('spawner syntax'));
nodeGroup.appendChild(br());
const nodeSpawnGroupInput = document.createElement("textarea");
nodeGroup.appendChild(nodeSpawnGroupInput);
nodeGroup.appendChild(br());

formContainer.appendChild(nodeGroup);

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
        'spawner': nodeSpawnGroupInput.value
    };

    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            if (data[key] === false || data[key] === '' || (typeof data[key] === "undefined")) {
                delete data[key];
            }
        }
    }
    //console.log(JSON.stringify(data, null, 2));

    const textToCopy = JSON.stringify(data, null, 2);
    
    //navigator.clipboard.writeText(textToCopy)
    //    .then(() => {
    //        //alert("Text copied to clipboard!");
    //    })
    //    .catch(err => {
    //        console.error("Failed to copy text: ", err);
    //    });

    
    if (window.selectedNode!=null){
        window.selectedNode.data().json = data
    } 
}

window.guiNodeSetSelectedNode = guiNodeSetSelectedNode;