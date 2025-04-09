
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



nodeGroup.appendChild(label('Script'));
nodeGroup.appendChild(br());
const nodeScriptInput = document.createElement("textarea");
nodeGroup.appendChild(nodeScriptInput);
nodeGroup.appendChild(br());

nodeGroup.appendChild(label('Show If'));
nodeGroup.appendChild(br());
const nodeShowIfInput = document.createElement("textarea");
nodeGroup.appendChild(nodeShowIfInput);
nodeGroup.appendChild(br());

nodeGroup.appendChild(label('Execute'));
nodeGroup.appendChild(br());
const nodeExecuteInput = document.createElement("textarea");
nodeGroup.appendChild(nodeExecuteInput);
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

        if (typeof data['show_if'] !== "undefined"){
            nodeShowIfInput.value = data['show_if'];
        } else {
            nodeShowIfInput.value = '';
        }

        if (typeof data['script'] !== "undefined"){
            nodeScriptInput.value = data['script'];
        } else {
            nodeScriptInput.value = '';
        }

        if (typeof data['execute'] !== "undefined"){
            nodeExecuteInput.value = data['execute'];
        } else {
            nodeExecuteInput.value = '';
        }

    }
}
  
function save_json() {
    const data = {
        'id': nodeIdInput.value,
        'label': nodeLabelInput.value,
        'color': nodeColorInput.value,
        'execute': nodeExecuteInput.value,
        'script':  nodeScriptInput.value,
        'show_if':  nodeShowIfInput.value
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

    cy.nodes(':selected').forEach(function(node) {
        // Your code to operate on each selected node
        node.data().json = data
    });
    //if (window.selectedNode!=null){
    //    window.selectedNode.data().json = data
    //} 
}

window.guiNodeSetSelectedNode = guiNodeSetSelectedNode;