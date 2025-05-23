from actors.player_only_functions.checks import check_no_empty_line, check_not_spamming
import random

@check_no_empty_line
@check_not_spamming
def command_say(self, line):
    self.simple_broadcast(
        f'You say "{line}"',
        f'{self.pretty_name()} says "{line}"'
        )

@check_no_empty_line
@check_not_spamming
def command_shout(self, line):
    self.simple_broadcast(
        f'You shout "{line}"',
        f'{self.pretty_name()} shouts from {self.room.name} "{line}"',
        worldwide = True)

'''
emotes = {
    'sing': ['You sing', '#USER# sings']
}
@check_no_empty_line
@check_not_spamming
def command_emote(self, line):
    words = line.split()
    match words[0]:
        case 'sing'
'''

@check_no_empty_line
@check_not_spamming
def command_emote(self, line):
    return


@check_no_empty_line
@check_not_spamming
def command_roll(self, line):
    rmin = 0
    rmax = 100

    if line != '':
        try:
            line = int(line)
            rmax = line
        except Exception as e:
            self.sendLine('The roll argument must be an intiger')
            return

    if rmax <= 0:
        self.sendLine('The roll argument must be 1 or higher')
        return

    roll = random.randint(rmin,rmax)
    self.simple_broadcast(
        f'You roll: @green{roll}/{rmax}@normal',
        f'{self.pretty_name()} rolls: @green{roll}/{rmax}@normal')
    