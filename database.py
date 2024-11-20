import sqlite3
import json

class Database:
    def __init__(self):
        # Connect to the database
        self.conn = sqlite3.connect('game.db')
        self.cursor = self.conn.cursor()

        # Create the users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        ''')

        # Create the actors table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS actors (
            username TEXT PRIMARY KEY,
            data TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
        ''')
        
        # Commit changes
        self.conn.commit()

    def write_user(self, username, password):
        # Insert a new user or update the password if the user already exists
        self.cursor.execute('''
        INSERT INTO users (username, password)
        VALUES (?, ?)
        ON CONFLICT(username) DO UPDATE SET password = excluded.password
        ''', (username, password))
        
        # Commit the transaction
        self.conn.commit()

    def read_user(self, username):
        # Retrieve user data based on the username
        self.cursor.execute('''
        SELECT username, password FROM users WHERE username = ?
        ''', (username,))
        
        user = self.cursor.fetchone()
        return user  # Returns None if the user doesn't exist, otherwise returns (username, password)

    def write_actor(self, username, actor_data):
        # Serialize the actor_data dictionary to JSON
        actor_data_json = json.dumps(actor_data)

        # Insert a new actor or update the data if the actor already exists
        self.cursor.execute('''
        INSERT INTO actors (username, data)
        VALUES (?, ?)
        ON CONFLICT(username) DO UPDATE SET data = excluded.data
        ''', (username, actor_data_json))
        
        # Commit the transaction
        self.conn.commit()

    def read_actor(self, username):
        # Retrieve actor data based on the username
        self.cursor.execute('''
        SELECT data FROM actors WHERE username = ?
        ''', (username,))
        
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
