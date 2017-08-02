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

import re

import signal
import time
import datetime
from urllib.request import urlopen
import zmq

import pyspark

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sip.common import heartbeat_task

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
    if len(sys.argv) < 2:
        port = 6477
    else:
        port = int(sys.argv[1])
# Define a process name to be sent to the socket
    process_name = 'PROCESS2'

# Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)
    # Create process sender
    process_sender = heartbeat_task.Sender(process_name, port)

# Spark driver
    sparkHomeDir = os.environ.get('SPARK_HOME')
    sparkSubmit = os.path.join(sparkHomeDir, 'bin/spark-submit')

# Get sipRoot
    sipRoot = str(os.environ.get('SIP_ROOT'))

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
    cmd = [sparkSubmit]
    cmd.extend(options.split(' '))
    cmd.append(jarFull)
    cmd = sparkSubmit + ' ' + options + ' --conf spark.eventLog.enabled=true --conf spark.eventLog.dir=file:///tmp/spark-events ' + jarFull
    print(cmd)

    # Submitt the command by Popen
    devnull = subprocess.DEVNULL
    pipe = subprocess.PIPE
    sdpPipeline = subprocess.Popen(cmd, stdout=devnull, stderr=pipe, shell=True)

    appID = None
    while appID is None:
        line = str(sdpPipeline.stderr.readline(), 'utf-8')
        #print(line)
        if len(line) is 0:
            # TODO clean phail
            break
        match = re.search('app-[0-9]{14}-[0-9]{4}', line)
        if match:
            appID = match.group(0)
            sdpPipeline.stderr.close() # keeping pipe open causes subprocess to stall
    if appID:
        print('appID = ' + appID)
    else:
        print('Something has gone wrong: no appID found')
        return


    import requests
    count = 0
    while count < 10:
        # Create a timestamp

        req = requests.get('http://127.0.0.1:18080/api/v1/applications/'+appID)
        print(req)
        if req.ok:
            print(req.headers['Content-Type'])
        if req.ok and 'application/json' == req.headers['Content-Type']:
            print(req.json())

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime(
                '%Y-%m-%d %H:%M:%S')

        # Check spark status
        #print(str(urlopen(url).read()))
        sparkStatus = str(urlopen(url).read()).find(idleString)
        if(sparkStatus == -1):
                _state = 'working'
        else:
                _state = 'idle'

        # Add current state to the heartbeat sequence
        st += ' State: '+_state + ': Component: '
        print(st)
        # Sent to the socket
        process_sender.send(st)
        # Wait 1 sec
        if _state is 'idle':
            count += 1;
        time.sleep(1)


if __name__ == '__main__':
        run()

