import sqlite3

def get_all_tables_and_values(database_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Get all table names in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Loop through each table and get its data
    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")
        
        # Get all rows from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in cursor.description]
        print(f"Columns: {column_names}")

        # Print all rows from the table
        for row in rows:
            print(row)
        
        print("\n" + "-"*50 + "\n")
    
    # Close the connection
    conn.close()

# Example usage
database_path = 'database.db'  # Path to your SQLite database file
get_all_tables_and_values(database_path)
