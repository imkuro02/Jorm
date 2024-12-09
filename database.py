import sqlite3
import json

class Database:
    def __init__(self):
        # Connect to the database
        self.conn = sqlite3.connect('game.db')
        self.cursor = self.conn.cursor()

        # Create the users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            unique_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')

        # Create the actors table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS actors (
            unique_id TEXT PRIMARY KEY,
            data TEXT,
            FOREIGN KEY(unique_id) REFERENCES users(unique_id)
        )
        ''')
        
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

    def write_actor(self, unique_id, actor_data):
        # Serialize the actor_data dictionary to JSON
        actor_data_json = json.dumps(actor_data)

        # Insert a new actor or update the data if the actor already exists
        self.cursor.execute('''
        INSERT INTO actors (unique_id, data)
        VALUES (?, ?)
        ON CONFLICT(unique_id) DO UPDATE SET data = excluded.data
        ''', (unique_id, actor_data_json))
        
        # Commit the transaction
        #print(unique_id)
        self.conn.commit()

    def read_actor(self, unique_id):
        # Retrieve actor data based on the username
        self.cursor.execute('''
        SELECT data FROM actors WHERE unique_id = ?
        ''', (unique_id,))
        
        result = self.cursor.fetchone()
        if result is None:
            return None  # Actor does not exist
        else:
            # Deserialize JSON back to a dictionary
            actor_data = json.loads(result[0])
            return actor_data

    def close(self):
        # Close the database connection
        self.conn.close()
