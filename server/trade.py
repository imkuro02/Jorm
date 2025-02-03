import utils 
from configuration.config import ItemType
trade_commands = {
    'with':     'trade_request',    # request / acccept a trade
    'offer':    'trade_offer',      # offer an item in a trade
    # 'undo':     'trade_undo',       # remove item in a trade
    'accept':   'trade_accept',     # complete trade
    'look':     'trade_look',       # look at all items in trade
    'cancel':   'trade_stop',       # stop the trade
    'identify': 'trade_identify'    # identify item in trade
    
}

class TradeWindow:
    def __init__(self, trader1, trader2):
        self.trader1 = trader1
        self.trader2 = trader2
        self.offers1 = {}
        self.offers2 = {}
        self.trader1_accepted = False
        self.trader2_accepted = False

    def refresh(self):
        self.trader1_accepted = False
        self.trader2_accepted = False

    def accept(self, trader):
        if trader == self.trader1:
            self.trader1_accepted = True
        if trader == self.trader2:
            self.trader2_accepted = True

        trader.simple_broadcast('You accept the trade', f'{trader.pretty_name()} accepts the trade')

        if self.trader1_accepted and self.trader2_accepted:
            trader.simple_broadcast('Trade complete!', 'Trade complete!')
            '''
            def give_item(self, item, receiver):
                receiver.add_item(item)
                self.remove_item(item)
            '''
            for item in self.offers1.values():
                self.trader1.inventory_manager.give_item(item, self.trader2.inventory_manager)
            for item in self.offers2.values():
                self.trader2.inventory_manager.give_item(item, self.trader1.inventory_manager)
            trader.trade_manager.trade_stop(silent = True)

    def offer(self, item, trader):
        
        if trader == self.trader1:
            self.offers1[item.id] = item
            self.trader1.sendLine(f'You offer {item.name}')
            self.trader2.sendLine(f'{self.trader1.pretty_name()} offers {item.name}')
        if trader == self.trader2:
            self.offers2[item.id] = item
            self.trader2.sendLine(f'You offer {item.name}')
            self.trader1.sendLine(f'{self.trader2.pretty_name()} offers {item.name}')



class TradeManager:
    def __init__(self, actor):
        self.actor = actor
        self.pending = None
        self.trade = None
   
    def trade_request(self, line):
        other = self.actor.get_entity(line)
        # dont trade if no target found
        if other == None:
            self.actor.sendLine('Trade with who?')
            return

        # dont trade unless they can trade
        if not hasattr(other, 'trade_manager'):
            self.actor.sendLine(f'You can\'t trade with {other.pretty_name()}')
            return
        
        # dont trade with yourself :)
        if self.actor == other:
            self.actor.sendLine('You trade with you trade with you trade with you thought you broke it didn\'t you')
            return
        
        # dont send more requests if you are already pending
        if other == self.pending:
            self.actor.sendLine(f'You already asked {other.pretty_name()} to trade')
            return
        
        # dont send requests if they are busy trading
        if other.trade_manager.trade != None:
            self.actor.sendLine(f'{other.pretty_name()} is busy')
            return

        if self.actor == other.trade_manager.pending: 
            self.open_trade(other)
            self.actor.simple_broadcast(
                f'You accept {other.pretty_name()}\'s trade',
                f'{self.actor.pretty_name()} accepts your trade request!'
            )
        else:
            self.pending = other
            self.actor.simple_broadcast(
                f'You ask {other.pretty_name()} to trade (waiting for response)',
                f'{self.actor.pretty_name()} asks you to trade ("trade with {self.actor.name}" or ignore to decline)'
            )

    def open_trade(self, other):
        # reset pending trades
        self.pending = None
        other.trade_manager.pending = None
        trade_window = TradeWindow(self.actor, other) # create new trade window with the actors

        self.trade = trade_window
        other.trade_manager.trade = trade_window


    def trade_accept(self, line):
        if self.trade == None:
            self.actor.sendLine('You are not in a trade')
            return
        
        self.trade.accept(self.actor)

    def trade_offer(self, line):
        if self.trade != None:
            self.trade.refresh()
            
        item = self.actor.get_item(line)
        if item == None:
            self.actor.sendLine('Offer what?')
            return
        if item.keep:
            self.actor.sendLine('You can\'t trade kept items')
            return
        if item.item_type == ItemType.EQUIPMENT:
            if item.equiped:
                self.actor.sendLine('You can\'t trade equiped items')
                return
        self.trade.offer(item, self.actor)
        
    def trade_identify(self, line):
        inventory = {}
        for item in self.trade.offers1.values():
            inventory[item.id] = item
        for item in self.trade.offers2.values():
            inventory[item.id] = item
        item = self.actor.get_item(line, inventory = inventory)
        if item == None:
            self.actor.sendLine('Identify what?')
            return
        output = item.identify(identifier = self.actor)
        self.actor.sendLine(output)

    def trade_look(self, line):
        if self.trade == None:
            self.actor.sendLine('You are not trading right now')
            return
        
        if self.actor == self.trade.trader1:
            trader_me = self.trade.trader1
            offers_me = self.trade.offers1
            trader_other = self.trade.trader2
            offers_other = self.trade.offers2
        if self.actor == self.trade.trader2:
            trader_me = self.trade.trader2
            offers_me = self.trade.offers2
            trader_other = self.trade.trader1
            offers_other = self.trade.offers1

        output = 'You will trade \n'
        
        for of in offers_me.values():
            output += of.name + '\n'

        output += 'You will receive \n'

        for of in offers_other.values():
            output += of.name + '\n'

        #output += '"trade cancel" or "trade accept"?'
        trader_me.sendLine(output)

    #def trade_undo(self, line):
    #    print(self.actor, 'undo')

    def trade_stop(self, line = '', silent = False):
        if self.trade == None:
            if silent == False:
                self.actor.sendLine('There is no trade to cancel')
            return
        tr = self.trade 
        if silent == False:
            tr.trader1.sendLine('Trade cancelled')
            tr.trader2.sendLine('Trade cancelled')
        tr.trader1.trade_manager.trade = None
        tr.trader2.trade_manager.trade = None

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


    