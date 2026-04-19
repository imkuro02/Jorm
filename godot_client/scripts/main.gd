extends Control

@export var websocket_url_local = "ws://localhost:8002"
@export var websocket_url = "wss://jorm.kurowski.xyz:8001"

var socket = WebSocketPeer.new()

# References to UI nodes
@onready var INPUT = $canvas/input/input
@onready var OUTPUT = $canvas/container/output/output
@onready var SIDEBAR = $canvas/container/sidebar
@onready var DEBUG = $canvas/debug
@onready var SFX_MAN = $sfx_manager
@onready var LOOK_ROOM = $canvas/container/sidebar/look_room
@onready var ASCIIMAP = $canvas/container/sidebar/ascii_map
@onready var OUTPUT_COMBAT = $canvas/container/output/output_combat
@onready var MOUSE_CLICK_OPTIONS = $canvas/mouse_click_options
@onready var EXPBAR = $canvas/smooth_exp_bar

var game_state = 'none yet'

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
	SIDEBAR.visible = false
	EXPBAR.visible = false
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
			await get_tree().create_timer(0.2).timeout
			socket.send(PackedByteArray([IAC, SB, GMCP, "godot on", IAC, SE]))
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
	var prefix = 'prefix'
	var dict_string = ''
	if len(parts) <= 1:
		prefix = parts[0]
	else:
		prefix = parts[0]
		dict_string = parts[1]
	var data_dict = null

	if "{" not in dict_string:
		data_dict = null
	else:
		data_dict = JSON.parse_string(dict_string.replace("'", '"'))

	match prefix:
		'ExpBar':
			EXPBAR.fill_exp(data_dict['exp_cur'], data_dict['exp_max'], data_dict['lvl'])
			
		'GAME_STATE':
			game_state = dict_string
			ASCIIMAP.clear()
			OUTPUT_COMBAT.clear()
			#OUTPUT.clear()
			#OUTPUT.append_text("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
			INPUT.secret = 'REGISTER_PASSWORD' in game_state or 'LOGIN_PASSWORD' in game_state
			INPUT.clear()
			
			SIDEBAR.visible = 'PLAY' in game_state
			EXPBAR.visible = 'PLAY' in game_state
				
		'Client.Media.Play':
			var sfx = load("res://audio/sfx/" + data_dict['name'])
			SFX_MAN.stream = sfx
			SFX_MAN.play()
		#'Actors':
		#	ACTORS_OUTPUT.set_text("")
		#	ACTORS_OUTPUT.clear()
		#	ACTORS_OUTPUT.get_message(dict_string)
		'OUTPUT_COMBAT':
			#print('dict_string')
			#print(dict_string)
			OUTPUT_COMBAT.clear()
			OUTPUT_COMBAT.get_message('********************************************************************************\n'+dict_string)
		'MAP':
			ASCIIMAP.clear()
			ASCIIMAP.get_message(dict_string)
		'MMAAPP':
			ASCIIMAP.clear()
			ASCIIMAP.get_message(dict_string)
		'LOOK_ROOM':
			LOOK_ROOM.clear()
			LOOK_ROOM.get_message(dict_string)
		#'Time':
		#	CLOCK.get_message(data_dict)
			#BACKGROUND_COLOR.get_message(data_dict)


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

func handle_meta_clicked(meta, forced = false):
	#print(meta)
	if forced:
		if ',' in meta:
			var output := []
			var entries = meta.split(",")
			for entry in entries:
				if "->" in entry:
					var parts = entry.split("->", false, 2)
					var url = parts[1].strip_edges()
					var text = parts[0].strip_edges()
					output.append("%s" % [url])
					var o = "".join(output)
					socket.send_text(o.strip_edges())
					break
		else:
			socket.send_text(meta.strip_edges())
	else:
		if ',' in meta:
			var output := []
			var entries = meta.split(",")
			for entry in entries:
				if "->" in entry:
					var parts = entry.split("->", false, 2)
					var url = parts[1].strip_edges()
					var text = parts[0].strip_edges()
					output.append("[url=%s]%s[/url]\n" % [url, text])
			MOUSE_CLICK_OPTIONS.text = "".join(output).strip_edges(false, true)
			#OUTPUT.append_text("<OPTIONS START>\n")
			#OUTPUT.append_text("".join(output))
			#OUTPUT.append_text("<OPTIONS END>\n")
		else:
			socket.send_text(meta.strip_edges())
			
"""
func _on_navigation_meta_clicked(meta):
	handle_meta_clicked(meta)

func _on_output_meta_clicked(meta):
	handle_meta_clicked(meta)

func _on_mouse_click_options_meta_clicked(meta):
	handle_meta_clicked(meta)

func _on_output_combat_meta_clicked(meta):
	handle_meta_clicked(meta)

func _on_ascii_map_meta_clicked(meta):
	handle_meta_clicked(meta)
"""

var last_button_clicked = MOUSE_BUTTON_LEFT
var last_meta_hovered = null

func _input(event):
	#print(event)
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT:
			MOUSE_CLICK_OPTIONS.text = ""
			MOUSE_CLICK_OPTIONS.size.x = 0
			MOUSE_CLICK_OPTIONS.size.y = 0
			MOUSE_CLICK_OPTIONS.position.x = -1000
			MOUSE_CLICK_OPTIONS.position.y = -1000
			if last_meta_hovered == null:
				return
			handle_meta_clicked(last_meta_hovered, false)
			if MOUSE_CLICK_OPTIONS.text == "":
				return
			MOUSE_CLICK_OPTIONS.position.x = event.position.x
			MOUSE_CLICK_OPTIONS.position.y = event.position.y
			
			var screen_height = get_viewport_rect().size.y - (6*16)
			var screen_width = get_viewport_rect().size.x
			if MOUSE_CLICK_OPTIONS.position.y + MOUSE_CLICK_OPTIONS.size.y > screen_height:
				MOUSE_CLICK_OPTIONS.position.y = screen_height - MOUSE_CLICK_OPTIONS.size.y
			if MOUSE_CLICK_OPTIONS.position.x + MOUSE_CLICK_OPTIONS.size.x > screen_width:
				MOUSE_CLICK_OPTIONS.position.x = screen_width - MOUSE_CLICK_OPTIONS.size.x
				
		if event.button_index == MOUSE_BUTTON_MASK_RIGHT:
			if last_meta_hovered == null:
				return
			handle_meta_clicked(last_meta_hovered, true)
					
func _on_ascii_map_meta_hover_started(meta):
	last_meta_hovered = meta
func _on_ascii_map_meta_hover_ended(meta):
	last_meta_hovered = null

func _on_navigation_meta_hover_started(meta):
	last_meta_hovered = meta
func _on_navigation_meta_hover_ended(meta):
	last_meta_hovered = null

func _on_output_meta_hover_started(meta):
	last_meta_hovered = meta
func _on_output_meta_hover_ended(meta):
	last_meta_hovered = null

func _on_mouse_click_options_meta_hover_started(meta):
	last_meta_hovered = meta
func _on_mouse_click_options_meta_hover_ended(meta):
	last_meta_hovered = null

func _on_output_combat_meta_hover_started(meta):
	last_meta_hovered = meta
func _on_output_combat_meta_hover_ended(meta):
	last_meta_hovered = null
