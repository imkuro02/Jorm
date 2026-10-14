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

# Cache phase values by identifier.
var phase_cache: Dictionary = {}

func _process_custom_fx(char_fx: CharFXTransform) -> bool:
	var time := Time.get_unix_time_from_system()
	var speed := 6.0
	var height := 5.0

	var phase_name: String = str(char_fx.env.get("phase", "default"))

	# Calculate and cache the phase only once per unique string.
	if not phase_cache.has(phase_name):
		phase_cache[phase_name] = float(abs(phase_name.hash()) % 6283) / 1000.0

	var phase: float = phase_cache[phase_name]

	char_fx.offset.y = absf(sin(time * speed + phase)) * height

	return true
