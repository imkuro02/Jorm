from actors.player_only_functions.checks import check_no_empty_line
@check_no_empty_line
def command_say(self, line):
    self.simple_broadcast(
        f'You say "{line}"',
        f'{self.pretty_name()} says "{line}"'
        )