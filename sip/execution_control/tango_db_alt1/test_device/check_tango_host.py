# coding: utf-8
"""."""
from tango import Database

# Get reference to tango database
db = Database()
print(db.get_info())
