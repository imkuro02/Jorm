from actors.player_only_functions.checks import check_no_empty_line
@check_no_empty_line
def command_say(self, line):
    self.recently_send_message_count += 100
    if self.recently_send_message_count >= 500:
        if self.recently_send_message_count >= 1000: self.recently_send_message_count = 1000
        return
    self.simple_broadcast(
        f'You say "{line}"',
        f'{self.pretty_name()} says "{line}"'
        )

def command_shout(self, line):
    self.recently_send_message_count += 100
    if self.recently_send_message_count >= 500:
        if self.recently_send_message_count >= 1000: self.recently_send_message_count = 1000
        return
    self.simple_broadcast(
        f'You shout "{line}"',
        f'{self.pretty_name()} shouts from {self.room.name} "{line}"',
        worldwide = True)

import random
def command_roll(self, line):
    self.recently_send_message_count += 100
    if self.recently_send_message_count >= 500:
        if self.recently_send_message_count >= 1000: self.recently_send_message_count = 1000
        return
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
        f'You roll: @green{roll}@normal',
        f'{self.pretty_name()} rolls: @green{roll}@normal')
    