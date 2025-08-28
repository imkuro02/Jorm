extends Sprite2D


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
	
func get_message(data):
	
	
	var bonus_base = 180
	var bonus_hour = 360 / 24*int(data['hour']) 
	#var bonus_min: float = (360 / (24 * 60)) * data['minute'];
	#print(int(data['minute']))
	#print(bonus_min)
	set_rotation_degrees(bonus_base + bonus_hour)

	#print(data)
