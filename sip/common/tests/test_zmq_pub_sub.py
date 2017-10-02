# -*- coding: utf-8 -*-
""" Unit tests for ZMQ pub / sub interface.

Run with:
    $ python3 -m unittest -f -v sip.common.tests.zmq_pub_sub_test

.. moduleauthor:: Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>
"""
import sys
import threading
import time
import unittest

import zmq


def recv_messages(zmq_subscriber, timeout_count, message_count):
    """Test utility function.

    Subscriber thread that receives and counts ZMQ messages.

    Args:
        zmq_subscriber (zmq.Socket): ZMQ subscriber socket.
        timeout_count (int): No. of failed receives until exit.
        message_count (int): No. of messages expected to be received.

    Returns:
        (int) Number of messages received.
    """
    # pylint: disable=E1101
    fails = 0  # No. of receives that didn't return a message.
    receive_count = 0  # Total number of messages received.
    while fails < timeout_count:
        try:
            _ = zmq_subscriber.recv_string(flags=zmq.NOBLOCK)
            fails = 0
            receive_count += 1
            if receive_count == message_count:
                break
        except zmq.ZMQError as error:
            if error.errno == zmq.EAGAIN:
                pass
            else:
                raise
        fails += 1
        time.sleep(1e-6)
    return receive_count


class TestPubSocketBind(unittest.TestCase):
    """ Mode1: Subscriber connects and the publisher binds to the socket.

    This method means that each subscriber must know the hostname (IP)
    of each publisher, publishers do not need to know the hostname of the
    subscriber.

    This has some advantages for writing publishers but means that the
    subscriber must know all of the hostnames of the publishers.
    """

    @classmethod
    def setUpClass(cls):
        """ Set up subscriber in a thread.
        """
        # pylint: disable=E1101
        cls.sub_host = 'localhost'
        cls.sub_port = 6666
        cls.send_count = 100

        context = zmq.Context()
        cls.sub = context.socket(zmq.SUB)
        try:
            cls.sub.connect('tcp://{}:{}'.format(cls.sub_host, cls.sub_port))
        except zmq.ZMQError as error:
            print(error)
        cls.sub.setsockopt_string(zmq.SUBSCRIBE, '')
        cls.sub_context = context
        time.sleep(1.0)

        def watcher(zmq_subscriber, message_count, timeout=5000):
            """Thread run method to monitor subscription socket"""
            receive_count = recv_messages(zmq_subscriber, timeout,
                                          message_count)
            assert receive_count == message_count, \
                'Received {} / {} messages'.format(receive_count,
                                                   message_count)

        cls.watcher = threading.Thread(target=watcher,
                                       args=(cls.sub, cls.send_count))
        cls.watcher.start()

    @classmethod
    def tearDownClass(cls):
        """ Destroy the test class.
        """
        cls.sub.disconnect('tcp://{}:{}'.format(cls.sub_host, cls.sub_port))
        cls.sub.close()
        cls.sub_context.term()

    def test_pub(self):
        """Publish log messages. bind() to PUB socket."""
        # pylint: disable=E1101
        context = zmq.Context()
        pub = context.socket(zmq.PUB)
        try:
            pub.bind('tcp://*:{}'.format(self.sub_port))
        except zmq.ZMQError as error:
            print(error)
        time.sleep(0.1)

        send_count = self.send_count
        for i in range(send_count):
            pub.send_string('hi there {}'.format(i))
            time.sleep(1e-5)
        sys.stdout.flush()

        # Wait for the watcher thread to exit.
        while self.watcher.isAlive():
            self.watcher.join(timeout=1e-5)

        pub.close()
        context.term()


class TestSubSocketBind(unittest.TestCase):
    """ Mode2: Subscriber binds and the publisher connects to the socket.

    This is the current model for the SIP logger.

    This method means that each log publisher must know the hostname (IP)
    of the subscriber, but the subscriber only needs to know the logging
    port.
    """

    @classmethod
    def setUpClass(cls):
        """Set up subscriber in a thread."""
        # pylint: disable=E1101
        cls.sub_host = 'localhost'
        cls.sub_port = 6666
        cls.send_count = 100

        # Create subscriber socket.
        context = zmq.Context()
        subscriber = context.socket(zmq.SUB)
        try:
            subscriber.bind('tcp://*:{}'.format(cls.sub_port))
        except zmq.ZMQError as error:
            print('ERROR:', error)
        subscriber.setsockopt_string(zmq.SUBSCRIBE, '')
        cls.sub = subscriber
        cls.sub_context = context
        time.sleep(0.1)

        def watcher(zmq_subscriber, message_count, timeout=5000):
            """Thread run method to monitor subscription socket"""
            receive_count = recv_messages(zmq_subscriber, timeout,
                                          message_count)
            assert receive_count == message_count, \
                'Received {} / {} messages'.format(receive_count,
                                                   message_count)

        cls.watcher = threading.Thread(target=watcher,
                                       args=(subscriber, cls.send_count))
        cls.watcher.start()

    @classmethod
    def tearDownClass(cls):
        """ Destroy the test class
        """
        cls.sub.unbind('tcp://0.0.0.0:{}'.format(cls.sub_port))
        cls.sub.close()
        cls.sub_context.term()

    def test_pub(self):
        """Publish log messages. connect() to PUB socket."""
        # pylint: disable=E1101
        context = zmq.Context()
        pub = context.socket(zmq.PUB)
        try:
            _address = 'tcp://{}:{}'.format(self.sub_host, self.sub_port)
            pub.connect(_address)
        except zmq.ZMQError as error:
            print('ERROR:', error)
        time.sleep(0.1)

        send_count = self.send_count
        for i in range(send_count):
            pub.send_string('hi there {}'.format(i))
            time.sleep(1e-5)

        # Wait for the watcher thread to exit
        while self.watcher.isAlive():
            self.watcher.join(timeout=1e-5)

        pub.close()
        context.term()
