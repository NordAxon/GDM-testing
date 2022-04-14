import os
import sqlite3
import config

""" Sets up the sqlite-database, if the script is set to present/export through sqlite. """
if config.EXPORT_CHANNEL == "sqlite":
    db_filename = "test_results.sqlite"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, db_filename)
    conn = sqlite3.connect(db_path)
