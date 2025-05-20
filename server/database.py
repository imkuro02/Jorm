import sqlite3
import json
import utils
from configuration.config import ItemType
class Database:
    def __init__(self):
        # Connect to the database
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

        # Create the users table
        self.cursor.execute('''          
        CREATE TABLE IF NOT EXISTS accounts (
            unique_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )''')

        # Create admins table
        self.cursor.execute('''          
            CREATE TABLE IF NOT EXISTS admins (
                actor_id TEXT,
                admin_level INT
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS actors (
            unique_id TEXT UNIQUE NOT NULL,
            actor_id TEXT PRIMARY KEY NOT NULL,
            actor_name TEXT NOT NULL,
            actor_recall_site TEXT NOT NULL,
            actor_date_of_creation INT NOT NULL,
            actor_date_of_last_login INT NOT NULL,
            actor_time_in_game INT NOT NULL,
            FOREIGN KEY(unique_id) REFERENCES users(unique_id)
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS stats (
            actor_id TEXT PRIMARY KEY,
            hp_max INT NOT NULL,
            mp_max INT NOT NULL,
            hp INT NOT NULL,
            mp INT NOT NULL,
            grit INT NOT NULL,
            flow INT NOT NULL,
            mind INT NOT NULL,
            soul INT NOT NULL,
            armor INT NOT NULL,
            marmor INT NOT NULL,
            exp INT NOT NULL,
            lvl INT NOT NULL,
            pp INT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS inventory (
            actor_id TEXT NOT NULL,
            premade_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            item_keep BOOL NOT NULL,
            item_stack INT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS equipment (
            actor_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            FOREIGN KEY(item_id) REFERENCES inventory(item_id)
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS equipment_bonuses (
            actor_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            id TEXT NOT NULL,
            type TEXT NOT NULL,
            key TEXT NOT NULL,
            val INT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS skills (
            actor_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            skill_lvl INT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES inventory(actor_id)
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS quests (
            actor_id TEXT NOT NULL,
            quest_id TEXT NOT NULL,
            objective_id TEXT NOT NULL,
            objective_count INT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS settings_aliases (
            actor_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS settings (
            actor_id TEXT PRIMARY KEY,
            gmcp BOOL NOT NULL,
            view_room BOOL NOT NULL,
            view_map BOOL NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )''')

        # Commit changes
        self.conn.commit()

    def find_account_from_username(self, username):
        self.cursor.execute(
            '''
                SELECT unique_id, username, password 
                FROM accounts WHERE username = ?
            ''', (username,))

        account = self.cursor.fetchone()
        
        
        return account

    def find_all_accounts(self):
        self.cursor.execute(
            '''
                SELECT unique_id, username, password 
                FROM accounts 
            ''')
        
        accounts = self.cursor.fetchall()

        actor_objs = []
        # Iterate through each account and create the actor object
        for acc in accounts:

            # Fetch account details
            actor = self.read_actor(acc[0])  # Assuming acc[0] is the account ID or relevant identifier
            # 'quests': {'tutorial_1': {'Get a corpse': 0, 'turned_in': 1}
            if actor == None:
                continue
            
            # Create actor_obj and append to the list
            actor_obj = {
                'name': acc[1],  # Assuming acc[1] is the account's name
                'exp': actor['stats']['exp'],  # Extract experience points from actor stats
                'lvl': actor['stats']['lvl'],  # Extract level from actor stats
                'date_of_creation': actor['meta_data']['date_of_creation'],
                'date_of_last_login': actor['meta_data']['date_of_last_login'],
                'time_in_game': actor['meta_data']['time_in_game'], 
                'quests_turned_in': len([q for q in actor['quests'].values() if q['turned_in'] == 1]) 
            }
            actor_objs.append(actor_obj)


        # Sort actor_objs list from most experience to least experience
        sorted_actor_objs = sorted(actor_objs, key=lambda x: x['exp'], reverse=True)

        # Print the sorted list of actor objects
        #for actor in sorted_actor_objs:
        #    print(actor)
        return sorted_actor_objs
        
    def create_new_account(self, unique_id, username, password):
        self.cursor.execute('''
            INSERT INTO accounts (unique_id, username, password)
            VALUES (?, ?, ?)
            ON CONFLICT(unique_id) DO UPDATE SET 
                username = excluded.username,
                password = excluded.password
        ''', (unique_id, username, password))
        self.conn.commit()

    def write_actor(self, actor):
        actor_id = actor.id
        
        my_dict = {}
        my_dict['unique_id'] = actor.protocol.id
        my_dict['actor_id'] = actor_id
        my_dict['actor_name'] = actor.protocol.username
        my_dict['actor_recall_site'] = actor.recall_site
        my_dict['actor_date_of_creation'] = actor.date_of_creation
        my_dict['actor_date_of_last_login'] = actor.date_of_last_login
        # append time spent in game
        my_dict['actor_time_in_game'] = actor.time_in_game + (utils.get_unix_timestamp() - actor.date_of_last_login)

        self.cursor.execute('''
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
        ''', my_dict)
        
        self.cursor.execute('''
            DELETE FROM equipment WHERE actor_id = ?
        ''', (actor_id,))

        my_dict = {}
        my_dict['actor_id'] = actor_id

        for item_id in actor.slots_manager.slots.values():
            my_dict['item_id'] = item_id
            if item_id != None:
                
                self.cursor.execute('''
                    INSERT INTO equipment (
                        actor_id, item_id
                    ) VALUES (
                        :actor_id, :item_id
                    )
                    ''', my_dict)
                
        self.cursor.execute('''
            DELETE FROM skills WHERE actor_id = ?
        ''', (actor_id,))

        unequiped = []
        for eq_id in actor.slots_manager.slots.values():
            if eq_id != None:
                unequiped.append(eq_id)
                actor.inventory_unequip(actor.inventory_manager.items[eq_id], silent = True)

        my_dict = {}
        my_dict = actor.stat_manager.stats
        my_dict['actor_id'] = actor_id

        self.cursor.execute('''
            INSERT INTO stats (
                actor_id, hp_max, mp_max, hp, mp,
                armor, marmor, grit, flow, mind, soul,
                exp, lvl, pp
            ) VALUES (
                :actor_id, :hp_max, :mp_max, :hp, :mp,
                :armor, :marmor, :grit, :flow, :mind, :soul,
                :exp, :lvl, :pp
            )
            ON CONFLICT(actor_id) DO UPDATE SET
                hp_max = excluded.hp_max,
                mp_max = excluded.mp_max,
                hp = excluded.hp,
                mp = excluded.mp,
                armor = excluded.armor,
                marmor = excluded.marmor,
                grit = excluded.grit,
                flow = excluded.flow,
                mind = excluded.mind,
                soul = excluded.soul,
                exp = excluded.exp,
                lvl = excluded.lvl,
                pp = excluded.pp
        ''', my_dict)

        

        my_dict = {}
        my_dict['actor_id'] = actor_id

        self.cursor.execute('''
            DELETE FROM inventory WHERE actor_id = ?
        ''', (actor_id,))
        
        for item in actor.inventory_manager.items.values():
            my_dict['item_id'] = item.id
            my_dict['item_keep'] = item.keep
            my_dict['premade_id'] = item.premade_id
            my_dict['item_stack'] = item.stack

            self.cursor.execute('''
                INSERT INTO inventory (
                    actor_id, premade_id, item_id, item_keep, item_stack
                ) VALUES (
                    :actor_id, :premade_id, :item_id, :item_keep, :item_stack
                )
                ''', my_dict)

        my_dict = {}
        my_dict['actor_id'] = actor_id

        for skill_id in actor.skill_manager.skills:
            my_dict['skill_id'] = skill_id
            my_dict['skill_lvl'] = actor.skill_manager.skills[skill_id]
            if skill_id != None:
                self.cursor.execute('''
                    INSERT INTO skills (
                        actor_id, skill_id, skill_lvl
                    ) VALUES (
                        :actor_id, :skill_id, :skill_lvl
                    )
                    ''', my_dict)



        self.cursor.execute('''
            DELETE FROM equipment_bonuses WHERE actor_id = ?
        ''', (actor_id,))

        my_dict = {}
        my_dict['actor_id'] = actor_id
        for item in actor.inventory_manager.items.values():
            if item.item_type == ItemType.EQUIPMENT:
                bonuses = item.manager.bonuses
                for id in item.manager.bonuses:

                    bonus = bonuses[id]
                    if bonus.premade_bonus:
                        continue

                    my_dict['item_id'] = item.id
                    my_dict['id'] = id
                    my_dict['type'] = bonus.type
                    my_dict['key'] = bonus.key
                    my_dict['val'] = bonus.val
                    self.cursor.execute('''
                        INSERT INTO equipment_bonuses (
                            actor_id, item_id, id, type, key, val
                        ) VALUES (
                            :actor_id, :item_id, :id, :type, :key, :val
                        )
                        ''', my_dict)


                
        for eq_id in unequiped:
            actor.inventory_equip(actor.inventory_manager.items[eq_id], forced = True)
            
        my_dict = {}
        my_dict['actor_id'] = actor_id

        self.cursor.execute('''
            DELETE FROM quests WHERE actor_id = ?
        ''', (actor_id,))
        
        for quest in actor.quest_manager.quests.values():
            for objective in quest.objectives.values():
                #print(objective)
                my_dict['quest_id'] = objective.quest_id
                my_dict['objective_id'] = objective.name
                my_dict['objective_count'] = objective.count
                self.cursor.execute('''
                    INSERT INTO quests (
                        actor_id, quest_id, objective_id, objective_count
                    ) VALUES (
                        :actor_id, :quest_id, :objective_id, :objective_count
                    )
                    ''', my_dict)

        my_dict = {}
        my_dict['actor_id'] = actor_id

        self.cursor.execute('''
            DELETE FROM settings_aliases WHERE actor_id = ?
        ''', (actor_id,))
        
        for key in actor.settings_manager.aliases:
            value = actor.settings_manager.aliases[key]
            my_dict['key'] = key
            my_dict['value'] = value
            self.cursor.execute('''
                INSERT INTO settings_aliases (
                    actor_id, key, value
                ) VALUES (
                    :actor_id, :key, :value
                )
                ''', my_dict)


        my_dict = {}
        my_dict['actor_id'] = actor_id

        self.cursor.execute('''
            DELETE FROM settings WHERE actor_id = ?
        ''', (actor_id,))
        my_dict['gmcp'] = actor.settings_manager.gmcp
        my_dict['view_room'] = actor.settings_manager.view_room
        my_dict['view_map'] = actor.settings_manager.view_map
        self.cursor.execute('''
            INSERT INTO settings (
                actor_id, gmcp, view_room, view_map
            ) VALUES (
                :actor_id, :gmcp, :view_room, :view_map
            )
        ''', my_dict)
                
        self.write_admins(actor)
        self.conn.commit()

    def read_actor(self, unique_id):

        self.cursor.execute('''
            SELECT actor_id FROM actors WHERE unique_id = ?
        ''', (unique_id,))

        actor_id = self.cursor.fetchone()
        if not actor_id:
            return
        actor_id = actor_id[0]

        self.cursor.execute('''
            SELECT actor_name FROM actors WHERE unique_id = ?
        ''', (unique_id,))
        actor_name = self.cursor.fetchone()[0]

        self.cursor.execute('''
            SELECT actor_recall_site FROM actors WHERE unique_id = ?
        ''', (unique_id,))
        actor_recall_site = self.cursor.fetchone()[0]

        self.cursor.execute('''
            SELECT * FROM stats WHERE actor_id = ?
        ''', (actor_id,))

        stats = self.cursor.fetchone()
        #print('stats',stats)

        self.cursor.execute('''
            SELECT * FROM inventory WHERE actor_id = ?
        ''', (actor_id,))

        inventory = self.cursor.fetchall()
        #print('inventory',inventory)

        self.cursor.execute('''
            SELECT * FROM equipment WHERE actor_id = ?
        ''', (actor_id,))

        equipment = self.cursor.fetchall()
        #print('equipment',equipment)

        self.cursor.execute('''
            SELECT * FROM skills WHERE actor_id = ?
        ''', (actor_id,))

        skills = self.cursor.fetchall()
        #print('skills',skills)

        self.cursor.execute('''
            SELECT * FROM quests WHERE actor_id = ?
        ''', (actor_id,))

        quests = self.cursor.fetchall()
        #print('quests',quests)

        self.cursor.execute('''
            SELECT * FROM equipment_bonuses WHERE actor_id = ?
        ''', (actor_id,))
        bonuses = self.cursor.fetchall()
        #print('bonuses', bonuses)

        self.cursor.execute('''
            SELECT * FROM settings_aliases WHERE actor_id = ?
        ''', (actor_id,))

        settings_aliases = self.cursor.fetchall()

        self.cursor.execute('''
            SELECT * FROM settings WHERE actor_id = ?
        ''', (actor_id,))

        settings = self.cursor.fetchall()


        my_dict = {}
        my_dict['actor_id'] = actor_id
        my_dict['actor_name'] = actor_name
        my_dict['actor_recall_site'] = actor_recall_site

        self.cursor.execute('''
            SELECT actor_date_of_creation, actor_date_of_last_login, actor_time_in_game FROM actors WHERE actor_id = ?
        ''', (actor_id,))
        
        dates = self.cursor.fetchone()

        my_dict['meta_data'] = {
            'date_of_creation': dates[0],
            'date_of_last_login':  dates[1],
            'time_in_game': dates[2]
        }

        my_dict['stats'] = {
            'hp_max': stats[1],
            'mp_max': stats[2],
            'hp': stats[3],
            'mp': stats[4],
            'grit':stats[5],
            'flow':stats[6],
            'mind': stats[7],
            'soul': stats[8],
            'armor': stats[9],
            'marmor': stats[10],
            'exp': stats[11],
            'lvl': stats[12],
            'pp': stats[13],
        }

        my_dict['inventory'] = {}
        for item in inventory:
            my_dict['inventory'][item[2]] = {        
                'item_id': item[2],
                'item_keep': item[3],
                'premade_id': item[1],
                'item_stack': item[4]
            }

        my_dict['equipment'] = []
        for eq in equipment:
            my_dict['equipment'].append(eq[1])

        my_dict['equipment_bonuses'] = {}
        for bonus in bonuses:
            boon_dict = {
                'type': bonus[3],
                'key': bonus[4],
                'val': bonus[5]
                }
            if bonus[1] in my_dict['equipment_bonuses']:
                my_dict['equipment_bonuses'][bonus[1]].append(boon_dict)
            else:
                my_dict['equipment_bonuses'][bonus[1]] = []
                my_dict['equipment_bonuses'][bonus[1]].append(boon_dict)
                

        my_dict['skills'] = {}
        for skill in skills:
            my_dict['skills'][skill[1]] = skill[2]

        my_dict['quests'] = {}
        for quest in quests:
            
            if quest[1] in my_dict['quests']:
                
                my_dict['quests'][quest[1]] = my_dict['quests'][quest[1]] | {quest[2]: quest[3]}
            else:
                my_dict['quests'][quest[1]] = {quest[2]: quest[3]}

        
        my_dict['settings_aliases'] = {}
        for alias in settings_aliases:
            #print(alias)
            my_dict['settings_aliases'][alias[1]] = alias[2]

        my_dict['settings'] = {}
        if len(settings) == 4:
            my_dict['settings'] = {
                'gmcp': settings[1],
                'view_room': settings[2],
                'view_map': settings[3]
            }
       
        #print(my_dict['settings_aliases'])
        return my_dict
    
    # write down admin on save
    # if your admin level is 0 dont need to write it
    def write_admins(self, actor):
        self.cursor.execute('''
            DELETE FROM admins WHERE actor_id = ?
        ''', (actor.id,))

        if actor.admin >= 1:
            my_dict = {'actor_id': actor.id, 'admin_level': actor.admin}
            self.cursor.execute('''
                INSERT INTO admins (
                    actor_id, admin_level
                ) VALUES (
                    :actor_id, :admin_level
                )
                ''', my_dict)

    # read admin level
    def read_admins(self, actor):
        self.cursor.execute('''
            SELECT * FROM admins WHERE actor_id = ?
        ''', (actor.id, ))

        admins = self.cursor.fetchone()
        return admins

    def delete(self, username):
        self.cursor.execute('''
            SELECT name 
            FROM sqlite_master 
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            AND sql LIKE '%actor_id%';
        ''', ())

        tables_actors = self.cursor.fetchall()
        
        self.cursor.execute('''
            SELECT name 
            FROM sqlite_master 
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            AND sql LIKE '%unique_id%';
        ''', ())

        tables_accounts = self.cursor.fetchall()

        self.cursor.execute(f'''
            SELECT unique_id, actor_id
            FROM actors
            WHERE actor_name = ?
            ''',(username,))
        
        acc = self.cursor.fetchone()
        if acc == None:
            print('cant remove this pogchamp')
            return
        unique_id = acc[0]
        actor_id = acc[1]
        
        return

        for i in tables_actors:
            self.cursor.execute(f'''
            DELETE FROM {i} WHERE actor_id = ?
            ''', (actor_id,))

        for i in tables_actors:
            self.cursor.execute(f'''
            DELETE FROM {i} WHERE unique_id = ?
            ''', (unique_id,))


      
    def close(self):
        # Close the database connection
        self.conn.close()

if __name__ == '__main__':
    db = Database()
    db.delete('kuro1')