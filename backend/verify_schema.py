import sqlite3

conn = sqlite3.connect("rf_analyzer.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(analyses)")
columns = cursor.fetchall()

print("Analyses table schema:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
