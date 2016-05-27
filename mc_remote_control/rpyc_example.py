"""This is a simple example showing how to communicate with
the master controller - with and without a callback

use as 'python3 rpyc_example.py'
"""
import rpyc

# Define a very simple callback function
def callb(x):
   print(x)

# Connect to server
conn = rpyc.connect("localhost",port=12345)

# Send online with callback
conn.root.command("online",callb)

# and silently go offline again
conn.root.command("offline")


