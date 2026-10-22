import random
class Audio:
    PLAYER_DEATH = "die1.wav"
    ENEMY_DEATH = "die.wav"
    BUFF = "buff2.wav"
    WALK = "walk1.wav"
    HURT = "pot-hit.wav"
    ERROR = "error.wav"
    ITEM_GET = "item_get.mp3"
    ITEM_DROP = "item_drop.mp3"
    FIREPLACE = "fireplace.wav"
    BREAK_PHYARMOR = 'armor_break.mp3'
    BREAK_MAGARMOR = 'magic_descend.mp3'
    EAT = 'eating.mp3'
    DRINK = 'potion.wav'

    DAMAGE_MAGIC_DEALT = 'damage_magic_dealt.mp3'
    DAMAGE_PURE_DEALT = 'damage_magic_dealt.mp3'
    DAMAGE_PHYSICAL_DEALT = "pot-hit.wav"
    DAMAGE_HEALING_DEALT = "buff.wav"

    def walk():
        return random.choice(["walk1.wav", "walk2.wav", "walk3.wav"])