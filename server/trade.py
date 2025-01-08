
trade_commands = {
    'with':     'trade_request',
    'offer':    'trade_offer',
    'undo':     'trade_undo',
    'accept':   'trade_accept',
    'cancel':   'trade_stop'
}

class TradeWindow:
    def __init__(self, t1, t2):
        # trader 1 and trader 2
        self.t1 = t1
        self.t2 = t2 
        # when both values turn True then this window will become the current trade
        self.t1ready = False
        self.t2ready = False
        # when both values turn True then the trade will happen
        self.t1accepted = False
        self.t2accepted = False

class TradeManager:
    def __init__(self, actor):
        self.actor = actor
        self.trade = None
        self.pending_trades = []
        self.current_trade = None

    def check_if_duped_trade(trade_window1, trade_window2):
        t1 = trade_window1
        for t2 in self.pending_trades:
            t2 = trade_window2

            t1_exists_in_both = False
            t2_exists_in_both = False

            if t1.t1 == t2.t1 or t1.t1 == t2.t2:
                t1_exists_in_both = True
            if t1.t2 == t2.t1 or t1.t2 == t2.t2:
                t2_exists_in_both = True

            # if both trades have the same two participants then its a duped trade
            if t1_exists_in_both and t2_exists_in_both:
                return True
        return False 

    # this function first needs to check whether you are trying to trade with someone
    # who is already trying to trade with you, if thats the case then that window becomes active
    def trade_request(line):
        other = self.actor.get_entity(line)
        if other == None:
            self.actor.sendLine('Trade with who?')
            return
        if type(other).__name__ != 'Player':
            self.actor.sendLine('Trade with who?')
            return

        print(self.actor.name, 'requested to trade with ', other.name)
        t1 = self.actor
        t2 = other
        
        trade = TradeWindow(t1 = t1, t2 = t2)

        duped = self.check_if_duped_trade(trade)
        
        if duped:
            return

        self.pending_trades.append(trade)
        other.pending_trades.append(trade)



    def trade_accept(line):
        print(self.actor, 'accepted')

    def trade_offer(line):
        print(self.actor, 'offers')

    def trade_undo(line):
        print(self.actor, 'undo')

    def trade_complete(line):
        print(self.actor, 'completed')

    def trade_stop(line):
        print(self.actor, 'cancels')


    def handle_trade_message(self, line):
        # empty lines are handled as resend last line
        if not line: 
            line = self.last_line_sent
            if not line:
                return

        

        
        best_match, best_score = utils.match_word(command, commands.keys(), get_score = True)
        if best_score < 75:
            self.actor.sendLine(f'You wrote "{command}" did you mean "{best_match}"?\nUse "help trade" to learn more about this command.')
            return

        
        script = getattr(self, commands[best_match])
        self.last_command_used = best_match
        script(line)


    