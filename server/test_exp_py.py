def get_exp_needed_to_level(lvl):
    l = lvl + 1
    exp_needed = int(
        3 + (l**3.55075)
    )  # int(2 ** self.stat_manager.stats[StatType.LVL]) + (self.stat_manager.stats[StatType.LVL]*self.stat_manager.stats[StatType.LVL])
    return exp_needed

for i in range(0,30):
    print(f'{i}'.rjust(3),get_exp_needed_to_level(i))