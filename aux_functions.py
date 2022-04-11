import os
import sqlite3

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "test_results.sqlite")
conn = sqlite3.connect(db_path)