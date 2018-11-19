# coding: utf-8
"""."""
from tango import Database

# Get reference to tango database
DB = Database()
print('=' * 80)
print('Database info:')
print('=' * 80)
print(DB.get_info())
print('=' * 80)
print('Server list:')
print('=' * 80)
print(DB.get_server_list().value_string)
print('')
