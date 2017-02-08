# coding: utf-8
"""Module providing functions for the aggregation and display of
log messages sent by other SIP modules. SIP logging uses a ZMQ log handler
(defined in the sip_common/logging_handlers.py module) to publish messages
using a PUB/SUB pattern. The classes and functions here provide SIP with
a ZMQ aware subscriber which can be used to aggregate and display SIP log
messages.

.. moduleauthor:: Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>
"""
import os

import json
import logging
import logging.config
import logging.handlers
import os
import threading

import numpy as np
import zmq


class OriginFilter(logging.Filter):
    """Origin Filter.

    Filters LogRecord origins according to a minimal match with the pattern:
        module.function:lineno

    The filter is either inclusive or exclusive according to the parameter
    exclude passed to the constructor.
    """

    def __init__(self, origin=None, exclude=True):
        """
        Constructor.

        Args:
            origin (list): List of origin strings to match against.
            exclude (bool): If true, exclude messages from the specified origins
                            If false, include messages from the specified origins
        """
        self.origin = origin
        if isinstance(self.origin, str):
            self.origin = list([self.origin])
        self.exclude = exclude

    def filter(self, record: logging.LogRecord):
        """Filter log messages."""
        if self.origin is None:
            return True
        for _filter in self.origin:
            if record.origin.startswith(_filter):
                return False if self.exclude else True
        return True if self.exclude else False


class MessageFilter(logging.Filter):
    """Message filter"""

    def __init__(self, messages=None, exclude=True):
        """."""
        self.message_filter = messages
        if isinstance(self.message_filter, str):
            self.message_filter = list([self.message_filter])
        self.exclude = exclude

    def filter(self, record: logging.LogRecord):
        """."""
        if self.message_filter is None:
            return True
        for _filter in self.message_filter:
            if _filter in record.getMessage():
                return False if self.exclude else True
        return True if self.exclude else False


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

        # Construct and configure logger object.
        config_file = os.path.join('sip', 'etc', 'default_logging.json')
        print('Loading logging configuration: {}.'.format(config_file))
        with open(config_file) as f:
            _config = json.load(f)
        logging.config.dictConfig(_config)

    def stop(self):
        """Stop the thread."""
        self._stop_requested.set()

    def run(self):
        """Run loop.

        Receives log messages from connected publishers and logs them via
        a python logging interface.
        """
        log = logging.getLogger('sip.logging_aggregator')
        fail_count = 0
        fail_count_limit = 100
        # Exponential relaxation of timeout in event loop.
        timeout = np.logspace(-6, -2, fail_count_limit)
        while not self._stop_requested.is_set():
            try:
                topic, values = self._subscriber.recv_multipart(zmq.NOBLOCK)
                str_values = values.decode('utf-8')
                try:
                    dict_values = json.loads(str_values)
                    record = logging.makeLogRecord(dict_values)
                    log.handle(record)
                    fail_count = 0
                except json.decoder.JSONDecodeError:
                    print('ERROR: Unable to convert JSON log record.')
                    raise
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    fail_count += 1
                else:
                    raise  # Re-raise the exception
            if fail_count < fail_count_limit:
                _timeout = timeout[fail_count]
            else:
                _timeout = timeout[-1]
            self._stop_requested.wait(_timeout)
