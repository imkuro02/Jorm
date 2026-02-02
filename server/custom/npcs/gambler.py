import random

from actors.npcs import Npc
from items.manager import load_item
from systems.dialog import Dialog


class gambling_dialog(Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.to_gamble = 0
        self.is_gambling = False
        self.npc.dialogs[self] = self
        self.ticks = 0
        self.rolls = []

    def end_gambling(self):
        if self in self.npc.dialogs:
            del self.npc.dialogs[self]
        if self.is_gambling:
            self.npc.simple_broadcast(
                f"",
                f'{self.npc.pretty_name()} says "{self.player.pretty_name()} I dont tolerate cheap tactics, im keeping your money"',
            )
            return super().end_dialog()
        self.give_back_money()
        return super().end_dialog()

    def end_dialog(self, forced = 0):
        if self.current_line != "propose_bid" or forced == 1:
            self.player.sendLine('END')
            self.end_gambling()
            return super().end_dialog()

    def give_back_money(self):
        if self.to_gamble != 0:
            new_item = load_item("currency_0")
            new_item.stack = self.to_gamble
            self.player.inventory_manager.add_item(new_item, forced=True)

    def answer(self, line):
        if self.current_line != "propose_bid":
            return super().answer(line)

        try:
            line = int(line)
        except ValueError:
            self.end_dialog(1)
            return False

        if line <= 0:
            self.end_dialog(1)
            return True

        if self.is_gambling:
            self.npc.simple_broadcast(
                f"",
                f'{self.npc.pretty_name()} says "{self.player.pretty_name()} You can\'t change your bid now"',
            )
            return True

        self.to_gamble = line
        if not self.player.inventory_manager.remove_items_by_id(
            "currency_0", self.to_gamble
        ):
            # self.end_gambling()
            # super().end_dialog()
            self.player.simple_broadcast(
                f"You bid {self.to_gamble} scrap",
                f"{self.player.pretty_name()} bids {self.to_gamble} scrap",
            )
            self.npc.simple_broadcast(
                "",
                f'"{self.player.pretty_name()} Im not stupid.." says {self.npc.pretty_name()}. "You don\'t have enough scrap"',
            )
            self.to_gamble = 0
            self.end_gambling()
            super().end_dialog()
            return True

        self.player.simple_broadcast(
            f"You bid {self.to_gamble} scrap",
            f"{self.player.pretty_name()} bids {self.to_gamble} scrap",
        )
        self.is_gambling = True
        return True

    def tick(self):
        # if self.npc not in self.player.room.actors.values():
        #    self.end_gambling()
        #    super().end_dialog()
        #    return

        pause_time = 30
        if self.is_gambling == False:
            self.ticks = 0
            return

        self.ticks += 1

        if self.ticks == 0:
            self.npc.simple_broadcast(
                "",
                f"{self.npc.pretty_name()} takes {self.to_gamble} scrap",
            )
            return

        if self.ticks in [pause_time, pause_time * 2, pause_time * 3]:
            roll = random.randint(1, 6)
            self.rolls.append(roll)
            if len(self.rolls) >= 3:
                return

            self.player.simple_broadcast(
                f"{self.npc.pretty_name()} rolls a {roll}!",
                f"{self.npc.pretty_name()} rolls a {roll}",
            )
            return

        if self.ticks >= pause_time * 3:
            self.player.simple_broadcast(
                f'{self.npc.pretty_name()} says "a {self.rolls[0]}, {self.rolls[1]} and a {self.rolls[2]}"!',
                f'{self.npc.pretty_name()} says "a {self.rolls[0]}, {self.rolls[1]} and a {self.rolls[2]}"',
            )

            duplicates = len(self.rolls) - len(set(self.rolls)) + 1
            output = "ERROR"
            match duplicates:
                case 1:
                    duplicates = 0
                    output = 'says "No dice!" and keeps the scrap'
                case 2:
                    output = 'says "You rolled a dupe" You get back double the scrap'
                case 3:
                    output = 'says "Three in a row..." You get back tripple the scrap'

            self.to_gamble = self.to_gamble * duplicates

            self.player.simple_broadcast(
                f"{self.npc.pretty_name()} {output}!",
                f"{self.npc.pretty_name()} {output}",
            )

            self.give_back_money()
            self.to_gamble = 0
            self.is_gambling = False


class gambling(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        if "gambling_0" not in npc_object.npc_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_exisiting = 0
        self.dialog_manager = gambling_dialog
        self.actors = len(self.room.actors.values())
        self.dialogs = {}

        self.trigger_manager.trigger_add(trigger_key = 'gamble', trigger_action = self.trigger_gamble)
        self.description += '\nYou can "gamble <amount>" to skip the chitchat.'

    def trigger_gamble(self, player, line):
        if len(line.split())!=2:
            player.sendLine(f'{self.pretty_name()} says "If you want to gamble, either talk to me, or "gamble <amount>""')
            return True
        self.talk_to(player)
        player.current_dialog.answer('1')
        player.current_dialog.answer(line.split()[1])
        return True

    def tick(self):
        super().tick()
        for i in self.dialogs.values():
            i.tick()
