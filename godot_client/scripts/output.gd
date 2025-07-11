extends RichTextLabel


@onready var OUTPUT = self

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func get_message(message):
	
	OUTPUT.append_text(add_ansi_text(message))
	OUTPUT.scroll_following = true
	
func add_ansi_text(ansi_text: String) -> String:
	var ansi_to_fg = {
		"30": "black",
		"31": "red",
		"32": "green",
		"33": "yellow",
		"34": "blue",
		"35": "magenta",
		"36": "cyan",
		"37": "white",
		"90": "gray"
	}
	
	var ansi_to_bg = {
		"40": "black",
		"41": "red",
		"42": "green",
		"43": "yellow",
		"44": "blue",
		"45": "magenta",
		"46": "cyan",
		"47": "white",
		"100": "gray"
	}

	var output = ""
	var current_fg = ""
	var current_bg = ""
	var pattern = RegEx.new()
	pattern.compile(r"\x1b\[([0-9;]+)m")
	
	var last_index = 0
	for match in pattern.search_all(ansi_text):
		var start = match.get_start()
		var end = match.get_end()
		var code_str = match.get_string(1)
		var codes = code_str.split(";")
		
		# Text before this ANSI code
		var pre_text = ansi_text.substr(last_index, start - last_index)
		if pre_text != "":
			var wrapped_text = pre_text
			if current_fg != "":
				wrapped_text = "[color=%s]%s[/color]" % [current_fg, wrapped_text]
			if current_bg != "":
				wrapped_text = "[bgcolor=%s]%s[/bgcolor]" % [current_bg, wrapped_text]
			output += wrapped_text

		# Parse ANSI codes
		for c in codes:
			if c == "0":
				current_fg = ""
				current_bg = ""
			elif ansi_to_fg.has(c):
				current_fg = ansi_to_fg[c]
			elif ansi_to_bg.has(c):
				current_bg = ansi_to_bg[c]

		last_index = end
	
	# Remaining text
	var remaining_text = ansi_text.substr(last_index)
	if remaining_text != "":
		var wrapped_text = remaining_text
		if current_fg != "":
			wrapped_text = "[color=%s]%s[/color]" % [current_fg, wrapped_text]
		if current_bg != "":
			wrapped_text = "[bgcolor=%s]%s[/bgcolor]" % [current_bg, wrapped_text]
		output += wrapped_text
	

	return output
