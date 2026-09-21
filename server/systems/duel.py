import systems.utils
from configuration.constants.item_type import ItemType

trade_commands = {
    "with": "duel_request",  # request / acccept a duel
    "offer": "trade_offer",  # offer an item in a trade
    "cancel": "duel_stop",  # stop the trade
    "stop": "duel_stop",  # stop the trade

}

class DuelManager:
    def __init__(self, actor):
        self.actor = actor
        self.pending = None
        self.trade = None

    def duel_stop(self):
        if self.pending:
            self.actor.send_line('You cancel all pending duels')
        self.pending = None

    def duel_request(self, line):
        other = self.actor.get_actor(line)

        # dont trade if no target found
        if other == None or line == '':
            self.actor.send_line("Duel who?")
            return

        # dont trade unless they can trade
        if not hasattr(other, "duel_manager"):
            self.actor.send_line(f"You can't duel {other.pretty_name(self.actor)}")
            return

        if other == self.actor:
            self.actor.send_line("You can't duel yourself")
            return

        # dont send more requests if you are already pending
        if other == self.pending:
            self.actor.send_line(f"{self.actor.pretty_name(identifier = self.actor)} already asked {other.pretty_name(identifier = self.actor)} to duel")
            return

        # dont send requests if they are busy trading
        if other.duel_manager.trade != None:
            self.actor.send_line(f"{other.pretty_name(identifier = self.actor)} is busy")
            return

        if self.actor == other.duel_manager.pending:
            '''self.open_trade(other)'''
            self.actor.send_line(f"{self.actor.pretty_name(identifier = self.actor)} accept {other.pretty_name(self.actor)}'s duel request")
            other.send_line(f"{self.actor.pretty_name(identifier = other)} accepts the duel request")

            participants = {self.actor.id: self.actor, other.id: other}
            if self.actor.party_manager.party:
                for i in self.actor.party_manager.party.participants.values():
                    participants[i.id] = i
            if other.party_manager.party:
                for i in other.party_manager.party.participants.values():
                    participants[i.id] = i
            for i in participants.values():
                i.duel_manager.duel_stop()

            self.actor.room.combat = self.actor.room.combat_manager_class(self.actor.room, participants)
            self.actor.room.combat.pvp = True
            self.actor.room.combat.initiative()

        else:
            self.pending = other
            self.actor.send_line(
                f"{self.actor.pretty_name(identifier = self.actor)} ask {other.pretty_name(self.actor)} to duel (waiting for response)"
            )
            other.send_line(
                f'{self.actor.pretty_name(identifier = other)} asks {other.pretty_name(identifier = other)} to duel ("duel with {self.actor.pretty_name(identifier = other)}" or ignore to decline)'
            )

    def handle_duel_message(self, line):
        self.duel_stop()

        # empty lines are handled as resend last line
        if not line:
            return
        
        self.duel_request(line)
