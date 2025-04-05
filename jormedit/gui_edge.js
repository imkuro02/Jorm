
function label(text){
    const label = document.createElement("label");
    label.textContent = text;
    return label;
}

function br(){
    const br = document.createElement('br');
    return br;
}

const edgeFormContainer = document.createElement("div");
document.body.appendChild(edgeFormContainer)
edgeFormContainer.id = 'edge-form-container';

//const edgeFormContainer = document.getElementById("form-container");
edgeFormContainer.innerHTML = '';

const edgeGroup = document.createElement("div");
edgeGroup.classList.add("input-edgeGroup");

const edgeSaveBtn = document.createElement("button");
edgeSaveBtn.textContent = 'Save';
edgeSaveBtn.onclick = edge_save_json;
edgeGroup.appendChild(edgeSaveBtn);
edgeGroup.appendChild(br());

edgeGroup.appendChild(label('id'));
edgeGroup.appendChild(br());
const edgeIdInput = document.createElement("input");
edgeGroup.appendChild(edgeIdInput);
edgeGroup.appendChild(br());

edgeGroup.appendChild(label('label'));
edgeGroup.appendChild(br());
const edgeLabelInput = document.createElement("input");
edgeGroup.appendChild(edgeLabelInput);
edgeGroup.appendChild(br());

edgeGroup.appendChild(label('direction'));
edgeGroup.appendChild(br());
const edgeDirectionInput = document.createElement("input");
edgeGroup.appendChild(edgeDirectionInput);
edgeGroup.appendChild(br());

const edgeBlockedInput = document.createElement("input");
edgeBlockedInput.type = 'checkbox';
edgeGroup.appendChild(edgeBlockedInput);
edgeGroup.appendChild(label('blocked'));
edgeGroup.appendChild(br());

const edgeSecretInput = document.createElement("input");
edgeSecretInput.type = 'checkbox';
edgeGroup.appendChild(edgeSecretInput);
edgeGroup.appendChild(label('secret'));
edgeGroup.appendChild(br());


edgeFormContainer.appendChild(edgeGroup);

function guiEdgeSetSelectedEdge(edge){
    if(edge !== null){
        data = edge.data().json;

        if (typeof data['id'] !== "undefined"){
            edgeIdInput.value = data['id'];
        } else {
            edgeIdInput.value = '';
        }

        if (typeof data['label'] !== "undefined"){
            edgeLabelInput.value = data['label'];
        } else {
            edgeLabelInput.value = '';
        }

        if (typeof data['direction'] !== "undefined"){
            edgeDirectionInput.value = data['direction'];
        } else {
            edgeDirectionInput.value = '';
        }

        if (typeof data['blocked'] !== "undefined"){
            edgeBlockedInput.checked = data['blocked'];
        } else {
            edgeBlockedInput.checked = false;
        }

        if (typeof data['secret'] !== "undefined"){
            edgeSecretInput.checked = data['secret'];
        } else {
            edgeSecretInput.checked = false;
        }
    }
}

function edge_save_json() {
    const data = {
        'id': edgeIdInput.value,
        'label': edgeLabelInput.value,
        'direction': edgeDirectionInput.value,
        'secret': edgeSecretInput.checked,
        'blocked': edgeBlockedInput.checked
    };

    

    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            if (data[key] === false || data[key] === '' || (typeof data[key] === "undefined")) {
                delete data[key];
            }
        }
    }

    console.log(data);
    
    if (window.selectedEdge!=null){
        window.selectedEdge.data().json = data
    } 
}

window.guiEdgeSetSelectedEdge = guiEdgeSetSelectedEdge;