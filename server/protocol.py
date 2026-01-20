import copy
import random
import secrets
import uuid
import brevo
import utils
from actors.player import Player
from actors.player_only_functions.settings import SETTINGS
from configuration.config import (
    SKILLS,
    SPLASH_SCREENS,
    ActorStatusType,
    Color,
    ItemType,
    StaticRooms,
    StatType,
)
from items.equipment import EquipmentBonus
from items.manager import load_item, save_item
from quest import OBJECTIVE_TYPES
from twisted.internet import protocol
import ast

IAC = b"\xff"  # Interpret as Command
WILL = b"\xfb"  # Will Perform
SE = b"\xf0"
SB = b"\xfa"
WONT = b"\xfc"  # Will Not Perform
DO = b"\xfd"  # Please Do
DONT = b"\xfe"  # Please Don’t
ECHO = b"\x01"  # Echo
LINEMODE = b"\x22"  # Line mode
GMCP = b"\xc9"
MSSP = b"\x46"

with open('configuration/words.txt', "r", encoding="utf-8") as f:
    secret_words = [line.strip() for line in f if line.strip()]

def generate_tmp_pwd(num_words=4):
    return "-".join(secrets.choice(secret_words) for _ in range(num_words))

class Protocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.state: callable = self.LOGIN_OR_REGISTER

        self.enabled_gmcp = False

        self.guest = False

        self.actor = None

        self.account = None
        self.username = None
        self.password = None


        # for password reset
        self.tmp_pwd = None

        self.tick_since_last_message = self.factory.ticks_passed

        self.id = str(uuid.uuid4())

    def clear_screen(self):
        self.sendLine("\x1b[0m")
        self.sendLine("\u001b[2J")

    def start_mssp(self):
        self.transport.write(IAC + WILL + MSSP)

    def send_mssp(self):
        data = IAC + SB + MSSP
        data += b"\x01NAME\x02Jorm"
        data += b"\x01PLAYERS\x02" + str(len(self.factory.protocols)).encode("utf-8")
        data += b"\x01UPTIME\x02" + str(int(self.factory.start)).encode("utf-8")
        data += IAC + SE
        self.transport.write(data)

    def start_gmcp(self):
        self.transport.write(IAC + WILL + GMCP)

    def send_gmcp(self, gmcp_data, gmcp_data_type):
        if not self.enabled_gmcp:
            return

        gmcp_data = str(gmcp_data)
        # gmcp_data_type = 'Core.Hello'
        # gmcp_data = '{"da": "me", "daa": "nee"}'
        if self.actor != None:
            if self.actor.settings_manager.get_value(SETTINGS.DEBUG):
                packet = (
                    ""
                    + "IAC "
                    + "SB "
                    + "GMCP "
                    + gmcp_data_type
                    + " "
                    + gmcp_data
                    + " IAC"
                    + " SE"
                    + ""
                )
                packet = packet.encode("utf-8")
                self.transport.write(packet)
                # return
        # utils.debug_print(packet)
        packet = (
            IAC
            + SB
            + GMCP
            + gmcp_data_type.encode("utf-8")
            + " ".encode("utf-8")
            + gmcp_data.encode("utf-8")
            + IAC
            + SE
        )

        self.transport.write(packet)

    def splash_screen(self):
        splash = random.choice(SPLASH_SCREENS["screens"])
        splash = (
            f"Art source: {Color.IMPORTANT}https://www.asciiart.eu/plants/mushroom\n{Color.BACK}"
            + splash
        )
        splash = splash.replace(
            f"#DISCORD#", f"{Color.IMPORTANT}https://discord.gg/AZ98axtXc6{Color.BACK}"
        )
        splash = splash.replace(
            f"#ONLINE#", f"{Color.IMPORTANT}{len(self.factory.protocols)}{Color.BACK}"
        )
        splash = f"{Color.NORMAL}{splash}{Color.NORMAL}"
        self.sendLine(splash)

    def change_state(self, state):
        match state:
            case self.LOGIN_OR_REGISTER:
                self.id = str(uuid.uuid4())
                self.account = None
                self.username = None
                self.password = None
                self.sendLine(
                    f"Type {Color.GOOD} new   {Color.BACK} to register.\nType {Color.GOOD} login {Color.BACK} to log in.\nType {Color.GOOD} reset {Color.BACK} to reset your password.\nType {Color.GOOD} guest {Color.NORMAL} to enter as guest."
                )

            case self.LOGIN_USERNAME:
                self.sendLine(f"Your {Color.GOOD}username{Color.BACK}:")

            case self.RESET_USERNAME:
                self.sendLine(f"Your {Color.GOOD}username{Color.BACK}:")

            case self.LOGIN_PASSWORD:
                self.sendLine(f"Your {Color.GOOD}password{Color.BACK}:")

            case self.REGISTER_USERNAME:
                self.sendLine(
                    "Please use a unique username, not linking your Jorm account to anything private."
                )
                self.sendLine(
                    "Please use a unique password, only for Jorm. Never share it."
                )
                self.sendLine(
                    f"Creating new account. enter your {Color.GOOD}username{Color.BACK}:"
                )

            case self.REGISTER_PASSWORD1:
                self.sendLine(f"Enter your {Color.GOOD}password{Color.BACK}:")

            case self.REGISTER_PASSWORD2:
                self.sendLine(f"Enter {Color.GOOD}password{Color.BACK} again:")

            case self.PLAY:
                self.account = self.factory.db.find_account_from_username(self.username)
                self.id = self.account[0]
                self.username = self.account[1]
                self.password = self.account[2]
                for online_account in self.factory.protocols:
                    if self.id == online_account.id and self != online_account:
                        online_account.disconnect()
                self.load_actor()

            case self.PLAY_AS_GUEST:
                self.guest = True
                self.id = self.account[0]
                self.username = self.account[1]
                self.password = self.account[2]
                state = self.PLAY
                self.load_actor()

        self.state = state

    def PLAY(self, line):
        if line:
            self.actor.last_line_sent = line
        self.actor.queue_handle(line)
        return

    def PLAY_AS_GUEST(self, line):
        return

    def REGISTER_USERNAME(self, line):
        self.account = self.factory.db.find_account_from_username(line)
        if self.account != None:
            self.sendLine("This username is already taken")
            self.change_state(self.REGISTER_USERNAME)
            return

        if len(line) >= 21 or len(line) <= 3:
            self.sendLine("Username must be between 4 and 20 characters long")
            self.change_state(self.REGISTER_USERNAME)
            return

        if not line.isalnum():
            self.sendLine("Username can only contain letters and numbers")
            self.change_state(self.REGISTER_USERNAME)
            return

        self.username = line
        self.change_state(self.REGISTER_PASSWORD1)

    def REGISTER_PASSWORD1(self, line):
        if len(line) < 6:
            self.sendLine("Your password must be a minimum of 6 character")
            self.change_state(self.REGISTER_PASSWORD1)
            return

        self.password = line
        self.change_state(self.REGISTER_PASSWORD2)

    def REGISTER_PASSWORD2(self, line):
        if line != self.password:
            self.sendLine("Passwords do not match")
            self.change_state(self.LOGIN_OR_REGISTER)
            return

        self.factory.db.create_new_account(self.id, self.username, self.password)
        # self.sendLine('Account created! you can now log in!')
        # self.change_state(self.LOGIN_OR_REGISTER)

        self.sendLine("Account created! logging in!")
        self.change_state(self.PLAY)

    def LOGIN_PASSWORD(self, line):
        self.password = line
        if self.account == None:
            self.sendLine("Wrong username or password")
            self.change_state(self.LOGIN_OR_REGISTER)
            self.tmp_pwd = None
            return

        if self.account[2] != line and self.tmp_pwd != line:
            self.sendLine("Wrong username or password")
            self.change_state(self.LOGIN_OR_REGISTER)
            self.tmp_pwd = None
            return

        self.tmp_pwd = None
        self.change_state(self.PLAY)

    def LOGIN_USERNAME(self, line):
        self.account = self.factory.db.find_account_from_username(line)
        self.username = line
        self.change_state(self.LOGIN_PASSWORD)
        return

    def RESET_USERNAME(self, line):
        self.account = self.factory.db.find_account_from_username(line)
        self.username = line

        if self.account == None:
            self.sendLine('This account does not exist')
            self.change_state(self.LOGIN_OR_REGISTER)
            return

        actor = self.factory.db.read_actor(self.account[0])
        if actor == None:
            self.sendLine('This account does not exist')
            self.change_state(self.LOGIN_OR_REGISTER)
            return

        if 'email' not in actor['settings']:
            self.sendLine('This account does not have an email')
            self.change_state(self.LOGIN_OR_REGISTER)
            return

        email = actor['settings']['email']
        if email == '':
            self.sendLine('This account does not have an email')
            self.change_state(self.LOGIN_OR_REGISTER)
            return

        self.sendLine(f'''
{Color.IMPORTANT}You will soon receive a ONE TIME password on your email.
Please check your spam folder.
You will need to change your password after you log in
"setting password <new password>"
This ONE TIME password will not work next time you try to log in.{Color.NORMAL}
            '''.strip())
        self.tmp_pwd = generate_tmp_pwd()

        brevo.send_reset_email(to = email, pwd = self.tmp_pwd)
        print(email, self.tmp_pwd)

        self.change_state(self.LOGIN_PASSWORD)
        return

    def LOGIN_OR_REGISTER(self, line):
        if line.lower() == "login".lower():
            self.change_state(self.LOGIN_USERNAME)
            return
        if line.lower() == "reset".lower():
            self.change_state(self.RESET_USERNAME)
            return
        if line.lower() == "new".lower():
            self.change_state(self.REGISTER_USERNAME)
            return
        if line.lower() == "guest".lower():
            _id = str(uuid.uuid4())
            titles = ["Goon", "Gamer", "Gold Farmer", "Noob", "Pro", "Mudder", "Smelly"]
            _usr = utils.generate_name() + " The " + random.choice(titles)
            _pwd = str(uuid.uuid4())
            self.account = [_id, _usr, _pwd]

            self.change_state(self.PLAY_AS_GUEST)

            return
        self.change_state(self.LOGIN_OR_REGISTER)
        return

    def register_account_changes(self, username, password):
        if len(password) < 6:
            self.sendLine("Your password must be a minimum of 6 character")
            return False

        if password.startswith(" ") or password.endswith(" "):
            self.sendLine("Your password cannot start or end with a whitespace")
            return

        if "  " in password:
            self.sendLine(
                'Yes this is a stupid rule but: Your password cannot include multiple whitespaces in a row... "  " not good'
            )
            return False

        account = self.factory.db.find_account_from_username(username)
        # utils.debug_print(self.account)
        if account != None and account[0] != self.id:
            self.sendLine("This username is already taken")
            return False

        self.account = account

        if len(username) >= 21 or len(username) <= 3:
            self.sendLine("Username must be between 4 and 20 characters long")
            return False

        if not username.isalnum():
            self.sendLine("Username can only contain letters and numbers")
            return False

        self.username = username
        self.password = password
        if self.actor != None:
            self.actor.name = self.username
        self.factory.db.create_new_account(self.id, username, password)
        _alert = f"{Color.BAD}[{Color.IMPORTANT}!{Color.BAD}]{Color.BACK}"
        self.sendLine(
            f'{Color.GOOD}Account information updated\n{_alert}   Your login username is: "{Color.IMPORTANT}{self.username}{Color.BACK}"   {_alert}{Color.NORMAL}'
        )
        # Your password is: "{Color.IMPORTANT}{'*'*len(self.password)}{Color.BACK}"
        return True

    # override
    def connectionMade(self):
        # utils.logging.debug(self.id + 'Connection made')
        self.tick_since_last_message = self.factory.ticks_passed
        self.start_mssp()
        self.start_gmcp()

        self.factory.protocols.add(self)
        self.splash_screen()
        self.change_state(self.LOGIN_OR_REGISTER)

    def compare_slots_to_items(self):
        for i in self.actor.slots_manager.slots.values():
            if i not in self.actor.inventory_manager.items:
                if i == None:
                    continue
                utils.debug_print(
                    f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!{i} is not in inventory?"
                )

    def load_actor(self):
        actor = self.factory.db.read_actor(self.account[0])
        # utils.debug_print('>>>',actor)

        if actor == None:  # new actor
            self.actor = Player(
                self,
                _id=None,
                name=self.username,
                room=self.factory.world.rooms[StaticRooms.LOADING],
            )
        else:  # load an existing actor
            self.actor = Player(
                self,
                _id=actor["actor_id"],
                name=actor["actor_name"],
                room=self.factory.world.rooms[StaticRooms.LOADING],
            )
            self.actor.recall_site = actor["actor_recall_site"]
            self.actor.date_of_creation = actor["meta_data"]["date_of_creation"]
            self.actor.time_in_game = actor["meta_data"]["time_in_game"]
            self.actor.date_of_last_login_previous = actor["meta_data"][
                "date_of_last_login"
            ]

            # add quests
            for quest in actor["quests"]:
                if self.actor.quest_manager.start_quest(quest, silent=True):
                    for objective in actor["quests"][quest]:
                        if (
                            objective
                            not in self.actor.quest_manager.quests[quest].objectives
                        ):
                            continue
                        if (
                            self.actor.quest_manager.quests[quest]
                            .objectives[objective]
                            .type
                            == OBJECTIVE_TYPES.COLLECT_X
                        ):
                            continue

                        # if it is a daily quest, load in everything from db, otherwise, load it from config
                        self.actor.quest_manager.quests[quest].objectives[
                            objective
                        ].count = actor["quests"][quest][objective]["count"]
                        if quest == "daily_quest":
                            self.actor.quest_manager.quests[quest].objectives[
                                objective
                            ].requirement_id = actor["quests"][quest][objective][
                                "req_id"
                            ]
                            self.actor.quest_manager.quests[quest].objectives[
                                objective
                            ].goal = actor["quests"][quest][objective]["goal"]
                            self.actor.quest_manager.quests[quest].objectives[
                                objective
                            ].type = actor["quests"][quest][objective]["type"]

            # self.actor.date_of_last_login = actor['meta_data']['date_of_last_login']

            self.actor.stat_manager.stats.update(actor["stats"])
            self.actor.skill_manager.skills = actor["skills"]
            # remove removed skills
            tmp = copy.deepcopy(self.actor.skill_manager.skills)
            for skill in tmp:
                if skill not in SKILLS:
                    del self.actor.skill_manager.skills[skill]

            for _setting in actor["settings"]:
                self.actor.settings_manager.settings[_setting] = actor["settings"][
                    _setting
                ]

            if SETTINGS.ALIAS in self.actor.settings_manager.settings:
                self.actor.settings_manager.settings[SETTINGS.ALIAS] = ast.literal_eval(actor['settings'][SETTINGS.ALIAS])

            # utils.debug_print(actor['settings'])
            '''if actor["settings"] != {}:
                self.actor.settings_manager.gmcp = actor["settings"]["gmcp"]
                self.actor.settings_manager.view_room = actor["settings"]["view_room"]
                self.actor.settings_manager.view_map = actor["settings"]["view_map"]
                self.actor.settings_manager.view_ascii_art = actor["settings"]["view_ascii_art"]
                self.actor.settings_manager.prompt = actor["settings"]["prompt"]
                self.actor.settings_manager.email = actor["settings"]["email"]'''

            bonuses = actor["equipment_bonuses"]

            for item in actor["inventory"].values():
                new_item = load_item(
                    item_premade_id=item["premade_id"], unique_id=item["item_id"]
                )
                new_item.keep = item["item_keep"]
                new_item.id = item["item_id"]
                new_item.stack = item["item_stack"]

                """
                item_id TEXT NOT NULL,
                type TEXT NOT NULL,
                key TEXT NOT NULL,
                val INT NOT NULL,
                """

                if item["item_id"] in bonuses:
                    for bonus in bonuses[item["item_id"]]:
                        # utils.debug_print(bonus)
                        boon = EquipmentBonus(
                            type=bonus["type"], key=bonus["key"], val=bonus["val"]
                        )
                        new_item.manager.add_bonus(boon)

                self.actor.inventory_manager.add_item(new_item, forced=True)
            self.compare_slots_to_items()

            # actor is loaded without equipment stats on
            # add them back here
            for item_id in actor["equipment"]:
                # skip if item is somehow not in inventory
                if item_id not in self.actor.inventory_manager.items:
                    utils.debug_print(item_id, "is equiped but not in inventory?")
                    continue
                if (
                    self.actor.inventory_manager.items[item_id].item_type
                    != ItemType.EQUIPMENT
                ):
                    utils.debug_print(item_id, "is equiped but not ItemType.EQUIPMENT")
                    continue
                item = self.actor.inventory_manager.items[item_id]
                self.actor.inventory_equip(item, forced=True)

            # utils.debug_print(actor['friends'])
            if actor["friends"] != []:
                for i in actor["friends"]:
                    # skip if somehow you friended yourself
                    if i[1] == self.actor.id:
                        continue
                    # skip if actor id does not return anything
                    if (
                        self.actor.friend_manager.find_actor_name_from_actor_id(i[1])
                        == None
                    ):
                        continue
                    self.actor.friend_manager.friends.append(i[1])

            # utils.debug_print(actor['explored_rooms'])
            if actor["explored_rooms"] != []:
                for i in actor["explored_rooms"]:
                    self.actor.explored_rooms.append(i[1])

        self.actor.inventory_manager.all_items_set_new(False)

        self.state = self.PLAY

        if actor == None:
            self.save_actor()
            self.actor.recall_site = StaticRooms.TUTORIAL
        else:
            if self.actor.recall_site not in self.actor.room.world.rooms:
                self.save_actor()
                self.actor.recall_site = StaticRooms.TUTORIAL

        self.actor.room.world.rooms[self.actor.recall_site].move_actor(self.actor)

        # disable / enable ascii map depending on gmcp settings
        self.actor.settings_manager.view_map = not self.enabled_gmcp
        #self.actor.settings_manager.view_room = not self.enabled_gmcp
        self.sendLine(
            "You are now in JORM! ascii map has been turned "
            + ("on" if self.actor.settings_manager.view_map else "off")
            + " due to current gmcp settings (help settings)"
        )

        self.actor.get_any_new_patches()
        self.actor.new_room_look()
        self.actor.friend_manager.friend_broadcast_login()
        self.actor.finish_turn()

    def save_actor(self):
        if self.guest:
            utils.debug_print("Not saving guest lol xd")
            return

        if self.actor == None:
            utils.debug_print("no actor")
            return

        self.factory.db.write_actor(self.actor)
        a = self.factory.db.read_actor(self.id)

    def disconnect(self):
        self.transport.abortConnection()

    def unload_actor(self):
        self.actor.affect_manager.unload_all_affects(silent=False)
        self.save_actor()
        self.actor.simple_broadcast(
            "Logging off", f"{self.actor.pretty_name()} logging off"
        )
        self.actor.friend_manager.friend_broadcast_logout()
        # teleport player to loading to remove them safely
        self.factory.world.rooms[StaticRooms.LOADING].move_actor(self.actor)
        # del self.factory.world.rooms[StaticRooms.LOADING].actors[self.actor.id]
        # remove player from combat
        # del self.actor.room.actors[self.actor.id]
        # self.actor.room = None

        self.actor.unload()
        self.actor.protocol = None
        self.actor = None
        # self.actor = None

    # override
    def connectionLost(self, reason):
        # utils.logging.debug(self.id + f' Connection lost: {reason}')
        if self.actor != None:
            self.unload_actor()

        self.factory.protocols.remove(self)

    # override
    def dataReceived(self, data):
        self.tick_since_last_message = self.factory.ticks_passed

        # interrupt
        if data == b"\xff\xf4\xff\xfd\x06":
            self.disconnect()
            return

        if IAC in data:
            # IAC   SB GMCP 'MSDP {"COMMANDS" : ["LIST", "REPORT", "RESET", "SEND", "UNREPORT"]}' IAC SE
            # self.transport.write(IAC + SB + GMCP + '{"COMMANDS" : ["LIST", "REPORT", "RESET", "SEND", "UNREPORT"]}'.encode('utf-8') + IAC + SE)
            if data == IAC + DO + MSSP:
                self.send_mssp()
            if data == IAC + DO + GMCP:
                self.enabled_gmcp = True
            if data == IAC + DONT + GMCP:
                self.enabled_gmcp = False
            return

        # decode and process input data
        line = data.decode("utf-8", errors="ignore").strip()

        # log account unique ID and what message was sent
        # if self.state == self.PLAY:
        # utils.logging.debug(self.account[0] + ' -> ' + line)

        # if line:  # skip empty lines
        #if "@" in line:
        #    line = str(line) + Color.NORMAL
        self.state(line)
        return

    def sendLine(self, line):
        line = utils.add_color(line)
        self.transport.write(f"{line}\n".encode("utf-8"))
