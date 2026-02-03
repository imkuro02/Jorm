from actors.player_only_functions.checks import check_no_empty_line, check_not_spamming
from actors.player_only_functions import emote_presets
import random
from configuration.config import MsgType
@check_no_empty_line
@check_not_spamming
def command_say(self, line):
    line = line + '@back'
    #print(line)
    self.simple_broadcast(
        f'You say "@cyan{line}@normal"',
        f'{self.pretty_name()} says "@cyan{line}@normal"@normal',
        msg_type = [MsgType.SAY, MsgType.CHAT])

@check_no_empty_line
@check_not_spamming
def command_shout(self, line):
    line = line + '@back'
    self.simple_broadcast(
        f'You shout "@cyan{line}@normal"',
        f'{self.pretty_name()} shouts "@cyan{line}@normal" from "{self.room.pretty_name()}@normal"',
        send_to = 'world', msg_type = [MsgType.SHOUT, MsgType.CHAT])

@check_not_spamming
def command_emote(self, line):
    emotes = emote_presets.emotes

    line = line.split()
    emote = None
    if len(line) >= 1:
        emote = line[0]
    if emote not in emotes:
        self.sendLine(f'Here is a list of emotes: {[e for e in emotes.keys()]}')
        return
    target = None
    if len(line) >= 2:
        target = self.get_actor(line[1])
    if target == None:
        target = self





    perspectives = {
        'you on you':       emotes[emote]['you on you'],
        'you on other':     emotes[emote]['you on other'],
        'user on user':     emotes[emote]['user on user'],
        'user on you':      emotes[emote]['user on you'],
        'user on other':    emotes[emote]['user on other']
    }

    for perspective in perspectives:
        perspectives[perspective] = perspectives[perspective].replace('#USER#', self.pretty_name())
        perspectives[perspective] = perspectives[perspective].replace('#OTHER#', target.pretty_name())

    for receiver in self.room.actors.values():
        if type(receiver).__name__ != "Player":
            continue

        if receiver == self and receiver == target:
            receiver.sendLine(perspectives['you on you'])
            continue
        if receiver == self and receiver != target:
            receiver.sendLine(perspectives['you on other'])
            continue
        if receiver != self and receiver != target and self == target:
            receiver.sendLine(perspectives['user on user'])
            continue
        if receiver != self and receiver == target:
            receiver.sendLine(perspectives['user on you'])
            continue
        if receiver != self and receiver != target:
            receiver.sendLine(perspectives['user on other'])
            continue
    return


@check_not_spamming
def command_roll(self, line):
    rmin = 0
    rmax = 100_000

    if line != '':
        try:
            line = int(line)
            rmax = line
        except Exception as e:
            self.sendLine('The roll argument must be an intiger')
            return
    else:
        rmax = 100

    if rmax <= 0:
        self.sendLine('The roll argument must be 1 or higher')
        return

    roll = random.randint(rmin,rmax)
    self.simple_broadcast(
        f'You roll: @green{roll}/{rmax}@normal',
        f'{self.pretty_name()} rolls: @green{roll}/{rmax}@normal')
