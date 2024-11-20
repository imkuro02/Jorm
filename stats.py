class Stats:
    def __init__(self):
        pass

    def convert_to_dict(self):
        return {
            'hp': self.hp
            'mp': self.mp
            'hp_max': self.hp_max
            'hp_'
        }
class EnemyStats(Stats):
    def __init__(self):
        pass

class PlayerStats(Stats):
    def __init__(self, 
                hp, mp, hp_max, mp_max, 
                _str, _dex, _int, _luk, 
                armor, marmor, damage, 
                level, exp, points):
        self.hp = hp
        self.mp = mp
        self.hp_max = hp_max
        self.mp_max = mp_max

        self.str = _str
        self.dex = _dex
        self.int = _int
        self.luk = _luk

        self.armor = armor
        self.marmor = marmor
        self.damage = damage

        self.level = level
        self.exp = exp
        self.points

    
