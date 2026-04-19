from actors.player_only_functions.checks import check_no_empty_line, check_not_spamming
from actors.player_only_functions import emote_presets
import random
from configuration.constants.message_type import MessageType
@check_no_empty_line
@check_not_spamming
def command_say(self, line):
    line = line + '@back'
    #print(line)
    self.simple_broadcast(
        f'You say "@cyan{line}@normal"',
        f'{self.pretty_name()} says "@cyan{line}@normal"@normal',
        msg_type = [MessageType.SAY, MessageType.CHAT],
        sound = 'notif1.wav')

@check_no_empty_line
@check_not_spamming
def command_shout(self, line):
    line = line + '@back'
    self.simple_broadcast(
        f'You shout "@cyan{line}@normal"',
        f'{self.pretty_name()} shouts "@cyan{line}@normal" from "{self.room.pretty_name()}@normal"',
        send_to = 'world', msg_type = [MessageType.SHOUT, MessageType.CHAT],
        sound = 'notif1.wav')

@check_not_spamming
def command_emote(self, line):
    emotes = emote_presets.emotes

    line = line.split()
    emote = None
    if len(line) >= 1:
        emote = line[0]
    if emote not in emotes:
        self.send_line(f'Here is a list of emotes: {[e for e in emotes.keys()]}')
        return
    target = None
    
    if len(line) >= 2:
        target_actor = self.get_actor(line[1])
        target_item = self.get_item(line[1], search_mode = 'self_and_room')
    
        if target_item != None:
            target = target_item[0]
        if target_actor != None:
            target = target_actor
    
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
        perspectives[perspective] = perspectives[perspective].replace('#USER#', self.id)
        perspectives[perspective] = perspectives[perspective].replace('#OTHER#', target.id)


    list_pretty_name_objects = [self, target]

    
    for receiver in self.room.actors.values():
        if type(receiver).__name__ != "Player":
            continue

        if receiver == self and receiver == target:
            _p = perspectives['you on you']
            receiver.pretty_broadcast(line_self = _p, line_others = '', send_to="room", sound=None, msg_type=None, list_pretty_name_objects = list_pretty_name_objects)
            #receiver.send_line(perspectives['you on you'])
            continue
        if receiver == self and receiver != target:
            _p = perspectives['you on other']
            receiver.pretty_broadcast(line_self = _p, line_others = '', send_to="room", sound=None, msg_type=None, list_pretty_name_objects = list_pretty_name_objects)
            #receiver.send_line(perspectives['you on other'])
            continue
        if receiver != self and receiver != target and self == target:
            _p = perspectives['user on user']
            receiver.pretty_broadcast(line_self = _p, line_others = '', send_to="room", sound=None, msg_type=None, list_pretty_name_objects = list_pretty_name_objects)
            #receiver.send_line(perspectives['user on user'])
            continue
        if receiver != self and receiver == target:
            _p = perspectives['user on you']
            receiver.pretty_broadcast(line_self = _p, line_others = '', send_to="room", sound=None, msg_type=None, list_pretty_name_objects = list_pretty_name_objects)
            #receiver.send_line(perspectives['user on you'])
            continue
        if receiver != self and receiver != target:
            _p = perspectives['you on other']
            receiver.pretty_broadcast(line_self = _p, line_others = '', send_to="room", sound=None, msg_type=None, list_pretty_name_objects = list_pretty_name_objects)
            #receiver.send_line(perspectives['user on other'])
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
            self.send_line('The roll argument must be an intiger')
            return
    else:
        rmax = 100

    if rmax <= 0:
        self.send_line('The roll argument must be 1 or higher')
        return

    roll = random.randint(rmin,rmax)
    self.simple_broadcast(
        f'You roll: @green{roll}/{rmax}@normal',
        f'{self.pretty_name()} rolls: @green{roll}/{rmax}@normal')
