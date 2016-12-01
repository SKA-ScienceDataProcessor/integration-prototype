#!/usr/bin/python3

""" Skeleton spark task to be started by slave

It has three states - standby, Mean and Var, toggling between
Mean and Var in a polling loop according to the timer.

It sends heartbeat messages to the slave containing the timestamp, 
the current state, the result and its name

"""

import sys
import os
import signal
import time
import datetime


sys.path.append(os.path.join(os.path.dirname(__file__),'..', 'common'))

from sip_common import heartbeat_task


# Spark environment #########

sys.path.append('/home/vlad/software.x32/spark-bin/python')
sys.path.append('/home/vlad/software.x32/spark-bin/python/lib/py4j-0.10.3-src.zip')

os.environ['PYSPARK_PYTHON'] = 'python3'

from random import random, seed
from operator import add

# Numba gives an error, possible Python 3.x - related bug
#import numba
import numpy as np
import math

from pyspark.sql import SparkSession

def f(_):
	x = random() * 2 - 1
	y = random() * 2 - 1
	return 1 if x ** 2 + y ** 2 < 1 else 0

# Numba gives an error, possible Python 3.x - related bug
#@numba.jit
#def cpu_some_trig1(x,y):
#	return (np.cos(x) + np.sin(y))


###################


# The state of the task
_state = 'standby'

def _sig_handler(signum, frame):
	spark.stop()
	sys.exit(0)

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
	mypi = 0.0

# Starting cluster spark session with proper parameters
#	spark = SparkSession\
#		.builder\
#	    	.master("spark://apvsws.ra.phy.private.cam.ac.uk:7077")\
#		.appName("SIP_task2_PythonPi")\
#	    	.config("spark.executor.memory", "2g")\
#	    	.config("spark.driver.memory", "2g")\
#		.getOrCreate()

# Simple local Spark session with default settings
	spark = SparkSession\
		.builder\
		.appName("SIP_task2_PythonPi")\
		.getOrCreate()

	partitions = 2
	n = 100000 * partitions
# Get Spark context
	sc = spark.sparkContext
# Simple PI calculations - create RDD and apply Map/Reduce operations
	count = sc.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
	result = 4.0 * count / n

	st = 'Pi is roughly ' + str(4.0 * count / n) + ' : '
	process_sender.send(st)

	while True:
		# Create a timestamp
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime(
                        '%Y-%m-%d %H:%M:%S')

# Generate two arrays of random numbers, create RDDs and make some spark actions/transformations
		xs = np.random.random(n).astype(np.float32)
		ys = np.random.random(n).astype(np.float32)

		xsRDD = sc.parallelize(xs)
		WithIndex = xsRDD.zipWithIndex()
		xsRDDWithIndex = WithIndex.map(lambda kv : (kv[1], kv[0]))

		ysRDD = sc.parallelize(ys)
		WithIndex = ysRDD.zipWithIndex()
		ysRDDWithIndex = WithIndex.map(lambda kv : (kv[1], kv[0]))

		xysRDD = xsRDDWithIndex.join(ysRDDWithIndex)
		xys_count = xysRDD.count()

# Numba gives an error, possible Python 3.x - related bug
#		res2 = xysRDD.map(lambda x: cpu_some_trig1(x[1][0], x[1][1])
		res2 = xysRDD.map(lambda x: x[1][0] + x[1][1])

#		# Change the state w.r.t. the time, e.g. calculate either mean or variance using pyspark API
		if int(time.time())%10 < 5 :
#		if _state == 'state2' :
			# Doing something
			_state = 'Mean'
			result = res2.sum()/xys_count
		else :
			# Doing something else
			_state = 'Var'
			result = res2.variance()
		# Add current state to the heartbeat sequence
		st += ' State: '+_state + ' Result = ' + str(result) + ': Component: '
		# Sent to the socket
		process_sender.send(st)
		# Wait 1 sec
		time.sleep(1)
	spark.stop()

if __name__ == '__main__':
	run()
	
