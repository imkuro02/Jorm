extends AudioStreamPlayer
var states = {
	'Normal': "res://audio/music/enneagon/10 Sure Is Dark In Here.ogg",
	'Fighting': "res://audio/music/enneagon/19 Counterfeit Finale.ogg",
	'Dead': "res://audio/music/alvin/N A W A K - FOREST.mp3",
	'Menu': "res://audio/music/alvin/N A W A K - FOREST.mp3"
}

# Called when the node enters the scene tree for the first time.
func _ready():
	stream.loop = true
	pass # Replace with function body.


func change_state(state):
	if load(states[state]) != stream:
		stream = load(states[state])
		play()


