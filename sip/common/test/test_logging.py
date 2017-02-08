# coding: utf-8
"""Tests of SIP logging API.

Run with:
    python3 -m unittest common.test.test_logging

.. moduleauthor:: Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>
"""
import os
import sys
import time

import logging.handlers
import unittest

# FIXME(BM) Horrible hack which will be fixed by SIP code restructuring.
sys.path.append('common')
sys.path.append(os.path.join('common', 'sip_common'))
os.environ['SIP_HOSTNAME'] = os.uname()[1]

from sip.common import logging_aggregator
from sip.common import logging_api
from sip.common import logging_handlers


class MyFilter(logging.Filter):
    """Test logging filter.

    Note can also use ZMQ filters at a lower level for ZMQ subscribers.
    """

    def filter(self, record):
        """Hide log records where the message starting with 'hi'"""
        return not record.getMessage().startswith('hi')


class TestLogging(unittest.TestCase):
    """Test of SIP logging API"""

    @classmethod
    def setUpClass(cls):
        """Set up a Log aggregator to receive messages via ZMQ"""
        cls.sub_thread = logging_aggregator.LogAggregator()
        cls.sub_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.sub_thread.stop()
        while cls.sub_thread.isAlive():
            cls.sub_thread.join(timeout=1e-6)

    def test_zmq(self):
        l = logging_api.SipLogger('sip.logging.test2', level='DEBUG')
        l.addHandler(logging_handlers.ZmqLogHandler.to('test:test2'))
        # l.addFilter(MyFilter())
        time.sleep(1e-2)  # This sleep is needed otherwise messages are lost
        l.info('hi there, {}'.format('how are you?'))
        l.debug('hello')
        # Wait for messages to be received.
        time.sleep(0.1)
