import sqlite3
import json

# Connect to the database
conn = sqlite3.connect('game.db')
cursor = conn.cursor()

# Fetch all rows
cursor.execute("SELECT id, data FROM actors")
rows = cursor.fetchall()

for monster_id, data in rows:
    # Parse JSON data
    monster_data = json.loads(data)
    
    # Rename key 'hp' to 'health'
    if 'hp' in monster_data:
        monster_data['health'] = monster_data.pop('hp')
    
    # Convert back to JSON and update the database
    updated_data = json.dumps(monster_data)
    cursor.execute("UPDATE monsters SET data = ? WHERE id = ?", (updated_data, monster_id))

# Commit changes and close the connection
conn.commit()
conn.close()