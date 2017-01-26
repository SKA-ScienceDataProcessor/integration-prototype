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
import urllib

sys.path.append(os.path.join(os.path.dirname(__file__),'..', 'common'))

from sip_common import heartbeat_task

_context = zmq.Context()

# The state of the task
_state = 'standby'

def _sig_handler(signum, frame):
	sys.exit(0)

# The string in html indicating no running spark applications
idleString = '0 <a href="#running-app">Running</a>'

# Define API for status request, "http" or "rest"
checkType = "rest"

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

# Get spark host name
	sparkHost = data["parameters"]['--master']
# Remove leading "spark://" and trailing ":7077" (assuming the parameter --master is in the form of spark://hostname.domain:XXXX)
	sparkHost = sparkHost[8:-5] 

	if(checkType == "rest"):
# Spark REST IP url
		url= "http://" + sparkHost + ":4040/api/v1/applications"
	else:
# Spark HTTP url
		url="http://" + sparkHost + ":8080"

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

		if(checkType == "rest"):
		# Check spark status (REST API version)
			try:
		# If spark application is running, read it's status
				response = urlopen(url)
				dataREST = json.loads(str(response.read().decode('utf-8')))
				_state = 'busy'
				appID = dataREST[0]['id']
				print("Task2_jar: Status = busy, app id is ", appID)
		# If spark application is not running, have an error when trying to query URL
			except urllib.error.URLError as err:
				appID = "None"
				_state = 'idle'						
				print("Task2_jar: ERROR: Can not open url ", url, " ", err, " app id is ", appID)
				print("Task2_jar: Status = idle")
		else:

		# Check spark status (HTTP version) - search for idleString showing no application is running
			sparkStatus = str(urlopen(url).read()).find(idleString)
			if(sparkStatus == -1):
				_state = 'busy'
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

