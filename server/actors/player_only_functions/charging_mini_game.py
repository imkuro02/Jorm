from actors.player_only_functions.checks import check_not_in_combat

@check_not_in_combat
def command_charging_mini_game_toggle(self, line):
    self.charging_mini_game.toggle()