"""
Database migration script to add new columns to licensed_stations table.
Run this script once to update existing database schema.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'rf_analyzer.db')

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(licensed_stations)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    columns_to_add = [
        ('eq_mfr', 'TEXT'),
        ('eq_mdl', 'TEXT'),
        ('emis_class_1', 'TEXT'),
    ]
    
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE licensed_stations ADD COLUMN {col_name} {col_type}")
                print(f"Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"Error adding {col_name}: {e}")
        else:
            print(f"Column already exists: {col_name}")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
