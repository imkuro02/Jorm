extends TextEdit

@onready var OUTPUT = $"../output"

var TEXT = ''
# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if TEXT != self.text:
		print('test')
		TEXT = self.text
		OUTPUT.get_message(self.text)

