extends AudioStreamPlayer
var states = {
	'Normal': "res://audio/music/enneagon/10 Sure Is Dark In Here.ogg",
	'Fighting': "res://audio/music/enneagon/19 Counterfeit Finale.ogg",
	'Dead': "res://audio/music/alvin/N A W A K - FOREST.mp3",
	'Menu': "res://audio/music/alvin/N A W A K - FOREST.mp3"
}
@onready var MAIN = $".."
@onready var current_song = states['Menu']
@onready var vol_music = 100
@onready var vol_master = 100
@onready var vol_desired = 0

func _ready():
	stream.loop = true
	change_state('Menu')
	
	
var last_desired = 0
func _process(_delta):
	#vol_music = MAIN.vol_music
	#vol_master = MAIN.vol_master
	vol_desired = ((vol_master/10) + (vol_music/10)) - 15
	if vol_desired == last_desired:
		return
	last_desired = vol_desired
	volume_db = last_desired
	print(volume_db)
	
	

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

		tween.tween_property(self, "volume_db", vol_desired, 0)
		
			

