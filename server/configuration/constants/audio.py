import random
class Audio:
    PLAYER_DEATH = "die1.wav"
    ENEMY_DEATH = "die.wav"
    BUFF = "buff.wav"
    WALK = "walk1.wav"
    HURT = "pot-hit.wav"
    ERROR = "error.wav"
    ITEM_GET = "item_get.mp3"
    ITEM_DROP = "item_drop.mp3"
    FIREPLACE = "fireplace.wav"

    def walk():
        return random.choice(["walk1.wav", "walk2.wav", "walk3.wav"])