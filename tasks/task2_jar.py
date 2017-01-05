#!/usr/bin/python3

""" Skeleton spark task to be started by slave

It has three states - standby, working and idle, indicating the status
of a spark job which is started as a subprocess.

It sends heartbeat messages to the slave containing the timestamp, 
the current state and its name

"""

import sys
import os
import json
import subprocess
import redis

import signal
import time
import datetime
import zmq
from urllib.request import urlopen

sys.path.append(os.path.join(os.path.dirname(__file__),'..', 'common'))

from sip_common import heartbeat_task

_context = zmq.Context()

# The state of the task
_state = 'standby'

def _sig_handler(signum, frame):
	sys.exit(0)

# Spark url
url="http://localhost:8080"

# The string in html indicating no running spark applications
idleString = '0 <a href="#running-app">Running</a>'

def run():

# Read port number
	if len(sys.argv) < 2 :
		port = 6477
	else :
		port = int(sys.argv[1])
# Define a process name to be sent to the socket
	process_name = 'PROCESS2'

    # Install handler to respond to SIGTERM
	signal.signal(signal.SIGTERM, _sig_handler)
	# Create process sender	
	process_sender = heartbeat_task.Sender(process_name, port)

# Spark driver

	r = redis.StrictRedis()
	sparkHomeDir = r.get("spark_home").decode("ascii")
#	sparkHomeDir = os.environ.get('SPARK_HOME')
	sparkSubmit = os.path.join(sparkHomeDir, 'bin/spark-submit')

# Get sipRoot
	sipRoot = r.get("sip_root").decode("ascii") + "/"
#	sipRoot = str(os.environ.get('SIP_ROOT'))

# Read parameters from json file
	with open(sipRoot + 'tasks/spark_config.json') as data_file:    
		data = json.load(data_file)

# Get options for spark driver
	options = ''	
	for x in data["parameters"]:
		options += x + ' ' + data["parameters"][x] + ' '		
	print(options)

# Get jar name
	jarDir  = data["pipeline"]["jarPath"]
	jarName = data["pipeline"]["jarName"] 
	jarFull = os.path.join(jarDir, jarName)

# Create the command		
	cmd = sparkSubmit + ' ' + options + ' ' + jarFull
	print(cmd)

# Submitt the command by Popen
	sdpPipeline = subprocess.Popen(cmd, shell=True)

	while True:
		# Create a timestamp

		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime(
                        '%Y-%m-%d %H:%M:%S')

		# Check spark status
		sparkStatus = str(urlopen(url).read()).find(idleString)
		if(sparkStatus == -1):
			_state = 'working'
		else:
			_state = 'idle'						

		# Add current state to the heartbeat sequence
		st += ' State: '+_state + ': Component: '
		# Sent to the socket
		process_sender.send(st)
		# Wait 1 sec
		time.sleep(1)
	

if __name__ == '__main__':
	run()

