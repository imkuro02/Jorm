extends ColorRect

# Define your two key colors
var night_color := Color(0.05, 0.1, 0.2)  
var day_color   := Color(0.145, 0.27, 0.301)

# Current in-game time (0–24)
var game_hour: float = 0.0


func get_message(data):
	var t := absf(((int(data['hour']) - 12.0) / 12.0))  # 0 at noon, 1 at midnight
	# Lerp between day and night
	var blended_color := day_color.lerp(night_color, t)
	color = blended_color   # if this script is on a Control node
	#color = blended_color


