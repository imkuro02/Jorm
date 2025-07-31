extends Panel

@onready var MAP = $map
@onready var ASS = $assets

@onready var node = $assets/node
@onready var connection = $assets/connection
@onready var up = $assets/up
@onready var down = $assets/down
@onready var door = $assets/door
@onready var you =  $assets/you

var directions = 'up down north west east south'.split(' ')
var directions_rotations = {'north': 0, 'east': 90, 'south': 180, 'west': 270}
var directions_vertical = {'up': up, 'down': down}
# Called when the node enters the scene tree for the first time.


func _ready():
	for child in ASS.get_children():
		child.visible = false
		
	var size = 64
	var center_x = position.x + (0*size) + (size*3) + size/2
	var center_y = position.y + (0*size) + (size*3) + size/2
	
	var _center = you.duplicate()
	_center.position.x = position.x + center_x
	_center.position.y = -position.y + center_y
	#_center.scale = _center.scale * 10
	_center.visible = true
	MAP.get_parent().add_child(_center)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func get_message(data):
	var size = 64
	
	var to_delete = []
	var to_add = []
	for child in MAP.get_children():
		to_delete.append(child)
		
		
	var center_x = position.x + (0*size) + (size*3) + size/2
	var center_y = position.y + (0*size) + (size*3) + size/2
	
	

	
	
	for i in data:
		var x = int(i.split(',')[0])
		var y = int(i.split(',')[1])
		var z = int(i.split(',')[2])
		if z != 0:
			continue
		if abs(x)>=4:
			continue
		if abs(y)>=4:
			continue
		
		var _node = node.duplicate()
		var pos_x = position.x + x*size + (size*3) + size/2
		var pos_y = position.y + y*size + (size*3) + size/2
		
		_node.position.x = pos_x
		_node.position.y = pos_y
		#_node.modulate = pos_x+pos_y
		to_add.append(_node)
		
		
		for conn in data[i]['exits']:
			if conn['direction'] not in directions:
				#print(conn['direction'], directions, conn['direction'] not in directions)
				continue
			if conn['direction'] in directions_rotations:
				var _conn = connection.duplicate()
				_conn.position.x = pos_x
				_conn.position.y = pos_y
				_conn.rotation = deg_to_rad(directions_rotations[conn['direction']]) 
				to_add.append(_conn)
			if conn['direction'] in directions_vertical:
				var _conn = null
				if conn['direction'] == 'up':
					_conn = up.duplicate()
				if conn['direction'] == 'down':
					_conn = down.duplicate()
				if _conn == null:
					continue
				_conn.position.x = pos_x
				_conn.position.y = pos_y
				to_add.append(_conn)
			
		var doorway = bool(data[i]['doorway'])
		if doorway:
			var _doorway = door.duplicate()
			_doorway.position.x = pos_x
			_doorway.position.y = pos_y
			to_add.append(_doorway)
			
	
		
			
		
	update_children(to_add, to_delete)
		
	
func update_children(to_add: Array, to_delete: Array) -> void:
	await get_tree().process_frame
	for child in to_delete:
		child.visible = false
		MAP.remove_child(child)
		child.queue_free()

	for child in to_add:
		child.visible = true
		MAP.add_child(child)
		
		
		
		

