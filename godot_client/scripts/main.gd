extends Control

@export var websocket_url_local = "ws://localhost:8002"
@export var websocket_url = "wss://jorm.kurowski.xyz:8001"

var socket = WebSocketPeer.new()

# References to UI nodes
@onready var INPUT = $canvas/HBoxContainer/input_output/input
@onready var OUTPUT = $canvas/HBoxContainer/input_output/HBoxContainer/output
@onready var DEBUG = $canvas/HBoxContainer/input_output/HBoxContainer/debug
@onready var ACTORS_OUTPUT = $canvas/HBoxContainer/Control/actors_output
@onready var SFX_MAN = $sfx_manager
@onready var MAP = $canvas/HBoxContainer/side_panel/map



const IAC      : int = 255   # 0xFF  Interpret‑As‑Command
const WILL     : int = 251   # 0xFB  Will Perform
const SE       : int = 240   # 0xF0  Sub‑negotiation End
const SB       : int = 250   # 0xFA  Sub‑negotiation Begin
const WONT     : int = 252   # 0xFC  Will Nospritet Perform
const DO       : int = 253   # 0xFD  Please Do
const DONT     : int = 254   # 0xFE  Please Don’t
const ECHO     : int =   1   # 0x01  Echo
const LINEMODE : int =  34   # 0x22  Line‑mode
const GMCP     : int = 201   # 0xC9  Generic Mud Comm Prot
const MSSP     : int =  70   # 0x46  Mud Server Status Prot

const telnet_stuff := {
	IAC:      "IAC",
	WILL:     "WILL",
	SE:       "SE",
	SB:       "SB",
	WONT:     "WONT",
	DO:       "DO",
	DONT:     "DONT",
	ECHO:     "ECHO",
	#LINEMODE: "LINEMODE",
	GMCP:     "GMCP",
	MSSP:     "MSSP",
}

func _ready():
	# Connect the input signal for Enter key
	INPUT.text_submitted.connect(_on_input_submitted)

	# Connect to WebSocket server
	var err = socket.connect_to_url(websocket_url_local)
	if err != OK:
		print("Unable to connect")
		set_process(false)
	else:
		print("Connecting...")
		await get_tree().create_timer(2).timeout
		socket.send(PackedByteArray([IAC,DO,GMCP]))
		#socket.send_text("Test packet")

func string_to_dict(source: String) -> Dictionary:
	var result := {}

	# Remove outer braces and whitespace
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

		var key = kv[0].strip_edges().replace("'","")
		var value = kv[1].strip_edges()

		# Remove optional quotes from keys
		#key = key.replace("'",'"')


		# Parse value
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
		return val.substr(1, val.length() - 2)# Remove quotes
	else:
		return val  # fallback: return as string

		
func handle_gmcp(message: String):
	var command = ''
	var data = ''
	var parts = message.split(" ", false, 1)
	if len(parts) <= 1:
		return
	var prefix = parts[0]
	var dict_string = parts[1]

	# Convert string to actual Dictionary using JSON
	# First, replace single quotes with double quotes for JSON compatibility
	#dict_string = dict_string.replace("'", '"')

	var data_dict = JSON.parse_string(dict_string.replace("'",'"')) #string_to_dict(dict_string)
	
	#print(prefix,data_dict)
	#print(dict_string)     
	#print(data_dict)  
	#print(prefix, data_dict)
	match prefix:
		'Client.Media.Play':
			
			var sfx = load("res://audio/sfx/"+data_dict['name'])
			SFX_MAN.stream = sfx
			SFX_MAN.play()
		'Actors':
			ACTORS_OUTPUT.set_text("")
			ACTORS_OUTPUT.clear()
			ACTORS_OUTPUT.get_message(dict_string)
		'Map':
			MAP.get_message(data_dict)
	
func extract_gmcp(int_data: Array[int]) -> void:
	var start := 0                      
	var segment := []
	for i in int_data:
		if i == SE:         
			var data = PackedByteArray(segment).get_string_from_utf8()
			DEBUG.append_text(data+'\n')
			if len(data)>0:
				handle_gmcp(data)
			segment = []
		else:
			segment.append(i)
			


func _process(_delta):
	socket.poll()

	var state = socket.get_ready_state()

	if state == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			var _message := socket.get_packet()
			var to_remove := []
			var int_subnegotiation : Array[int] = []
			# First pass: print commands, collect indices to remove
			var doing_sb = false
			for idx in range(_message.size()):
				var i = _message[idx]
				
				
				# a very dirty hack
				# if byte 70 (which is both MSSP and letter F) check if its somehow related to a subnegotiation
				# by checking previous byte, if not then skip this otherwise the letter F will get dropped
				var skip = false
				if idx != 0:
					if _message[idx] == 70 and _message[idx-1] not in [IAC, SB, SE, DO, DONT, WILL, WONT]:
						skip = true
				if skip:
					continue
						
				if i in telnet_stuff:
					if i == SB:
						doing_sb = true
					if i == SE:
						int_subnegotiation.append(SE)
						doing_sb = false
					#print(telnet_stuff[i])
					#DEBUG.append_text(telnet_stuff[i]+' ')
					to_remove.append(idx)
				if doing_sb and i not in telnet_stuff:
					int_subnegotiation.append(i)
					to_remove.append(idx)
			DEBUG.append_text('\n')

			# Second pass: remove collected indices, from back to front
			#to_remove.sort()
			to_remove.reverse()
			for idx in to_remove:
				_message.remove_at(idx)

			# print subnegotiation
			if int_subnegotiation.size() > 0:
				extract_gmcp(int_subnegotiation)

			var message = _message.get_string_from_utf8()
			OUTPUT.get_message(message)
			
			

	elif state == WebSocketPeer.STATE_CLOSING:
		# Keep polling until clean close
		pass

	elif state == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		print("WebSocket closed. Code: %d. Clean: %s" % [code, code != -1])
		set_process(false)

func _on_input_submitted(text: String) -> void:
	# and text.strip_edges() != ""
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		socket.send_text(text.strip_edges())
		#OUTPUT.append_text('>'+text+'\n')
		
		INPUT.select_all()
		#INPUT.clear()
	else:
		print("Socket not ready or input was empty.")
