# coding: utf-8
"""Module providing functions for the aggregation and display of
log messages sent by other SIP modules. SIP logging uses a ZMQ log handler
(defined in the sip_common/logging_handlers.py module) to publish messages
using a PUB/SUB pattern. The classes and functions here provide SIP with
a ZMQ aware subscriber which can be used to aggregate and display SIP log
messages.

.. moduleauthor:: Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>
"""
import json
import logging
import logging.handlers
import threading

import zmq
from logging_handlers import StdoutLogHandler


class LogAggregator(threading.Thread):
    """Class to aggregate log messages from SIP ZMQ publishers.

    SIP ZMQ publishers send a JSONified python logging LogRecord.
    This class converts the JSON received on the ZMQ SUB socket to a Python
    LogRecord so it can be displayed using the standard Python logging API.

    Eventually it is envisaged that this class can be extended to support
    the addition of user specified ZMQ and logging filters, as well as
    different logging adapters. Currently, log messages are simply
    written to stdout using a logging.StreamHandler, defined inside the run
    method.

    Notes:
        - Extend the class to support user specified logging handlers
        - Extend the class to support user specified ZMQ and logging
          filters.
        - Log topics are currently not used but provide a hook for future
          updates to the logging, mainly with filters in mind.
    """

    def __init__(self, port=logging.handlers.DEFAULT_TCP_LOGGING_PORT):
        """Constructor.

        Creates the ZMQ SUB socket, binds it to the specified port and
        sets the ZMQ SUB filter to accept all messages.

        Args:
            port (int): Port on which to bind to receive messages.
        """
        threading.Thread.__init__(self)
        self._stop_requested = threading.Event()
        context = zmq.Context()
        subscriber = context.socket(zmq.SUB)
        try:
            subscriber.bind('tcp://*:{}'.format(port))
        except zmq.ZMQError as e:
            print('ERROR:', e)
        subscriber.setsockopt_string(zmq.SUBSCRIBE, '')
        self._subscriber = subscriber

    def stop(self):
        """Stop the thread."""
        self._stop_requested.set()

    def run(self):
        """Run loop.

        Receives log messages from connected publishers and logs them via
        a python logging interface.
        """
        log = logging.getLogger('sip.logging')
        log.setLevel('DEBUG')
        log.addHandler(StdoutLogHandler())

        while not self._stop_requested.is_set():
            try:
                topic, values = self._subscriber.recv_multipart(zmq.NOBLOCK)
                values = json.loads(values.decode('utf-8'))
                record = logging.makeLogRecord(values)
                log.handle(record)
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    pass
                else:
                    raise  # Re-raise the exception
            # Note: the value of the timeout might have to be reviewed
            # if it blocks the CPU too much.
            self._stop_requested.wait(timeout=1e-6)
