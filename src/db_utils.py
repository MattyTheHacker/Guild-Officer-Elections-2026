import datetime
import sqlite3
import traceback
import sys
import os
import json

from typing import Final

from data_objects import ElectionData, Group, GroupItem


def save_to_db(data: ElectionData, date_generated: datetime.datetime) -> None:
    # we're going to have a separate table for different sets of data:
    # departments, year, type (UG, PGR, PGT) etc...

    db_file_path: str = "../data/db/all_data.db"

    if not os.path.exists(db_file_path):
        print("[ERROR] Database file does not exist. A new one will be created...")

    conn: sqlite3.Connection = sqlite3.connect(db_file_path)
    cur: sqlite3.Cursor = conn.cursor()

    groups: list[Group] = data["Groups"]
    group: Group
    for group in groups:
        table_name: str = group["Name"].replace(" ", "_").lower()
        cur.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )

        if cur.fetchone() is None:
            print("[ERROR] Table " + table_name + " does not exist. Creating it now...")
            cur.execute(
                f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, eligible INTEGER, voters INTEGER, turnout REAL, timestamp TEXT)"
            )

        group_data: GroupItem
        for group_data in group["Items"]:
            insert_command: str = (
                "INSERT INTO "
                + table_name
                + " (name, eligible, voters, turnout, timestamp) VALUES (?, ?, ?, ?, ?)"
            )
            try:
                cur.execute(
                    insert_command,
                    (
                        group_data["Name"],
                        group_data["Eligible"],
                        group_data["Voters"],
                        group_data["Turnout"],
                        date_generated.isoformat(),
                    ),
                )
                conn.commit()
            except sqlite3.Error as er:
                print("SQLite error: %s" % (" ".join(er.args)))
                print("Exception class is: ", er.__class__)
                print("SQLite traceback: ")
                exc_type, exc_value, exc_tb = sys.exc_info()
                print(traceback.format_exception(exc_type, exc_value, exc_tb))

    conn.commit()

    conn.close()

def combine_student_group_data() -> None:
    DB_FILE_PATH: Final[str] = "../data/db/all_data.db"

    if not os.path.exists(DB_FILE_PATH):
        print("[ERROR] Database file does not exist. Aborting...")
        return

    conn: sqlite3.Connection = sqlite3.connect(DB_FILE_PATH)
    cur: sqlite3.Cursor = conn.cursor()

    cur.execute(
        "DROP TABLE IF EXISTS all_student_groups"
    )

    # create new table first
    cur.execute(
        "CREATE TABLE all_student_groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, eligible INTEGER, voters INTEGER, turnout REAL, timestamp TEXT)"
    )

    TABLES: Final[list[str]] = ["associations", "medsoc_societies_and_sports_clubs", "societies", "volunteering_groups"]

    table: str
    for table in TABLES:
        cur.execute(
            f"INSERT INTO all_student_groups (name, eligible, voters, turnout, timestamp) SELECT name, eligible, voters, turnout, timestamp FROM {table}"
        )

    # remove any rows with "All other organisations" in the name
    cur.execute(
        "DELETE FROM all_student_groups WHERE name = 'All other organisations'"
    )

    conn.commit()
    conn.close()


def separate_turnout_data() -> None:
    DB_FILE_PATH: Final[str] = "../data/db/all_data.db"

    if not os.path.exists(DB_FILE_PATH):
        print("[ERROR] Database file does not exist. Aborting...")
        return
    
    data: dict[str, float] = {}

    for file in os.listdir("../data/json/raw/"):

        election_data: ElectionData = json.load(open("../data/json/raw/" + file))
        date_generated: datetime.datetime = datetime.datetime.fromisoformat(election_data["DateGenerated"])
        turnout: float = election_data["Turnout"]
        data[date_generated.isoformat()] = turnout
    
    conn: sqlite3.Connection = sqlite3.connect(DB_FILE_PATH)
    cur: sqlite3.Cursor = conn.cursor()

    cur.execute(
        "DROP TABLE IF EXISTS turnout_data"
    )

    cur.execute(
        "CREATE TABLE turnout_data (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, turnout REAL)"
    )

    for timestamp, turnout in data.items():
        cur.execute(
            "INSERT INTO turnout_data (timestamp, turnout) VALUES (?, ?)",
            (timestamp, turnout)
        )

    conn.commit()
    conn.close()


def separate_total_vote_count() -> None:
    DB_FILE_PATH: Final[str] = "../data/db/all_data.db"

    if not os.path.exists(DB_FILE_PATH):
        print("[ERROR] Database file does not exist. Aborting...")
        return
    
    data: dict[str, int] = {}

    for file in os.listdir("../data/json/raw/"):

        election_data: ElectionData = json.load(open("../data/json/raw/" + file))
        date_generated: datetime.datetime = datetime.datetime.fromisoformat(election_data["DateGenerated"])
        total_votes: int = election_data["Voters"]
        data[date_generated.isoformat()] = total_votes
    
    conn: sqlite3.Connection = sqlite3.connect(DB_FILE_PATH)
    cur: sqlite3.Cursor = conn.cursor()

    cur.execute(
        "DROP TABLE IF EXISTS total_vote_count"
    )

    cur.execute(
        "CREATE TABLE total_vote_count (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, vote_count INTEGER)"
    )

    for timestamp, vote_count in data.items():
        cur.execute(
            "INSERT INTO total_vote_count (timestamp, vote_count) VALUES (?, ?)",
            (timestamp, vote_count)
        )

    conn.commit()
    conn.close()
