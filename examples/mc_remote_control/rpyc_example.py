"""This is a simple example showing how to communicate with
the master controller - with and without a callback

use as 'python3 rpyc_example.py'
"""
import rpyc
import time

# Define a very simple callback function
def callb(x):
   print(x)

# Connect to server
conn = rpyc.connect("localhost",port=12345)

# Send online with callback
conn.root.online(callb)

# Give it some time to configure
time.sleep(10)

# and silently go offline again
conn.root.offline()

# print current state
print("Master Controller state is:",conn.root.get_current_state())



