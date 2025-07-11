extends Control

@export var websocket_url = "ws://localhost:8002"
#@export var websocket_url = "wss://jorm.kurowski.xyz:8001"

var socket = WebSocketPeer.new()

# References to UI nodes
@onready var INPUT = $canvas/input
@onready var OUTPUT = $canvas/HBoxContainer/output
@onready var DEBUG = $canvas/HBoxContainer/debug



const IAC      : int = 255   # 0xFF  Interpret‑As‑Command
const WILL     : int = 251   # 0xFB  Will Perform
const SE       : int = 240   # 0xF0  Sub‑negotiation End
const SB       : int = 250   # 0xFA  Sub‑negotiation Begin
const WONT     : int = 252   # 0xFC  Will Not Perform
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
	var err = socket.connect_to_url(websocket_url)
	if err != OK:
		print("Unable to connect")
		set_process(false)
	else:
		print("Connecting...")
		await get_tree().create_timer(2).timeout
		#socket.send_text("Test packet")



func handle_gmcp(int_data: Array[int]) -> void:
	var start := 0                      
	var segment := []
	for i in int_data:
		if i == SE:         
			var data = PackedByteArray(segment).get_string_from_utf8()
			DEBUG.append_text(data+'\n')
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
			to_remove.sort()
			to_remove.reverse()
			for idx in to_remove:
				_message.remove_at(idx)

			# print subnegotiation
			if int_subnegotiation.size() > 0:
				handle_gmcp(int_subnegotiation)

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
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN and text.strip_edges() != "":
		socket.send_text(text)
		INPUT.select_all()
	else:
		print("Socket not ready or input was empty.")
