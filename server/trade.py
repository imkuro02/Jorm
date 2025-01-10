import utils 

trade_commands = {
    'with':     'trade_request',
    'offer':    'trade_offer',
    'undo':     'trade_undo',
    'accept':   'trade_accept',
    'cancel':   'trade_stop'
}

class TradeManager:
    def __init__(self, actor):
        self.actor = actor
   
    def trade_request(self, line):
        other = self.actor.get_entity(line)
        if other == None:
            self.actor.sendLine('Trade with who?')
            return

        #if type(other) != 'Player':
        #    self.actor.sendLine('Trade with who?')
        #    return

        self.actor.sendLine(f'You trade with {other.pretty_name()}')
        print(self.actor.name, 'trade requests', other.name)

    def trade_accept(self, line):
        print(self.actor, 'accepted')

    def trade_offer(self, line):
        print(self.actor, 'offers')

    def trade_undo(self, line):
        print(self.actor, 'undo')

    def trade_complete(self, line):
        print(self.actor, 'completed')

    def trade_stop(self, line):
        print(self.actor, 'cancels')


    def handle_trade_message(self, line):
        # empty lines are handled as resend last line
        if not line: 
            return

        command = line.split()[0]
        line = " ".join(line.split()[1::]).strip()

        best_match, best_score = utils.match_word(command, trade_commands.keys(), get_score = True)
        if best_score < 75:
            self.actor.sendLine(f'You wrote "{command}" did you mean "{best_match}"?\nUse "help trade" to learn more about this command.')
            return

        
        script = getattr(self, trade_commands[best_match])
        script(line)


    