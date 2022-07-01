import os
import sqlite3
import config

""" Sets up the sqlite-database, if the script is set to present/export through sqlite. """
if config.EXPORT_CHANNEL == "sqlite":
    db_filename = f"{config.OUTPUT_NAME}.sqlite"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, db_filename)
    # Makes sure to set up the sqlite-database according to the create-tables.sql-file.
    if not os.path.exists(db_filename) or config.OVERWRITE_TABLE:
        if config.VERBOSE:
            print("Creating new database file.")
        os.system("sqlite3 {} < create-tables.sql".format(db_filename))
    conn = sqlite3.connect(db_path)
