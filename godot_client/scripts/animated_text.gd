"""
@tool
extends RichTextEffect
class_name JumpEffect

var bbcode := "jump"

func _process_custom_fx(char_fx: CharFXTransform) -> bool:
	var time := char_fx.elapsed_time
	var speed := 6.0
	var height := 5.0

	char_fx.offset.y = -absf(sin(time  * speed)) * height
	return true
"""

@tool
extends RichTextEffect
class_name JumpEffect

var bbcode := "jump"

func _process_custom_fx(char_fx: CharFXTransform) -> bool:
	var time := Time.get_unix_time_from_system() # char_fx.elapsed_time
	var speed := 6.0
	var height := 5.0

	# Get a string identifier from the BBCode effect parameters.
	var phase_name: String = str(char_fx.env.get("phase", "default"))
	# Convert the string into a consistent numeric phase.
	var phase: float = float(abs(phase_name.hash()) % 6283) / 1000.0

	char_fx.offset.y = -absf(sin(time * speed + phase)) * height

	return true
