extends AudioStreamPlayer
var states = {
	'Normal': "res://audio/music/enneagon/10 Sure Is Dark In Here.ogg",
	'Fighting': "res://audio/music/enneagon/19 Counterfeit Finale.ogg",
	'Dead': "res://audio/music/alvin/N A W A K - FOREST.mp3",
	'Menu': "res://audio/music/alvin/N A W A K - FOREST.mp3"
}

var current_song = states['Menu']

func _ready():
	stream.loop = true
	change_state('Menu')
	
	

func change_state(state):
	if load(states[state]) != stream:
		
		var _time1 = 0.0
		var _time2 = 0.0
		if state != 'Fighting':
			_time1 = 0.5
			_time2 = 1.0
			
		var tween = create_tween()

		tween.tween_property(self, "volume_db", -40.0, _time1)
		#tween.tween_interval(3.0)

		tween.tween_callback(func():
			stream = load(states[state])
			play()
			stream.loop = true
		)

		tween.tween_property(self, "volume_db", 0.0, 0)
		
			

