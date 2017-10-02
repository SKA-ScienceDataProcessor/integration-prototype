# coding: utf-8
"""Tests of SIP logging API.

Run with:
    python3 -m unittest sip.common.tests.test_logging
or:
    python3 -m unittest discover -f -v -p test_logging.py

.. moduleauthor:: Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>
"""
import os
import time

from io import StringIO

import logging.handlers
import unittest

os.environ['SIP_HOSTNAME'] = os.uname()[1]

from sip.common import logging_aggregator
from sip.common import logging_api
from sip.common import logging_handlers


class MyFilter(logging.Filter):
    """ Test logging filter.

    Note can also use ZMQ filters at a lower level for ZMQ subscribers.
    """

    def filter(self, record):
        """ Hide log records where the message starting with 'hi'
        """
        return not record.getMessage().startswith('hi')


# @unittest.skip("Skipping as this is broken.")
class TestLogging(unittest.TestCase):
    """ Tests of SIP logging API
    """

    @classmethod
    def setUpClass(cls):
        """ Redirect log output for analysis
        """
        cls.log_output = StringIO()
        output_handler = logging.StreamHandler(cls.log_output)

        # Set up a Log aggregator to receive messages via ZMQ
        cls.sub_thread = logging_aggregator.LogAggregator()
        cls.sub_thread.start()

        # Set up logger
        cls.l = logging_api.SipLogger('sip.logging.test2', level='DEBUG')
        cls.l.addHandler(output_handler)
        cls.l.addHandler(logging_handlers.ZmqLogHandler.to('test:test2'))
        time.sleep(1e-2)  # This sleep is needed otherwise messages are lost

        # filter out log init message
        cls.log_output.seek(0)
        cls.log_output.truncate()

    @classmethod
    def tearDownClass(cls):
        """ Clean up.
        """
        cls.sub_thread.stop()
        while cls.sub_thread.isAlive():
            cls.sub_thread.join(timeout=1e-6)

    def test_zmq(self):
        """."""
        self.l.info('Formatted info message: {}'.format('how are you?'))
        # l.info('Filtered info messages should not be shown')
        self.l.debug('Debug message')
        # l.debug('Filtered debug messages should not be shown')

        # Wait for messages to be received.
        time.sleep(0.1)

        self.log_output.seek(0)
        output = self.log_output.readlines()
        self.log_output.seek(0)
        self.log_output.truncate()

        self.assertEqual(2, len(output))
        self.assertTrue("Formatted info message: how are you?" in output[0])
        self.assertTrue("Debug message" in output[1])

    def test_message_filter(self):
        """."""
        message_filter = logging_aggregator.MessageFilter('Filtered')
        self.l.addFilter(message_filter)
        self.l.info('Filtered info messages should not be shown')
        self.l.debug('Filtered debug messages should not be shown')
        time.sleep(0.1)

        self.l.removeFilter(message_filter)
        self.l.info('Filtered info messages should now be shown')
        self.l.debug('Filtered debug messages should now be shown')
        time.sleep(0.1)

        self.log_output.seek(0)
        output = self.log_output.readlines()
        self.log_output.seek(0)
        self.log_output.truncate()

        self.assertEqual(2, len(output))
        self.assertTrue("Filtered info messages should now be shown"
                        in output[0])
        self.assertTrue("Filtered debug messages should now be shown"
                        in output[1])

    def test_origin_filter(self):
        """."""
        origin_filter = logging_aggregator.OriginFilter(origin='test',
                                                        exclude=True)
        self.l.addFilter(origin_filter)
        self.l.info('This info message should not be printed')
        time.sleep(0.1)
        self.l.removeFilter(filter)

        origin_filter = logging_aggregator.OriginFilter(origin='test',
                                                        exclude=False)
        self.l.addFilter(origin_filter)
        self.l.info('This info message should be printed')
        time.sleep(0.1)
        self.l.removeFilter(filter)

        self.log_output.seek(0)
        output = self.log_output.readlines()
        self.log_output.seek(0)
        self.log_output.truncate()

        self.assertEqual(1, len(output))
        self.assertTrue("This info message should be printed" in output[0])
