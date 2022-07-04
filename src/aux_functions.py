import os
import sqlite3
from sqlite3 import Error
from pathlib import Path


def create_sqlite(args):
    """Sets up the sqlite-database, if the script is set to present/export through sqlite."""
    if args.export_channel == "sqlite":
        db_filename = f"test_results/{args.experiment_id}.sqlite"
        db_path = Path(__file__).parents[1].resolve() / db_filename
        # Makes sure to set up the sqlite-database according to the create-tables.sql-file.
        if not db_path.exists() or args.overwrite_table:
            if args.verbose:
                print("Creating new database file.")
            os.system("sqlite3 {} < create-tables.sql".format(db_filename))
    return db_path


def create_connection(db_path):
    """Creates a connection to the database.
    Returns:
        _type_: Connection object
    """
    try:
        return sqlite3.connect(db_path)
    except Error as e:
        print(e)


def close_connection(conn):
    """Closes a connection
    Args:
        conn (_type_): Connection
    """
    try:
        if conn:
            conn.close()
        else:
            pass
    except Error as e:
        print(e)
