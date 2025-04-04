
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

const group = document.createElement("div");
group.classList.add("input-group");

const export_btn = document.createElement("button");
export_btn.textContent = 'EXPORT!!!!!!!!!';
export_btn.onclick = export_json;
group.appendChild(export_btn);
group.appendChild(br());

group.appendChild(label('id'));
group.appendChild(br());
const id_input = document.createElement("input");
group.appendChild(id_input);
group.appendChild(br());

group.appendChild(label('label'));
group.appendChild(br());
const label_input = document.createElement("input");
group.appendChild(label_input);
group.appendChild(br());

group.appendChild(label('color'));
group.appendChild(br());
const color_input = document.createElement("input");
group.appendChild(color_input);
group.appendChild(br());

group.appendChild(label('name'));
group.appendChild(br());
const name_input = document.createElement("input");
group.appendChild(name_input);
group.appendChild(br());

group.appendChild(label('desc'));
group.appendChild(br());
const desc_input = document.createElement("textarea");
group.appendChild(desc_input);
group.appendChild(br());

const can_be_recall_site_input = document.createElement("input");
can_be_recall_site_input.type = 'checkbox';
group.appendChild(can_be_recall_site_input);
group.appendChild(label('safe'));
group.appendChild(br());

const instanced_input = document.createElement("input");
instanced_input.type = 'checkbox';
group.appendChild(instanced_input);
group.appendChild(label('instanced'));
group.appendChild(br());

group.appendChild(label('spawner syntax'));
group.appendChild(br());
const spawm_group_input = document.createElement("textarea");
group.appendChild(spawm_group_input);
group.appendChild(br());

formContainer.appendChild(group);

function GUIsetSelectedNode(node){
    if(node !== null){
        data = node.data().json;

        if (typeof data['id'] !== "undefined"){
            id_input.value = data['id'];
        } else {
            id_input.value = '';
        }

        if (typeof data['label'] !== "undefined"){
            label_input.value = data['label'];
        } else {
            label_input.value = '';
        }

        if (typeof data['color'] !== "undefined"){
            color_input.value = data['color'];
        } else {
            color_input.value = '';
        }

        if (typeof data['name'] !== "undefined"){
            name_input.value = data['name'];
        } else {
            name_input.value = '';
        }

        if (typeof data['desc'] !== "undefined"){
            desc_input.value = data['desc'];
        } else {
            desc_input.value = '';
        }

        if (typeof data['can_be_recall_site'] !== "undefined"){
            can_be_recall_site_input.value = data['can_be_recall_site'];
        } else {
            can_be_recall_site_input.value = '';
        }

        if (typeof data['instanced'] !== "undefined"){
            instanced_input.value = data['instanced'];
        } else {
            instanced_input.value = '';
        }

        if (typeof data['spawn'] !== "undefined"){
            spawm_group_input.value = data['spawn'];
        } else {
            spawm_group_input.value = '';
        }
    }
}


  
function export_json() {
    const data = {
        'id': id_input.value,
        'label': label_input.value,
        'color': color_input.value,
        'name': name_input.value,
        'description': desc_input.value,
        'can_be_recall_site': can_be_recall_site_input.checked,
        'instanced': instanced_input.checked,
        'spawner': spawm_group_input.value
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
    
    navigator.clipboard.writeText(textToCopy)
        .then(() => {
            //alert("Text copied to clipboard!");
        })
        .catch(err => {
            console.error("Failed to copy text: ", err);
        });

    
    if (window.selectedNode!=null){
        window.selectedNode.data().json = data
    } 
}

window.GUIsetSelectedNode = GUIsetSelectedNode;