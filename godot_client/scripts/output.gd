extends RichTextLabel



# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func get_message(message):
	
	self.append_text(add_ansi_text(message))
	self.scroll_following = true
	
func add_ansi_text(ansi_text: String) -> String:
	var ansi_to_fg = {
		"30": "#000000", # black
		"31": "#AA0000", # red
		"32": "#00AA00", # green
		"33": "#CCCC00", # yellow (less brown, more true yellow)
		"34": "#0033CC", # blue (brighter than #0000AA)
		"35": "#AA00AA", # magenta
		"36": "#00AAAA", # cyan
		"37": "#AAAAAA", # light gray / white
	}

	var ansi_to_fg_bright = {
		"30": "#555555", # bright black / gray
		"31": "#FF5555", # bright red
		"32": "#55FF55", # bright green
		"33": "#FFFF55", # bright yellow
		"34": "#3388FF", # bright blue (lighter than before)
		"35": "#FF55FF", # bright magenta
		"36": "#55FFFF", # bright cyan
		"37": "#FFFFFF", # bright white
	}

	var ansi_to_bg = {
		"40": "#000000",
		"41": "#AA0000",
		"42": "#00AA00",
		"43": "#AA5500",
		"44": "#0000AA",
		"45": "#AA00AA",
		"46": "#00AAAA",
		"47": "#AAAAAA",
	}

	var ansi_to_bg_bright = {
		"40": "#555555",
		"41": "#FF5555",
		"42": "#55FF55",
		"43": "#FFFF55",
		"44": "#5555FF",
		"45": "#FF55FF",
		"46": "#55FFFF",
		"47": "#FFFFFF",
	}

	var pattern := RegEx.new()
	pattern.compile(r"\x1b\[([0-9;]*)m")

	var output := ""
	var last_index := 0
	var current_fg := ""
	var current_bg := ""
	var bright := false

	for match in pattern.search_all(ansi_text):
		var start := match.get_start()
		var end := match.get_end()
		var codes_str := match.get_string(1)
		var codes := codes_str.split(";")

		# Emit text before ANSI
		var pre_text := ansi_text.substr(last_index, start - last_index)
		if pre_text != "":
			var wrapped := pre_text
			if current_fg != "":
				wrapped = "[color=%s]%s[/color]" % [current_fg, wrapped]
			if current_bg != "":
				wrapped = "[bgcolor=%s]%s[/bgcolor]" % [current_bg, wrapped]
			output += wrapped

		# Parse ANSI codes
		for c in codes:
			match c:
				"0":
					current_fg = ""
					current_bg = ""
					bright = false
				"1":
					bright = true
				"2":
					bright = false
				_:
					if ansi_to_fg.has(c):
						if bright:
							current_fg = ansi_to_fg_bright[c]
						else:
							current_fg = ansi_to_fg[c]
					elif ansi_to_bg.has(c):
						if bright:
							current_bg = ansi_to_bg_bright[c]
						else:
							current_bg = ansi_to_bg[c]

		last_index = end

	# Remaining text
	var remaining := ansi_text.substr(last_index)
	if remaining != "":
		var wrapped := remaining
		if current_fg != "":
			wrapped = "[color=%s]%s[/color]" % [current_fg, wrapped]
		if current_bg != "":
			wrapped = "[bgcolor=%s]%s[/bgcolor]" % [current_bg, wrapped]
		output += wrapped

	return output
