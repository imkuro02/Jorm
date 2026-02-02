# from actors.enemy import create_enemy
import copy
import os
import random
import time

# from items import Item
import uuid

import systems.utils
from actors.npcs import create_npc
from actors.player import Player
from combat.manager import Combat
from configuration.config import (
    ENEMIES,
    ITEMS,
    NPCS,
    WORLD,
    ActorStatusType,
    Audio,
    MsgType,
    StatType,
)
from custom import loader as custom_loader
from items.manager import load_item
from systems.inventory import InventoryManager
from systems.room import Exit, Room
from systems.utils import REFTRACKER, unload


class GameTime:
    def __init__(self, factory, game_date_time=0):
        self.factory = factory
        self.TICKS_PER_SECOND = 30
        self.SECONDS_PER_TICK = 2  # game seconds per tick
        self.SECONDS_PER_MINUTE = 60
        self.MINUTES_PER_HOUR = 60
        self.HOURS_PER_DAY = 24
        self.DAYS_PER_WEEK = 7
        self.WEEKS_PER_MONTH = 4
        self.MONTHS_PER_YEAR = 12
        self.DAYS_PER_MONTH = self.DAYS_PER_WEEK * self.WEEKS_PER_MONTH  # 28
        self.DAYS_PER_YEAR = self.DAYS_PER_MONTH * self.MONTHS_PER_YEAR  # 336

        self.game_date_time = game_date_time

        self.WEEKDAYS = [
            "Moonsday",
            "Twosday",
            "Wakesday",
            "Thornsday",
            "Firesday",
            "Starsday",
            "Endsday",
        ]
        self.MONTHS = [
            "Suncall",
            "Moondrift",
            "Stormreach",
            "Frostwane",
            "Blossomveil",
            "Flamehollow",
            "Duskwind",
            "Brightshade",
            "Hollowfall",
            "Dawnspire",
            "Gloomtide",
            "Starcrest",
        ]

        self.TIME_OF_DAY = {
            "morning": False,
            "noon": False,
            "evening": False,
            "night": False,
            "not_morning": False,
            "not_noon": False,
            "not_evening": False,
            "not_night": False,
            "hour_even": False,
            "hour_uneven": False,
        }

        self.load_game_time()

    def load_game_time(self):
        filename = "database/gametime.txt"
        if not os.path.exists(filename):
            # File doesn't exist — create it and write 420
            with open(filename, "w") as f:
                f.write(f"{self.game_date_time}")
            value = self.game_date_time
        else:
            # File exists — read the integer inside
            with open(filename, "r") as f:
                self.game_date_time = int(f.read().strip())

        systems.utils.debug_print("Game Time:", self.game_date_time)

    def save_game_time(self):
        filename = "database/gametime.txt"
        with open(filename, "w") as f:
            f.write(f"{self.game_date_time}")

    def time_of_day_trigger(self):
        time_dict = self.get_game_time()

        self.TIME_OF_DAY["morning"] = time_dict["hour"] >= 5 and time_dict["hour"] <= 10
        self.TIME_OF_DAY["noon"] = time_dict["hour"] >= 10 and time_dict["hour"] <= 16
        self.TIME_OF_DAY["evening"] = (
            time_dict["hour"] >= 17 and time_dict["hour"] <= 20
        )
        self.TIME_OF_DAY["night"] = time_dict["hour"] >= 21 or time_dict["hour"] <= 4
        self.TIME_OF_DAY["not_morning"] = not self.TIME_OF_DAY["morning"]
        self.TIME_OF_DAY["not_noon"] = not self.TIME_OF_DAY["noon"]
        self.TIME_OF_DAY["not_evening"] = not self.TIME_OF_DAY["evening"]
        self.TIME_OF_DAY["not_night"] = not self.TIME_OF_DAY["night"]
        self.TIME_OF_DAY["hour_even"] = time_dict["hour"] % 2 == 0
        self.TIME_OF_DAY["hour_uneven"] = time_dict["hour"] % 2 != 0

    def tick(self):
        self.game_date_time += 1
        self.time_of_day_trigger()

    def set_game_time(self, line):
        try:
            time = int(line)
            self.game_date_time = time
        except Exception as e:
            self.sendLine(f"Cant set time: {e}")

    def get_game_time_compact_str(self):
        _time = self.get_game_time()
        time = f"{_time['second']:02}.{_time['minute']:02}.{_time['hour']:02}.{_time['day']:02}.{_time['month']:02}.{_time['year']:04}"
        return time

    def get_game_time_int(self):
        return self.game_date_time

    def get_game_time(self):
        total_game_seconds = self.game_date_time * self.SECONDS_PER_TICK

        total_minutes = total_game_seconds // 60
        seconds = total_game_seconds % 60

        total_hours = total_minutes // 60
        minutes = total_minutes % 60

        total_days = total_hours // 24
        hours = total_hours % 24

        year = total_days // self.DAYS_PER_YEAR + 1
        day_of_year = total_days % self.DAYS_PER_YEAR

        month_index = day_of_year // self.DAYS_PER_MONTH
        day_of_month = day_of_year % self.DAYS_PER_MONTH + 1

        weekday_index = total_days % self.DAYS_PER_WEEK

        return {
            "day_name": self.WEEKDAYS[weekday_index],
            "month_name": self.MONTHS[month_index],
            "year": year,
            "day": day_of_month,
            "month": month_index,
            "hour": int(hours),
            "minute": int(minutes),
            "second": int(seconds),
        }


