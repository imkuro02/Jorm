extends RichTextLabel


# Called when the node enters the scene tree for the first time.
func _ready():
	#fill_centered(self, '')
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	#fill_exp(15, 32, 16)
	pass

func fill_exp(exp_cur, exp_max, lvl) -> void:
	var label = self
	var base_text = ""
	label.clear()
	
	var percent = (float(exp_cur) / float(exp_max)) * 100.0
	var formatted = "(%.2f%%)" % percent
	base_text = " EXP " + str(exp_cur) + " / " + str(exp_max) + " " + str(formatted) + " LEVEL " + str(lvl)

	var font = label.get_theme_font("normal_font")
	var font_size = label.get_theme_font_size("normal_font_size")
	var max_width = label.size.x

	# Width of base text
	var base_size = font.get_string_size(base_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x

	# Width of one "#"
	var hash_width = font.get_string_size("#", HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x

	# Remaining space
	var remaining = max_width - base_size
	if remaining <= 0:
		label.append_text(base_text)
		return

	# Total number of hashes that fit
	var total_hashes = int(remaining / hash_width)

	# Split left/right
	var left = (total_hashes / 2) -6
	var right = (total_hashes / 2) -6

	var text_uncolored = " ".repeat(left) + ""+ base_text + "" + " ".repeat(right)
	
	var index = int(round(text_uncolored.length() * (percent / 100.0)))
	var col_exp = "[bgcolor=blue][color=white]"
	var col_nor = "[bgcolor=black][color=white]"
	var text_colored = text_uncolored.insert(index, col_nor)
	
	var final_text = "[center]" + col_nor + "_.-') " + col_exp + text_colored + col_nor + " ('-._"
	label.append_text(final_text)
