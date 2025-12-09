extends LineEdit

var history = []
var history_line = 0
# Called when the node enters the scene tree for the first time.
func _ready():
	
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func _input(event):
	return
	if Input.is_key_pressed(KEY_UP):
		if history_line == 0:
			history_line += 1
		history_line += 1
	if Input.is_key_pressed(KEY_DOWN):
		history_line -= 1
	if Input.is_key_pressed(KEY_ENTER):
		if text not in history:
			history.insert(0, text)
		history_line = 0
		if len(history) == 10:
			history.remove_at(9)
	
	if Input.is_key_pressed(KEY_UP) or Input.is_key_pressed(KEY_DOWN):
		history_line = clamp(history_line,0,len(history))
		if history_line != 0:
			text = history[history_line-1]
		else:
			text = ''
		await get_tree().create_timer(0.1).timeout
		set_caret_column(len(text))

