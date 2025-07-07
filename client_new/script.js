const output = document.getElementById('output');
const input = document.getElementById('input');
const ansi_up = new AnsiUp();
const maxLines = 1000;

const hostname = window.location.hostname;
let socket;

function connectWebSocket(url, fallbackUrl) {
    socket = new WebSocket(url);

    socket.onerror = (error) => {
        console.error(`WebSocket error on ${url}:`, error);

        if (url !== fallbackUrl) {
            console.log(`Falling back to ${fallbackUrl}`);
            connectWebSocket(fallbackUrl, fallbackUrl);
        } else {
            console.error("Both WebSocket connections failed.");
        }
    };

    socket.onopen = () => {
        appendMessage('Connected to WebSocket server.');
        const IAC  = 0xFF;
        const DO   = 0xFD;
        const GMCP = 0xC9;
        const msg = new Uint8Array([IAC, DO, GMCP]);
        socket.send(msg);
    };

    socket.onmessage = async (event) => {
        let result = await displayBlobContent(event.data);
        result = result.replace('\\xff\\xfb\\xc9','');
        result = result.replace('\\xff\\xfbF','');
        let text = extractGmcpData(result);
        text = text.replace(/\\x([0-9A-Fa-f]{2})/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)));
        text = fixEncoding(text);

        const prev_type = input.type;

        if (["Your \u001b[1;32mpassword\u001b[0m:\n", 
             "Enter your \u001b[1;32mpassword\u001b[0m:\n",
             "Enter \u001b[1;32mpassword\u001b[0m again:\n"].includes(text)) {
            input.type = "password";
            input.value = "";
        } else {
            input.type = "text";
        }

        if (input.type !== prev_type) {
            input.value = "";
        }

        appendAnsiMessage(text);
    };

    socket.onclose = () => {
        appendMessage('Disconnected from WebSocket server.');
    };
}

connectWebSocket("ws://localhost:8002", "wss://jorm.kurowski.xyz:8001");

input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        if (input.value.trim() !== '') {
            socket.send(input.value);
            input.select();
        }
    }
});

function appendMessage(message) {
    const div = document.createElement('div');
    const urlPattern = /(https:\/\/[^\s]+)/g;
    const parts = message.split(urlPattern);

    parts.forEach(part => {
        if (urlPattern.test(part)) {
            const link = document.createElement('a');
            link.href = part;
            link.target = '_blank';
            link.textContent = part;
            div.appendChild(link);
        } else {
            div.appendChild(document.createTextNode(part));
        }
    });

    output.appendChild(div);
    maintainLineLimit();
    output.scrollTop = output.scrollHeight;
}

function appendAnsiMessage(message) {
    const div = document.createElement('div');
    let htmlMessage = ansi_up.ansi_to_html(message);
    const urlPattern = /(https:\/\/[^\s]+)/g;
    const parts = htmlMessage.split(urlPattern);
    parts.forEach(part => {
        if (urlPattern.test(part)) {
            const link = document.createElement('a');
            link.href = part;
            link.target = '_blank';
            link.innerHTML = part;
            div.appendChild(link);
        } else {
            div.innerHTML += part;
        }
    });

    output.appendChild(div);
    maintainLineLimit();
    output.scrollTop = output.scrollHeight;
}

function maintainLineLimit() {
    const lines = output.querySelectorAll('div');
    if (lines.length > maxLines) {
        output.removeChild(lines[0]);
    }
}

function fixEncoding(mojibakeStr) {
    const bytes = new Uint8Array([...mojibakeStr].map(c => c.charCodeAt(0)));
    return new TextDecoder('utf-8').decode(bytes);
}

function extractGmcpData(data) {
    const regex = /\\xff\\xfa\\xc9(.*?)\\xff\\xf0/g;
    let match;
    let lastIndex = 0;
    let result = "";

    while ((match = regex.exec(data)) !== null) {
        const gmcpContent = match[1];
        console.log("Found GMCP data:", gmcpContent);
        const splitRegex = /^(\S+)\s+(\{.*\})$/;
        const parts = gmcpContent.match(splitRegex);

        if (parts) {
            const command = parts[1];
            let dictString = parts[2];
            dictString = dictString.replace(/'/g, '"');

            try {
                const dict = JSON.parse(dictString);
                if (command === "Client.Media.Play" && dict.name) {
                    playSound('audio/sfx/' + dict.name);
                }
            } catch (e) {
                console.error("Error parsing GMCP JSON:", e);
            }
        } else {
            console.warn("GMCP content didn't match expected format:", gmcpContent);
        }

        result += data.slice(lastIndex, match.index);
        lastIndex = regex.lastIndex;
    }

    result += data.slice(lastIndex);
    return result;
}

async function displayBlobContent(blob) {
    const buffer = await blob.arrayBuffer();
    const uint8Array = new Uint8Array(buffer);

    let result = '';
    let hexBuffer = '';

    uint8Array.forEach(byte => {
        if (byte >= 32 && byte <= 126) {
            if (hexBuffer) {
                result += `\\x${hexBuffer}`;
                hexBuffer = '';
            }
            result += String.fromCharCode(byte);
        } else {
            result += "\\x" + byte.toString(16).padStart(2, '0');
        }
    });

    if (hexBuffer) {
        result += `\\x${hexBuffer}`;
    }

    return result;
}

// === AUDIO UI ===

const volumeButton = document.getElementById('volumeButton');
const slidersBox = document.getElementById('slidersBox');
const slider1 = document.getElementById('slider1');
const slider2 = document.getElementById('slider2');

let AudioSFXVolume = slider1.value;
let AudioMusic = null;

volumeButton.addEventListener('click', () => {
    slidersBox.style.display = (slidersBox.style.display === 'block') ? 'none' : 'block';
});

slider1.addEventListener('input', () => {
    AudioSFXVolume = slider1.value;
});

slider2.addEventListener('input', () => {
    if (AudioMusic) AudioMusic.volume = slider2.value;
});

function startRandomAudioPlayer(audioFiles) {
    if (!audioFiles || audioFiles.length === 0) {
        console.error("No audio files provided.");
        return;
    }

    let currentAudio = null;

    function playRandomAudio() {
        const randomIndex = Math.floor(Math.random() * audioFiles.length);
        const selectedAudio = audioFiles[randomIndex];

        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }

        currentAudio = new Audio(selectedAudio);
        currentAudio.volume = slider2.value;
        currentAudio.play();
        currentAudio.onended = playRandomAudio;
        AudioMusic = currentAudio;
    }

    playRandomAudio();
}

function playSound(effect) {
    const audio = new Audio(effect);
    audio.volume = AudioSFXVolume;
    audio.play().catch(console.error);
}

const audioList = [
    'audio/music/7OOO.mp3',
    'audio/music/0240.mp3',
    'audio/music/Contrast 100.mp3',
    'audio/music/Ivory.mp3',
    'audio/music/N A W A K - FOREST.mp3',
    'audio/music/N A W A K - SEIZE.mp3',
    'audio/music/N A W A K - TRIAL.mp3'
];

function createStartScreen() {
    const startScreen = document.createElement('div');
    startScreen.id = 'startScreen';

    const button = document.createElement('button');
    button.id = 'startButton';
    button.textContent = 'START';

    startScreen.appendChild(button);
    document.body.appendChild(startScreen);

    button.addEventListener('click', function () {
        const unlockAudio = new Audio();
        unlockAudio.play().catch(() => {});
        startRandomAudioPlayer(audioList);
        startScreen.remove();
    });
}

window.addEventListener('DOMContentLoaded', createStartScreen);
