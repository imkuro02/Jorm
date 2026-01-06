import json
import sqlite3

import utils
from configuration.config import ItemType


class Database:
    def __init__(self):
        # Connect to the database
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()

        # Create the users table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            unique_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )""")

        # Create admins table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                actor_id TEXT,
                admin_level INT
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS actors (
            unique_id TEXT UNIQUE NOT NULL,
            actor_id TEXT PRIMARY KEY NOT NULL,
            actor_name TEXT NOT NULL,
            actor_recall_site TEXT NOT NULL,
            actor_date_of_creation INT NOT NULL,
            actor_date_of_last_login INT NOT NULL,
            actor_time_in_game INT NOT NULL,
            FOREIGN KEY(unique_id) REFERENCES users(unique_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            actor_id TEXT PRIMARY KEY,
            hp_max INT NOT NULL,
            hp INT NOT NULL,
            grit INT NOT NULL,
            flow INT NOT NULL,
            mind INT NOT NULL,
            soul INT NOT NULL,
            phy_armor INT NOT NULL,
            mag_armor INT NOT NULL,
            phy_armor_max INT NOT NULL,
            mag_armor_max INT NOT NULL,
            exp INT NOT NULL,
            lvl INT NOT NULL,
            pp INT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            actor_id TEXT NOT NULL,
            premade_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            item_keep BOOL NOT NULL,
            item_stack INT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            actor_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            FOREIGN KEY(item_id) REFERENCES inventory(item_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment_bonuses (
            actor_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            id TEXT NOT NULL,
            type TEXT NOT NULL,
            key TEXT NOT NULL,
            val INT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            actor_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            skill_lvl INT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES inventory(actor_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            actor_id TEXT NOT NULL,
            quest_id TEXT NOT NULL,
            objective_name TEXT NOT NULL,
            objective_type TEXT,
            objective_requirement_id TEXT,
            objective_count INT,
            objective_goal INT,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings_aliases (
            actor_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            actor_id TEXT PRIMARY KEY,
            gmcp BOOL NOT NULL,
            view_room BOOL NOT NULL,
            view_map BOOL NOT NULL,
            view_ascii_art BOOL NOT NULL,
            prompt TEXT NOT NULL,
            email TEXT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend (
            actor_id TEXT NOT NULL,
            friend_id TEXT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS explored_rooms (
            actor_id TEXT NOT NULL,
            room_id TEXT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )""")

        # Commit changes
        self.conn.commit()

    def find_account_from_username(self, username):
        self.cursor.execute(
            """
                SELECT unique_id, username, password
                FROM accounts WHERE username = ?
            """,
            (username,),
        )

        account = self.cursor.fetchone()

        return account

    def find_actor_name_from_actor_id(self, _id):
        self.cursor.execute(
            """
                SELECT actor_id, actor_name
                FROM actors WHERE actor_id = ?
            """,
            (_id,),
        )

        to_return = self.cursor.fetchone()
        return to_return

    def find_actor_id_from_actor_name(self, _username):
        self.cursor.execute(
            """
                SELECT actor_id, actor_name
                FROM actors WHERE actor_name = ?
            """,
            (_username,),
        )

        to_return = self.cursor.fetchone()
        return to_return

    def find_all_accounts(self):
        self.cursor.execute(
            """
                SELECT unique_id, username, password
                FROM accounts
            """
        )

        accounts = self.cursor.fetchall()

        actor_objs = []
        # Iterate through each account and create the actor object
        for acc in accounts:
            # Fetch account details
            actor = self.read_actor(
                acc[0]
            )  # Assuming acc[0] is the account ID or relevant identifier
            # 'quests': {'tutorial_1': {'Get a corpse': 0, 'turned_in': 1}
            if actor == None:
                continue

            # Create actor_obj and append to the list
            actor_obj = {
                "name": acc[1],  # Assuming acc[1] is the account's name
                "exp": actor["stats"][
                    "exp"
                ],  # Extract experience points from actor stats
                "lvl": actor["stats"]["lvl"],  # Extract level from actor stats
                "date_of_creation": actor["meta_data"]["date_of_creation"],
                "date_of_last_login": actor["meta_data"]["date_of_last_login"],
                "time_in_game": actor["meta_data"]["time_in_game"],
                #'quests_turned_in': len([q for q in actor['quests'] if actor['quests'][q]['turned_in'] == 1])
                "quests_turned_in": len(
                    [
                        q
                        for q in actor["quests"]
                        if actor["quests"][q]["turned_in"]["count"] == 1
                        and q != "daily_quest"
                    ]
                ),
                "explored_rooms": len([q for q in actor["explored_rooms"]]),
            }
            # utils.debug_print(actor['quests'], actor['quests'].values())
            actor_objs.append(actor_obj)

        # Sort actor_objs list from most experience to least experience
        sorted_actor_objs = sorted(actor_objs, key=lambda x: x["exp"], reverse=True)

        # utils.debug_print the sorted list of actor objects
        # for actor in sorted_actor_objs:
        #    utils.debug_print(actor)
        return sorted_actor_objs

    def create_new_account(self, unique_id, username, password):
        self.cursor.execute(
            """
            INSERT INTO accounts (unique_id, username, password)
            VALUES (?, ?, ?)
            ON CONFLICT(unique_id) DO UPDATE SET
                username = excluded.username,
                password = excluded.password
        """,
            (unique_id, username, password),
        )
        self.conn.commit()

    def write_actor(self, actor):
        actor_id = actor.id

        my_dict = {}
        my_dict["unique_id"] = actor.protocol.id
        my_dict["actor_id"] = actor_id
        my_dict["actor_name"] = actor.protocol.username
        my_dict["actor_recall_site"] = actor.recall_site
        my_dict["actor_date_of_creation"] = actor.date_of_creation
        my_dict["actor_date_of_last_login"] = actor.date_of_last_login
        # append time spent in game
        my_dict["actor_time_in_game"] = actor.time_in_game + (
            utils.get_unix_timestamp() - actor.date_of_last_login
        )

        self.cursor.execute(
            """
            INSERT INTO actors (
                unique_id, actor_id, actor_name, actor_recall_site, actor_date_of_creation, actor_date_of_last_login, actor_time_in_game
            ) VALUES (
                :unique_id, :actor_id, :actor_name, :actor_recall_site, :actor_date_of_creation, :actor_date_of_last_login, :actor_time_in_game
            )
            ON CONFLICT(unique_id) DO UPDATE SET
                actor_id = excluded.actor_id,
                actor_name = excluded.actor_name,
                actor_recall_site = excluded.actor_recall_site,
                actor_date_of_creation = excluded.actor_date_of_creation,
                actor_date_of_last_login = excluded.actor_date_of_last_login,
                actor_time_in_game = excluded.actor_time_in_game
        """,
            my_dict,
        )

        self.cursor.execute(
            """
            DELETE FROM equipment WHERE actor_id = ?
        """,
            (actor_id,),
        )

        my_dict = {}
        my_dict["actor_id"] = actor_id

        for item_id in actor.slots_manager.slots.values():
            my_dict["item_id"] = item_id
            if item_id != None:
                self.cursor.execute(
                    """
                    INSERT INTO equipment (
                        actor_id, item_id
                    ) VALUES (
                        :actor_id, :item_id
                    )
                    """,
                    my_dict,
                )

        self.cursor.execute(
            """
            DELETE FROM skills WHERE actor_id = ?
        """,
            (actor_id,),
        )

        unequiped = []
        for eq_id in actor.slots_manager.slots.values():
            if eq_id != None:
                unequiped.append(eq_id)
                actor.inventory_unequip(
                    actor.inventory_manager.items[eq_id], silent=True
                )

        my_dict = {}
        my_dict = actor.stat_manager.stats
        my_dict["actor_id"] = actor_id
        # my_dict['mp_max'] = 0
        # my_dict['mp'] = 0

        self.cursor.execute(
            """
            INSERT INTO stats (
                actor_id, hp_max, hp,
                phy_armor, mag_armor, phy_armor_max, mag_armor_max, grit, flow, mind, soul,
                exp, lvl, pp
            ) VALUES (
                :actor_id, :hp_max, :hp,
                :phy_armor, :mag_armor, :phy_armor_max, :mag_armor_max, :grit, :flow, :mind, :soul,
                :exp, :lvl, :pp
            )
            ON CONFLICT(actor_id) DO UPDATE SET
                hp_max = excluded.hp_max,

                hp = excluded.hp,

                phy_armor = excluded.phy_armor,
                mag_armor = excluded.mag_armor,
                phy_armor_max = excluded.phy_armor_max,
                mag_armor_max = excluded.mag_armor_max,
                grit = excluded.grit,
                flow = excluded.flow,
                mind = excluded.mind,
                soul = excluded.soul,
                exp = excluded.exp,
                lvl = excluded.lvl,
                pp = excluded.pp
        """,
            my_dict,
        )

        my_dict = {}
        my_dict["actor_id"] = actor_id

        self.cursor.execute(
            """
            DELETE FROM inventory WHERE actor_id = ?
        """,
            (actor_id,),
        )

        for item in actor.inventory_manager.items.values():
            my_dict["item_id"] = item.id
            my_dict["item_keep"] = item.keep
            my_dict["premade_id"] = item.premade_id
            my_dict["item_stack"] = item.stack

            self.cursor.execute(
                """
                INSERT INTO inventory (
                    actor_id, premade_id, item_id, item_keep, item_stack
                ) VALUES (
                    :actor_id, :premade_id, :item_id, :item_keep, :item_stack
                )
                """,
                my_dict,
            )

        my_dict = {}
        my_dict["actor_id"] = actor_id

        for skill_id in actor.skill_manager.skills:
            my_dict["skill_id"] = skill_id
            my_dict["skill_lvl"] = actor.skill_manager.skills[skill_id]
            if skill_id != None:
                self.cursor.execute(
                    """
                    INSERT INTO skills (
                        actor_id, skill_id, skill_lvl
                    ) VALUES (
                        :actor_id, :skill_id, :skill_lvl
                    )
                    """,
                    my_dict,
                )

        self.cursor.execute(
            """
            DELETE FROM equipment_bonuses WHERE actor_id = ?
        """,
            (actor_id,),
        )

        my_dict = {}
        my_dict["actor_id"] = actor_id
        for item in actor.inventory_manager.items.values():
            if item.item_type == ItemType.EQUIPMENT:
                bonuses = item.manager.bonuses
                for id in item.manager.bonuses:
                    bonus = bonuses[id]
                    if bonus.premade_bonus:
                        continue

                    my_dict["item_id"] = item.id
                    my_dict["id"] = id
                    my_dict["type"] = bonus.type
                    my_dict["key"] = bonus.key
                    my_dict["val"] = bonus.val
                    self.cursor.execute(
                        """
                        INSERT INTO equipment_bonuses (
                            actor_id, item_id, id, type, key, val
                        ) VALUES (
                            :actor_id, :item_id, :id, :type, :key, :val
                        )
                        """,
                        my_dict,
                    )

        for eq_id in unequiped:
            actor.inventory_equip(actor.inventory_manager.items[eq_id], forced=True)

        my_dict = {}
        my_dict["actor_id"] = actor_id

        self.cursor.execute(
            """
            DELETE FROM quests WHERE actor_id = ?
        """,
            (actor_id,),
        )

        for quest in actor.quest_manager.quests.values():
            # if quest.id == 'daily_quest':
            #    continue

            for objective in quest.objectives.values():
                # utils.debug_print(objective)
                my_dict["quest_id"] = objective.quest_id
                my_dict["objective_name"] = objective.name
                my_dict["objective_type"] = objective.type
                my_dict["objective_requirement_id"] = objective.requirement_id
                my_dict["objective_count"] = objective.count
                my_dict["objective_goal"] = objective.goal
                self.cursor.execute(
                    """
                    INSERT INTO quests (
                        actor_id, quest_id, objective_name, objective_requirement_id, objective_type, objective_count, objective_goal
                    ) VALUES (
                        :actor_id, :quest_id, :objective_name, :objective_requirement_id, :objective_type, :objective_count, :objective_goal
                    )
                    """,
                    my_dict,
                )

        my_dict = {}
        my_dict["actor_id"] = actor_id

        self.cursor.execute(
            """
            DELETE FROM settings_aliases WHERE actor_id = ?
        """,
            (actor_id,),
        )

        for key in actor.settings_manager.aliases:
            value = actor.settings_manager.aliases[key]
            my_dict["key"] = key
            my_dict["value"] = value
            self.cursor.execute(
                """
                INSERT INTO settings_aliases (
                    actor_id, key, value
                ) VALUES (
                    :actor_id, :key, :value
                )
                """,
                my_dict,
            )

        my_dict = {}
        my_dict["actor_id"] = actor_id

        self.cursor.execute(
            """
            DELETE FROM settings WHERE actor_id = ?
        """,
            (actor_id,),
        )
        my_dict["gmcp"] = actor.settings_manager.gmcp
        my_dict["view_room"] = actor.settings_manager.view_room
        my_dict["view_map"] = actor.settings_manager.view_map
        my_dict["view_ascii_art"] = actor.settings_manager.view_ascii_art
        my_dict["prompt"] = actor.settings_manager.prompt
        my_dict["email"] = actor.settings_manager.email
        self.cursor.execute(
            """
            INSERT INTO settings (
                actor_id, gmcp, view_room, view_map, view_ascii_art, prompt, email
            ) VALUES (
                :actor_id, :gmcp, :view_room, :view_map, :view_ascii_art, :prompt, :email
            )
        """,
            my_dict,
        )

        # self.cursor.execute('''
        # CREATE TABLE IF NOT EXISTS friend (
        #    actor_id TEXT NOT NULL,
        #    friend_id TEXT NOT NULL,
        #    FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        # )''')

        my_dict = {}
        my_dict["actor_id"] = actor_id
        self.cursor.execute(
            """
            DELETE FROM friend WHERE actor_id = ?
        """,
            (actor_id,),
        )

        for key in actor.friend_manager.friends:
            my_dict["actor_id"] = actor_id
            my_dict["friend_id"] = key
            # utils.debug_print(f'{actor_id} adds {key}')
            self.cursor.execute(
                """
                INSERT INTO friend (
                    actor_id, friend_id
                ) VALUES (
                    :actor_id, :friend_id
                )
            """,
                my_dict,
            )

        my_dict = {}
        my_dict["actor_id"] = actor_id
        self.cursor.execute(
            """
            DELETE FROM explored_rooms WHERE actor_id = ?
        """,
            (actor_id,),
        )

        for key in actor.explored_rooms:
            my_dict["actor_id"] = actor_id
            my_dict["room_id"] = key
            # utils.debug_print(f'{actor_id} adds {key}')
            self.cursor.execute(
                """
                INSERT INTO explored_rooms (
                    actor_id, room_id
                ) VALUES (
                    :actor_id, :room_id
                )
            """,
                my_dict,
            )

        self.write_admins(actor)
        self.conn.commit()

    def read_actor(self, unique_id):
        self.cursor.execute(
            """
            SELECT actor_id FROM actors WHERE unique_id = ?
        """,
            (unique_id,),
        )

        actor_id = self.cursor.fetchone()
        if not actor_id:
            return
        actor_id = actor_id[0]

        self.cursor.execute(
            """
            SELECT actor_name FROM actors WHERE unique_id = ?
        """,
            (unique_id,),
        )
        actor_name = self.cursor.fetchone()[0]

        self.cursor.execute(
            """
            SELECT actor_recall_site FROM actors WHERE unique_id = ?
        """,
            (unique_id,),
        )
        actor_recall_site = self.cursor.fetchone()[0]

        self.cursor.execute(
            """
            SELECT * FROM stats WHERE actor_id = ?
        """,
            (actor_id,),
        )

        stats = self.cursor.fetchone()
        # utils.debug_print('stats',stats)

        self.cursor.execute(
            """
            SELECT * FROM inventory WHERE actor_id = ?
        """,
            (actor_id,),
        )

        inventory = self.cursor.fetchall()
        # utils.debug_print('inventory',inventory)

        self.cursor.execute(
            """
            SELECT * FROM equipment WHERE actor_id = ?
        """,
            (actor_id,),
        )

        equipment = self.cursor.fetchall()
        # utils.debug_print('equipment',equipment)

        self.cursor.execute(
            """
            SELECT * FROM skills WHERE actor_id = ?
        """,
            (actor_id,),
        )

        skills = self.cursor.fetchall()
        # utils.debug_print('skills',skills)

        self.cursor.execute(
            """
            SELECT * FROM quests WHERE actor_id = ?
        """,
            (actor_id,),
        )

        quests = self.cursor.fetchall()
        # utils.debug_print('quests',quests)

        self.cursor.execute(
            """
            SELECT * FROM equipment_bonuses WHERE actor_id = ?
        """,
            (actor_id,),
        )
        bonuses = self.cursor.fetchall()
        # utils.debug_print('bonuses', bonuses)

        self.cursor.execute(
            """
            SELECT * FROM settings_aliases WHERE actor_id = ?
        """,
            (actor_id,),
        )

        settings_aliases = self.cursor.fetchall()

        self.cursor.execute(
            """
            SELECT * FROM settings WHERE actor_id = ?
        """,
            (actor_id,),
        )

        settings = self.cursor.fetchone()

        self.cursor.execute(
            """
            SELECT * FROM friend WHERE actor_id = ?
        """,
            (actor_id,),
        )

        friends = self.cursor.fetchall()

        self.cursor.execute(
            """
            SELECT * FROM explored_rooms WHERE actor_id = ?
        """,
            (actor_id,),
        )

        explored_rooms = self.cursor.fetchall()

        my_dict = {}
        my_dict["actor_id"] = actor_id
        my_dict["actor_name"] = actor_name
        my_dict["actor_recall_site"] = actor_recall_site

        self.cursor.execute(
            """
            SELECT actor_date_of_creation, actor_date_of_last_login, actor_time_in_game FROM actors WHERE actor_id = ?
        """,
            (actor_id,),
        )

        dates = self.cursor.fetchone()

        my_dict["meta_data"] = {
            "date_of_creation": dates[0],
            "date_of_last_login": dates[1],
            "time_in_game": dates[2],
        }

        my_dict["stats"] = {
            "hp_max": stats[1],
            #'mp_max': stats[2],
            "hp": stats[2],
            #'mp': stats[4],
            "grit": stats[3],
            "flow": stats[4],
            "mind": stats[5],
            "soul": stats[6],
            "phy_armor": stats[7],
            "mag_armor": stats[8],
            "phy_armor_max": stats[9],
            "mag_armor_max": stats[10],
            "exp": stats[11],
            "lvl": stats[12],
            "pp": stats[13],
        }

        my_dict["inventory"] = {}
        for item in inventory:
            my_dict["inventory"][item[2]] = {
                "item_id": item[2],
                "item_keep": item[3],
                "premade_id": item[1],
                "item_stack": item[4],
            }

        my_dict["equipment"] = []
        for eq in equipment:
            my_dict["equipment"].append(eq[1])

        my_dict["equipment_bonuses"] = {}
        for bonus in bonuses:
            boon_dict = {"type": bonus[3], "key": bonus[4], "val": bonus[5]}
            if bonus[1] in my_dict["equipment_bonuses"]:
                my_dict["equipment_bonuses"][bonus[1]].append(boon_dict)
            else:
                my_dict["equipment_bonuses"][bonus[1]] = []
                my_dict["equipment_bonuses"][bonus[1]].append(boon_dict)

        my_dict["skills"] = {}
        for skill in skills:
            my_dict["skills"][skill[1]] = skill[2]

        my_dict["quests"] = {}
        for quest in quests:
            if quest[1] in my_dict["quests"]:
                my_dict["quests"][quest[1]] = my_dict["quests"][quest[1]] | {
                    quest[2]: {
                        "type": quest[3],
                        "req_id": quest[4],
                        "count": quest[5],
                        "goal": quest[6],
                    }
                }
            else:
                my_dict["quests"][quest[1]] = {
                    quest[2]: {
                        "type": quest[3],
                        "req_id": quest[4],
                        "count": quest[5],
                        "goal": quest[6],
                    }
                }

        my_dict["settings_aliases"] = {}
        for alias in settings_aliases:
            # utils.debug_print(alias)
            my_dict["settings_aliases"][alias[1]] = alias[2]

        my_dict["settings"] = {}
        # utils.debug_print(settings)
        if settings != None:
            my_dict["settings"] = {
                "gmcp": settings[1],
                "view_room": settings[2],
                "view_map": settings[3],
                "view_ascii_art": settings[4],
                "prompt": settings[5],
                "email": settings[6],
            }

        # utils.debug_print(my_dict['settings_aliases'])
        my_dict["friends"] = []
        if friends != None:
            for friend in friends:
                # utils.debug_print('loading friend,',friend)
                my_dict["friends"].append(friend)
        # utils.debug_print(my_dict['friends'])

        # utils.debug_print(my_dict['settings_aliases'])
        my_dict["explored_rooms"] = []
        if explored_rooms != None:
            for explored_room in explored_rooms:
                # utils.debug_print('loading friend,',friend)
                my_dict["explored_rooms"].append(explored_room)
        # utils.debug_print(my_dict['friends'])

        return my_dict

    # write down admin on save
    # if your admin level is 0 dont need to write it
    def write_admins(self, actor):
        self.cursor.execute(
            """
            DELETE FROM admins WHERE actor_id = ?
        """,
            (actor.id,),
        )

        if actor.admin >= 1:
            my_dict = {"actor_id": actor.id, "admin_level": actor.admin}
            self.cursor.execute(
                """
                INSERT INTO admins (
                    actor_id, admin_level
                ) VALUES (
                    :actor_id, :admin_level
                )
                """,
                my_dict,
            )

    # read admin level
    def read_admins(self, actor):
        self.cursor.execute(
            """
            SELECT * FROM admins WHERE actor_id = ?
        """,
            (actor.id,),
        )

        admins = self.cursor.fetchone()
        return admins

    def delete(self, username):
        self.cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            AND sql LIKE '%actor_id%';
        """,
            (),
        )

        tables_actors = self.cursor.fetchall()

        self.cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            AND sql LIKE '%unique_id%';
        """,
            (),
        )

        tables_accounts = self.cursor.fetchall()

        self.cursor.execute(
            f"""
            SELECT unique_id, actor_id
            FROM actors
            WHERE actor_name = ?
            """,
            (username,),
        )

        acc = self.cursor.fetchone()
        if acc == None:
            utils.debug_print("cant remove this pogchamp")
            return
        unique_id = acc[0]
        actor_id = acc[1]

        return

        for i in tables_actors:
            self.cursor.execute(
                f"""
            DELETE FROM {i} WHERE actor_id = ?
            """,
                (actor_id,),
            )

        for i in tables_actors:
            self.cursor.execute(
                f"""
            DELETE FROM {i} WHERE unique_id = ?
            """,
                (unique_id,),
            )

    def close(self):
        # Close the database connection
        self.conn.close()


if __name__ == "__main__":
    db = Database()
    db.delete("kuro1")
