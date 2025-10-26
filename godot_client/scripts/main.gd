extends Control

@export var websocket_url_local = "ws://localhost:8002"
@export var websocket_url = "wss://jorm.kurowski.xyz:8001"

var socket = WebSocketPeer.new()

# References to UI nodes
@onready var INPUT = $canvas/HBoxContainer/input_output/input/input
@onready var OUTPUT = $canvas/HBoxContainer/input_output/HBoxContainer/output
@onready var DEBUG = $canvas/HBoxContainer/input_output/HBoxContainer/debug
@onready var ACTORS_OUTPUT = $canvas/HBoxContainer/Control/actors_output
@onready var SFX_MAN = $sfx_manager
@onready var MAP = $canvas/HBoxContainer/side_panel/map
@onready var ASCIIMAP = $canvas/HBoxContainer/side_panel/ascii_map
@onready var CLOCK = $canvas/HBoxContainer/side_panel/Clock
@onready var BACKGROUND_COLOR = $canvas/background_color

const IAC      : int = 255
const WILL     : int = 251
const SE       : int = 240
const SB       : int = 250
const WONT     : int = 252
const DO       : int = 253
const DONT     : int = 254
const ECHO     : int =   1
const LINEMODE : int =  34
const GMCP     : int = 201
const MSSP     : int =  70

const telnet_stuff := {
	IAC:      "IAC",
	WILL:     "WILL",
	SE:       "SE",
	SB:       "SB",
	WONT:     "WONT",
	DO:       "DO",
	DONT:     "DONT",
	ECHO:     "ECHO",
	GMCP:     "GMCP",
}

func _ready():
	# Connect the input signal for Enter key
	INPUT.text_submitted.connect(_on_input_submitted)

	# Try local WebSocket first, then fallback to remote
	await try_connect_in_order([websocket_url_local, websocket_url])


# --- Connection Handling ---

func try_connect_in_order(urls: Array) -> void:
	var connected := false
	for url in urls:
		print("Attempting connection to: ", url)
		var err = socket.connect_to_url(url)
		if err != OK:
			print("Immediate connect_to_url() error: ", err)
			continue

		var success := await wait_for_connection(socket, 3.0) # wait up to 3s
		if success:
			print("Connected to: ", url)
			OUTPUT.get_message("Connected to: %s\n" % url)
			await get_tree().create_timer(1.0).timeout
			socket.send(PackedByteArray([IAC, DO, GMCP]))
			connected = true
			break
		else:
			print("Connection to ", url, " failed or timed out.")
			socket = WebSocketPeer.new() # reset socket before retry

	if not connected:
		print("Unable to connect to any WebSocket server.")
		set_process(false)


func wait_for_connection(sock: WebSocketPeer, timeout: float) -> bool:
	var timer := get_tree().create_timer(timeout)
	while timer.time_left > 0:
		sock.poll()
		var state := sock.get_ready_state()
		if state == WebSocketPeer.STATE_OPEN:
			return true
		elif state == WebSocketPeer.STATE_CLOSED:
			return false
		await get_tree().process_frame
	return false


# --- Input Handling ---

func _on_input_submitted(text: String) -> void:
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN and text.strip_edges() != "":
		socket.send_text(text.strip_edges())
		if text.split(" ")[0] in ['say', 'shout']:
			INPUT.text = text.split(" ")[0] + ' '
			INPUT.caret_column = INPUT.text.length()
		else:
			INPUT.select_all()
	else:
		print("Socket not ready or input was empty.")


# --- GMCP / Telnet Logic ---

func string_to_dict(source: String) -> Dictionary:
	var result := {}
	source = source.strip_edges()
	if source.begins_with("{") and source.ends_with("}"):
		source = source.substr(1, source.length() - 2)
	else:
		return result

	var pairs = source.split(",", false)
	for pair in pairs:
		pair = pair.strip_edges()
		var kv = pair.split(":", false)
		if kv.size() != 2:
			continue
		var key = kv[0].strip_edges().replace("'", "")
		var value = kv[1].strip_edges()
		var val = parse_value(value)
		result[key] = val
	return result


func parse_value(val: String) -> Variant:
	val = val.strip_edges()
	if val == "true":
		return true
	elif val == "false":
		return false
	elif (val.begins_with("'") and val.ends_with("'")) or (val.begins_with('"') and val.ends_with('"')):
		return val.substr(1, val.length() - 2)
	else:
		return val


func handle_gmcp(message: String):
	var parts = message.split(" ", false, 1)
	if len(parts) <= 1:
		return
	var prefix = parts[0]
	var dict_string = parts[1]
	var data_dict = null

	if "{" not in dict_string:
		data_dict = null
	else:
		data_dict = JSON.parse_string(dict_string.replace("'", '"'))

	match prefix:
		'Client.Media.Play':
			var sfx = load("res://audio/sfx/" + data_dict['name'])
			SFX_MAN.stream = sfx
			SFX_MAN.play()
		'Actors':
			ACTORS_OUTPUT.set_text("")
			ACTORS_OUTPUT.clear()
			ACTORS_OUTPUT.get_message(dict_string)
		'MMAAPP':
			ASCIIMAP.clear()
			ASCIIMAP.get_message(dict_string)
		'Time':
			CLOCK.get_message(data_dict)
			BACKGROUND_COLOR.get_message(data_dict)


func extract_gmcp(int_data: Array[int]) -> void:
	var segment := []
	for i in int_data:
		if i == SE:
			var data = PackedByteArray(segment).get_string_from_utf8()
			DEBUG.append_text(data + '\n')
			if len(data) > 0:
				handle_gmcp(data)
			segment = []
		else:
			segment.append(i)


func remove_trailing_70(packet: PackedByteArray) -> PackedByteArray:
	if packet.size() > 0 and packet[packet.size() - 1] == 70:
		return packet.slice(0, packet.size() - 1)
	return packet


# --- Processing Loop ---

func _process(_delta):
	socket.poll()

	var state = socket.get_ready_state()

	if state == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			var _message := socket.get_packet()
			_message = remove_trailing_70(_message)

			var to_remove := []
			var int_subnegotiation : Array[int] = []
			var doing_sb = false
			for idx in range(_message.size()):
				var i = _message[idx]
				if i in telnet_stuff:
					if i == SB:
						doing_sb = true
					if i == SE:
						int_subnegotiation.append(SE)
						doing_sb = false
					to_remove.append(idx)
				if doing_sb and i not in telnet_stuff:
					int_subnegotiation.append(i)
					to_remove.append(idx)
			DEBUG.append_text('\n')

			to_remove.reverse()
			for idx in to_remove:
				_message.remove_at(idx)

			if int_subnegotiation.size() > 0:
				extract_gmcp(int_subnegotiation)

			var message = _message.get_string_from_utf8()
			OUTPUT.get_message(message)

	elif state == WebSocketPeer.STATE_CLOSING:
		pass

	elif state == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		print("WebSocket closed. Code: %d. Clean: %s" % [code, code != -1])
		OUTPUT.get_message("\n\n<--!-->\tYou have been disconnected! refresh the page to reconnect!\t<--!-->")
		set_process(false)