class World:
    def __init__(self, factory):
        self.factory = factory
        self.rooms = {}
        self.rooms_to_unload = []
        self.game_time = GameTime(self.factory)
        self.reload()

    def spawn_boss(self):
        all_mobs = []
        for i in self.rooms:
            if self.rooms[i].instanced:
                continue
            for x in self.rooms[i].actors:
                if type(self.rooms[i].actors[x]).__name__ != "Enemy":
                    continue
                if self.rooms[i].actors[x].status != ActorStatusType.NORMAL:
                    continue
                all_mobs.append(self.rooms[i].actors[x])

        boss_mob = random.choice(all_mobs)
        boss_mob.name = "<!>" + boss_mob.name + "<!>"
        boss_mob.simple_broadcast(
            "",
            f"{boss_mob.pretty_name()} is terrorizing {boss_mob.room.name}",
            send_to="world",
        )
        for s in boss_mob.stat_manager.stats:
            boss_mob.stat_manager.stats[s] = boss_mob.stat_manager.stats[s] * 2
        boss_mob.stat_manager.stats[StatType.EXP] = (
            boss_mob.stat_manager.stats[StatType.EXP] * 5
        )

    def reload(self):
        start = time.time()
        # systems.utils.debug_print(f"Reloading rooms: {time.time()} START")

        to_del = []
        for r in self.rooms:
            players = [
                actor
                for actor in self.rooms[r].actors.values()
                if type(actor).__name__ == "Player"
            ]
            if len(players) >= 1:
                continue
            systems.utils.debug_print("del room: ", self.rooms[r].id)
            to_del.append(r)

        for d in to_del:
            del self.rooms[d]

        world = WORLD

        target_id = "overworld/loading"

        # Only reorder if it exists
        if target_id in world["world"]:
            # Remove the target room from the dict
            target_room = world["world"].pop(target_id)

            # Reinsert it at the beginning
            world["world"] = {target_id: target_room, **world["world"]}

        for r in world["world"]:
            room = world["world"][r]

            if r in self.rooms:
                players = [
                    actor
                    for actor in self.rooms[r].actors.values()
                    if type(actor).__name__ == "Player"
                ]
                if len(players) >= 1:
                    continue

                # prepare to reload
                for e in self.rooms[r].actors.values():
                    e.room = None
                del self.rooms[r]

            # create the room
            self.rooms[r] = Room(
                self,
                r,
                room["name"],
                room["description"],
                room["from_file"],
                room["exits"],
                room["can_be_recall_site"],
                room["doorway"],
                room["instanced"],
            )

            # check if you actually want some other class
            room_class = custom_loader.compare_replace_rooms(self.rooms[r])
            self.rooms_to_unload.append(r)
            self.unload_rooms()

            # recreate the room regardless
            self.rooms[r] = room_class(
                self,
                r,
                room["name"],
                room["description"],
                room["from_file"],
                room["exits"],
                room["can_be_recall_site"],
                room["doorway"],
                room["instanced"],
            )

        systems.utils.debug_print(f"Reloading rooms: {time.time() - start} DONE")

    def save_world(self):
        pass

    def unload_rooms(self):
        for i in self.rooms_to_unload:
            to_kick_from_instance = []
            for x in self.rooms[i].actors.values():
                to_kick_from_instance.append(x)
            for x in to_kick_from_instance:
                if type(x).__name__ == "Player":
                    x.party_manager.party_leave()

            for x in self.rooms[i].inventory_manager.items.values():
                unload(x)
            unload(self.rooms[i].inventory_manager.triggerable_manager)

            to_unload = []
            for x in self.rooms[i].actors.values():
                to_unload.append(x)
            for x in to_unload:
                # x.die()
                x.unload()

            # self.rooms[i].actors = {}

            to_unload = []
            for x in self.rooms[i].exits:
                to_unload.append(x)
            for x in to_unload:
                unload(x)

            to_unload = []
            for x in self.rooms[i].__dict__:
                to_unload.append(x)
            for x in to_unload:
                unload(x)

            # systems.utils.debug_print(self.rooms[i])
            unload(self.rooms[i])
            # systems.utils.debug_print(self.rooms[i])
            del self.rooms[i]

        self.rooms_to_unload = []

        rooms = []
        for i in self.rooms:
            rooms.append(self.rooms[i])
        for i in rooms:
            ##if i.name.lower() == 'South-west corner'.lower():
            #    systems.utils.debug_print(i.id)
            #    for x in i.actors.values():
            #        systems.utils.debug_print('>', x.name)
            i.tick()

        systems.utils.unload_fr()

    def tick(self):
        self.game_time.tick()
        self.unload_rooms()


from actors import ai

ai.Room = Room
ai.Exit = Exit
