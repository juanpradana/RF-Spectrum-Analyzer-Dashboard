import sqlite3
import os

db_path = "rf_analyzer.db"

if not os.path.exists(db_path):
    print(f"Database {db_path} not found. No migration needed.")
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT file_path FROM analyses LIMIT 1")
    print("Column 'file_path' already exists. No migration needed.")
except sqlite3.OperationalError:
    print("Adding 'file_path' column to 'analyses' table...")
    cursor.execute("ALTER TABLE analyses ADD COLUMN file_path TEXT")
    conn.commit()
    print("Migration completed successfully!")

conn.close()
