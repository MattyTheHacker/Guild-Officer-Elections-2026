import sqlite3

# open db
conn: sqlite3.Connection = sqlite3.connect("../data/db/all_data.db")

# get cursor
cur: sqlite3.Cursor = conn.cursor()

# get all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")

# print all tables
tables: list[str] = [table[0] for table in cur.fetchall()]

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")

print(cur.fetchall())

for table in tables:
    cur.execute("SELECT * FROM " + table)
    print([description[0] for description in cur.description])
    print(cur.fetchall())
