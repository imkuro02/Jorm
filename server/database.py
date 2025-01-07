import sqlite3
import json


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
            FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS equipment (
            actor_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            FOREIGN KEY(item_id) REFERENCES inventory(item_id)
        )''')

        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS skills (
            actor_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            skill_lvl INT NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES inventory(actor_id)
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

        #print(my_dict)

        self.cursor.execute('''
            INSERT INTO actors (
                unique_id, actor_id, actor_name
            ) VALUES (
                :unique_id, :actor_id, :actor_name
            )
            ON CONFLICT(unique_id) DO UPDATE SET
                actor_id = excluded.actor_id
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

        for eq_id in actor.slots_manager.slots.values():
            if eq_id != None:
                actor.inventory_unequip(actor.inventory_manager.items[eq_id])

        my_dict = {}
        my_dict = actor.stats
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

            self.cursor.execute('''
                INSERT INTO inventory (
                    actor_id, premade_id, item_id, item_keep
                ) VALUES (
                    :actor_id, :premade_id, :item_id, :item_keep
                )
                ''', my_dict)

        my_dict = {}
        my_dict['actor_id'] = actor_id

        for skill_id in actor.skills:
            my_dict['skill_id'] = skill_id
            my_dict['skill_lvl'] = actor.skills[skill_id]
            if skill_id != None:
                self.cursor.execute('''
                    INSERT INTO skills (
                        actor_id, skill_id, skill_lvl
                    ) VALUES (
                        :actor_id, :skill_id, :skill_lvl
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
        
        #print(actor_id)

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

        my_dict = {}
        my_dict['actor_id'] = actor_id
        my_dict['actor_name'] = actor_name

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
                'premade_id': item[1]
            }

        my_dict['equipment'] = []
        for eq in equipment:
            my_dict['equipment'].append(eq[1])

        my_dict['skills'] = {}
        for skill in skills:
            my_dict['skills'][skill[1]] = skill[2]

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
      
    def close(self):
        # Close the database connection
        self.conn.close()
