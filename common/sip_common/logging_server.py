#!/usr/bin/env python3
"""
An example of logging server which uses ZeroMQ module, based on
http://nullege.com/codes/show/src@p@y@pyzmq-14.2.0@examples@logger@zmqlogger.py/17/zmq.log.handlers.PUBHandler
using the publish-subscribe pattern, PUB/SUB.

The host name is taken from SIP_HOSTNAME environment variable,
host IP (required by subscriber bind method) is determined by
socket.gethostbyname() method.

The value of logging.handlers.DEFAULT_TCP_LOGGING_PORT is 9020 .

The server listens to the port logging.handlers.DEFAULT_TCP_LOGGING_PORT
where the different modules send their logs, and redirects them to stdout .

"""

__author__ = 'Vlad Stolyarov'


import logging, logging.handlers
import os
import sys
import time
import socket
  
import zmq
from zmq.log.handlers import PUBHandler
  
#LOG_LEVELS = (logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR, logging.CRITICAL)

sip_hostname = os.environ['SIP_HOSTNAME'] = os.uname()[1]
print('Hostname is %s' % sip_hostname)
sip_address = socket.gethostbyname(sip_hostname)
port = logging.handlers.DEFAULT_TCP_LOGGING_PORT
  
def sub_logger(port, level=logging.DEBUG):
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.bind('tcp://*:%i' % (port))
    sub.setsockopt_string(zmq.SUBSCRIBE, '')

    logging.basicConfig(level=level)
  
    while True:
        level, message = sub.recv_multipart()
        if message.endswith(str.encode("\n")):
            # trim trailing newline, which will get appended again
            message = message[:-1]
        log = getattr(logging, level.lower().decode("utf-8"))
        log(message)
  
# start the log watcher
try:
   sub_logger(port)
except KeyboardInterrupt:
   pass

