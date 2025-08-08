extends Sprite2D

var current_sprite = null
# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	return
	if not visible:
		return
		
	var to_animate = []
		
	var children = get_parent().get_children()
	for i in children:
		if i.position == position:
			if i != self:
				to_animate.append(i)
	
	
	pass
