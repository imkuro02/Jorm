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
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func get_message(data):
	var size = 64
	
	for child in MAP.get_children():
		remove_child(child)
		child.free()
		
	var center_x = 0*size + (size*3) + size/2
	var center_y = 0*size + (size*3) + size/2
	
	var _center = you.duplicate()
	you.position.x = center_x
	you.position.y = center_y
	MAP.add_child(you)
	
	print('split')
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
		print(data[i]['id'],'x',x,',','y',y)
		var _node = node.duplicate()
		var pos_x = x*size + (size*3) + size/2
		var pos_y = y*size + (size*3) + size/2
		
		_node.position.x = pos_x
		_node.position.y = pos_y
		
		
		MAP.add_child(_node)
		
		
		for conn in data[i]['exits']:
			if conn['direction'] not in directions:
				print(conn['direction'], directions, conn['direction'] not in directions)
				continue
			if conn['direction'] in directions_rotations:
				var _conn = connection.duplicate()
				_conn.position.x = pos_x
				_conn.position.y = pos_y
				_conn.rotation = deg_to_rad(directions_rotations[conn['direction']]) 
				MAP.add_child(_conn)
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
				MAP.add_child(_conn)
			
		var doorway = bool(data[i]['doorway'])
		if doorway:
			var _doorway = door.duplicate()
			_doorway.position.x = pos_x
			_doorway.position.y = pos_y
			MAP.add_child(_doorway)
		
		
		
		

