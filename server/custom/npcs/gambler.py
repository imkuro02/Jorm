import random
import os
import json
from actors.npcs import Npc
from items.manager import load_item
from systems.dialog import Dialog
from configuration.constants.tickrate import TICKRATE

EARNINGS_DATA_LOCATION = 'database/gambling_earnings.json'

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
            list_pretty_name_objects = [self.npc, self.player]
            self.npc.pretty_broadcast(
                f"",
                f'{self.npc.id} says "{self.player.id}, I dont tolerate cheap tactics, im keeping your money"',
                list_pretty_name_objects = list_pretty_name_objects
            )
            return super().end_dialog()
        self.give_back_money()
        return super().end_dialog()

    def end_dialog(self, forced = 0):
        if self.current_line != "propose_bid" or forced == 1:
            #self.player.send_line('END')
            self.end_gambling()
            return super().end_dialog()

    def save_earnings(self):
        filename = EARNINGS_DATA_LOCATION
        if not os.path.exists(filename):
            # create file with default content
            with open(filename, "w") as f:
                json.dump({"from_file": str(__file__), "earnings": 0}, f)

        # now read the file
        with open(filename, "r") as f:
            earnings_data = json.load(f)

        earnings_data['earnings'] = self.npc.earnings

        with open(filename, "w") as f:
            json.dump(earnings_data, f, indent=4)

    def give_back_money(self):
        if self.to_gamble != 0:
            new_item = load_item("currency_0")
            new_item.stack = self.to_gamble
            self.player.inventory_manager.add_item(new_item, forced=True)
            self.npc.earnings -= self.to_gamble
            self.save_earnings()

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
            list_pretty_name_objects = [self.npc, self.player]
            self.npc.pretty_broadcast(
                f"",
                f'{self.npc.id} says "{self.player.id} You can\'t change your bid now"',
                list_pretty_name_objects = list_pretty_name_objects
            )
            return True

        self.to_gamble = line
        if not self.player.inventory_manager.remove_items_by_id(
            "currency_0", self.to_gamble
        ):
            # self.end_gambling()
            # super().end_dialog()
            list_pretty_name_objects = [self.player, self.npc]
            self.player.pretty_broadcast(
                f"{self.player.id} bid {self.to_gamble} scrap",
                f"{self.player.id} bids {self.to_gamble} scrap",
                list_pretty_name_objects = list_pretty_name_objects
            )
            self.player.pretty_broadcast(
                f'"{self.player.pretty_name(identifier = self.player, text_override = self.player.name)} Im not stupid.." says {self.npc.id}. "{self.player.id} don\'t have enough scrap"',
                f'"{self.player.id} Im not stupid.." says {self.npc.id}. "You don\'t have enough scrap"',
                list_pretty_name_objects = list_pretty_name_objects
            )
            self.to_gamble = 0
            self.end_gambling()
            super().end_dialog()
            return True

        list_pretty_name_objects = {self.player}
        self.player.pretty_broadcast(
            f"{self.player.id} bid {self.to_gamble} scrap",
            f"{self.player.id} bids {self.to_gamble} scrap",
            list_pretty_name_objects = list_pretty_name_objects
        )
        self.is_gambling = True
        self.npc.earnings += self.to_gamble
        self.save_earnings()
        return True

    def tick(self):
        # if self.npc not in self.player.room.actors.values():
        #    self.end_gambling()
        #    super().end_dialog()
        #    return

        pause_time = TICKRATE
        if self.is_gambling == False:
            self.ticks = 0
            return

        self.ticks += 1

        if self.ticks == 0:
            list_pretty_name_objects = [self.player, self.npc]
            self.npc.pretty_broadcast(
                None,
                f"{self.npc.id} takes {self.to_gamble} scrap",
                list_pretty_name_objects = list_pretty_name_objects
            )
            return

        if self.ticks in [pause_time, pause_time * 2, pause_time * 3]:
            roll = random.randint(1, 6)
            self.rolls.append(roll)
            if len(self.rolls) >= 3:
                return

            list_pretty_name_objects = [self.player, self.npc]
            self.player.pretty_broadcast(
                f"{self.npc.id} rolls a {roll}!",
                f"{self.npc.id} rolls a {roll}",
                list_pretty_name_objects = list_pretty_name_objects
            )
            return

        if self.ticks >= pause_time * 3:
            list_pretty_name_objects = [self.player, self.npc]
            self.player.pretty_broadcast(
                f'{self.npc.id} says "a {self.rolls[0]}, {self.rolls[1]} and a {self.rolls[2]}"!',
                f'{self.npc.id} says "a {self.rolls[0]}, {self.rolls[1]} and a {self.rolls[2]}"',
                list_pretty_name_objects = list_pretty_name_objects
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

            list_pretty_name_objects = [self.npc]
            self.player.pretty_broadcast(
                f"{self.npc.id} {output}",
                f"{self.npc.id} {output}",
                list_pretty_name_objects = list_pretty_name_objects
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

        self.original_description = self.description

        filename = EARNINGS_DATA_LOCATION
        if not os.path.exists(filename):
            # create file with default content
            with open(filename, "w") as f:
                json.dump({"from_file": str(__file__), "earnings": 0}, f)

        # now read the file
        with open(filename, "r") as f:
            earnings_data = json.load(f)

        self.earnings = earnings_data['earnings']

        self.trigger_manager.trigger_add(trigger_key = 'gamble', trigger_action = self.trigger_gamble)
        self.description += '\nYou can "gamble <amount>" to skip the chitchat.'

    def trigger_gamble(self, player, line):
        if len(line.split())!=2:
            list_pretty_name_objects = [self]
            player.send_line(f'{self.id} says "If you want to gamble, either talk to me, or "gamble <amount>""',
            list_pretty_name_objects = list_pretty_name_objects)
            return True
        self.talk_to(player)
        player.current_dialog.answer('1')
        player.current_dialog.answer(line.split()[1])
        return True

    def tick(self):
        
        super().tick()
        for i in self.dialogs.values():
            i.tick()

        self.time_exisiting += 1
        if self.time_exisiting % (TICKRATE * 3) == 0:
            self.description = f'{self.original_description} They have {"made" if self.earnings >= 0 else "lost"} {abs(self.earnings)} scrap so far.'
            if self.actors != len(self.room.actors.values()):
                self.actors = len(self.room.actors.values())
                
                actor = random.choice(list(self.room.actors.values()))

                if actor.__class__.__name__ != 'Player':
                    self.actors = 0
                    return

                if actor.current_dialog != None:
                    return
                
                if actor.inventory_manager.items == {}:
                    return

                item = random.choice(list(actor.inventory_manager.items.values()))

                item_name = item.name
                list_pretty_name_objects = [actor, self]
                actor.pretty_broadcast(
                    f'"Wanna bet that {item_name}, {actor.pretty_name(identifier = actor, text_override = actor.name)}?" {self.id} asks', f'"Wanna bet that {item_name}, {actor.id}?" {self.id} asks',
                    list_pretty_name_objects = list_pretty_name_objects
                )
