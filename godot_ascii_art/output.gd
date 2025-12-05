extends RichTextLabel



# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func get_message(message):
	self.clear()
	self.append_text(add_ansi_text(message))
	self.scroll_following = true
	
func add_ansi_text(ansi_text: String) -> String:
	var ansi_to_fg = {
		"@black": "#000000", # black
		"@red": "#AA0000", # red
		"@green": "#00AA00", # green
		"@yellow": "#CCCC00", # yellow (less brown, more true yellow)
		"@blue": "#0033CC", # blue (brighter than #0000AA)
		"@purple": "#AA00AA", # magenta
		"@cyan": "#00AAAA", # cyan
		"@white": "#AAAAAA", # light gray / white
		
		"@bblack": "#555555", # bright black / gray
		"@bred": "#FF5555", # bright red
		"@bgreen": "#55FF55", # bright green
		"@byellow": "#FFFF55", # bright yellow
		"@bblue": "#3388FF", # bright blue (lighter than before)
		"@bpurple": "#FF55FF", # bright magenta
		"@bcyan": "#55FFFF", # bright cyan
		"@bwhite": "#FFFFFF", # bright white
	}

	
	var codes = ansi_to_fg 
	var output = ansi_text
	for i in codes:
		var color = "[color=%s]" % [codes[i]]
		output = output.replace(i,color)

	return output
