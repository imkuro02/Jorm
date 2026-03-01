import systems.utils
from configuration.constants.item_type import ItemType

trade_commands = {
    "with": "trade_request",  # request / acccept a trade
    "offer": "trade_offer",  # offer an item in a trade
    # 'undo':     'trade_undo',       # remove item in a trade
    "accept": "trade_accept",  # complete trade
    "look": "trade_look",  # look at all items in trade
    "cancel": "trade_stop",  # stop the trade
    "identify": "trade_identify",  # identify item in trade
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

        trader.simple_broadcast(
            "You accept the trade", f"{trader.pretty_name()} accepts the trade"
        )

        if self.trader1_accepted and self.trader2_accepted:
            trader.simple_broadcast("Trade complete!", "Trade complete!")
            """
            def give_item(self, item, receiver):
                receiver.add_item(item)
                self.remove_item(item)
            """
            for item in self.offers1.values():
                self.trader1.inventory_manager.give_item(
                    item, self.trader2.inventory_manager
                )
            for item in self.offers2.values():
                self.trader2.inventory_manager.give_item(
                    item, self.trader1.inventory_manager
                )
            trader.trade_manager.trade_stop(silent=True)

    def offer(self, item, trader):
        if trader == self.trader1:
            self.offers1[item.id] = item
            self.trader1.send_line(f"You offer {item.pretty_name(self.trader1)}")
            self.trader2.send_line(
                f"{self.trader1.pretty_name(self.trader2)} offers {item.pretty_name(self.trader2)}"
            )
        if trader == self.trader2:
            self.offers2[item.id] = item
            self.trader2.send_line(f"You offer {item.pretty_name(self.trader2)}")
            self.trader1.send_line(
                f"{self.trader2.pretty_name(self.trader2)} offers {item.pretty_name(self.trader2)}"
            )


class TradeManager:
    def __init__(self, actor):
        self.actor = actor
        self.pending = None
        self.trade = None

    def trade_request(self, line):
        other = self.actor.get_actor(line)

        # dont trade if no target found
        if other == None:
            self.actor.send_line("Trade with who?")
            return

        # dont trade unless they can trade
        if not hasattr(other, "trade_manager"):
            self.actor.send_line(f"You can't trade with {other.pretty_name(self.actor)}")
            return

        # dont trade with yourself :)
        if self.actor == other:
            self.actor.send_line(
                "You trade with you trade with you trade with you thought you broke it didn't you"
            )
            return

        # dont send more requests if you are already pending
        if other == self.pending:
            self.actor.send_line(f"You already asked {other.pretty_name(self.actor)} to trade")
            return

        # dont send requests if they are busy trading
        if other.trade_manager.trade != None:
            self.actor.send_line(f"{other.pretty_name()} is busy")
            return

        if self.actor == other.trade_manager.pending:
            self.open_trade(other)
            self.actor.send_line(f"You accept {other.pretty_name(self.actor)}'s trade")
            other.send_line(f"{self.actor.pretty_name()} accepts your trade request!")
        else:
            self.pending = other
            self.actor.send_line(
                f"You ask {other.pretty_name(self.actor)} to trade (waiting for response)"
            )
            other.send_line(
                f'{self.actor.pretty_name(other)} asks you to trade ("trade with {self.actor.pretty_name(other)}" or ignore to decline)'
            )

    def open_trade(self, other):
        # reset pending trades
        self.pending = None
        other.trade_manager.pending = None
        trade_window = TradeWindow(
            self.actor, other
        )  # create new trade window with the actors

        self.trade = trade_window
        other.trade_manager.trade = trade_window

    def trade_accept(self, line):
        if self.trade == None:
            self.actor.send_line("You are not in a trade")
            return

        self.trade.accept(self.actor)

    def trade_offer(self, line):
        if self.trade == None:
            self.actor.send_line("You are not in a trade")
            return
        self.trade.refresh()

        items = self.actor.get_item(line)
        for item in items:
            if item == None:
                self.actor.send_line("Offer what?")
                return
            if not item.can_tinker_with():
                self.actor.send_line("Cannot trade kept or equipped items")
                continue
            self.trade.offer(item, self.actor)

    def trade_identify(self, line):
        inventory = {}
        for item in self.trade.offers1.values():
            inventory[item.id] = item
        for item in self.trade.offers2.values():
            inventory[item.id] = item
        items = self.actor.get_item(line, inventory=inventory)
        if items == None:
            self.actor.send_line("Identify what?")
            return
        for item in items:
            output = item.identify(identifier=self.actor)
            self.actor.send_line(output)

    def trade_look(self, line):
        if self.trade == None:
            self.actor.send_line("You are not trading right now")
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

        output = "You will trade \n"

        for of in offers_me.values():
            output += of.pretty_name(self.actor) + "\n"

        output += "You will receive \n"

        for of in offers_other.values():
            output += of.pretty_name(self.actor) + "\n"

        # output += '"trade cancel" or "trade accept"?'
        trader_me.send_line(output)

    # def trade_undo(self, line):
    #    systems.utils.debug_print(self.actor, 'undo')

    def trade_stop(self, line="", silent=False):
        if self.trade == None:
            if silent == False:
                self.actor.send_line("There is no trade to cancel")
            return
        tr = self.trade
        if silent == False:
            tr.trader1.send_line("Trade cancelled")
            tr.trader2.send_line("Trade cancelled")
        tr.trader1.trade_manager.trade = None
        tr.trader2.trade_manager.trade = None

    def handle_trade_message(self, line):
        # empty lines are handled as resend last line
        if not line:
            return

        command = line.split()[0]
        line = " ".join(line.split()[1::]).strip()

        best_match, best_score = systems.utils.match_word(
            command, trade_commands.keys(), get_score=True
        )
        if best_score < 75:
            self.actor.send_line(
                f'You wrote "{command}" did you mean "{best_match}"?\nUse "help trade" to learn more about this command.'
            )
            return

        script = getattr(self, trade_commands[best_match])
        script(line)
