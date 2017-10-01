# -*- coding: utf-8 -*-
""" Tests of the CSP visibility emulator.

Run with:
    python3 -m unittest discover -f -v -p test_visibility_sender.py
"""
import unittest

import numpy as np

try:
    from sip.emulators.csp_visibility_sender.heap_streamer import HeapStreamer
except ImportError:
    raise unittest.SkipTest('Skipping test as spead module not found.')


class TestHeapSimulator:
    """ Mock heap simulator class.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, config):
        self.config = config

    def send_heaps(self, streamer: HeapStreamer):
        """ Sends spead heaps using the specified HeapStreamer class.

        Args:
            streamer (HeapStreamer): Heap streamer object used to send heaps
        """
        # print(streamer.__dict__, file=sys.stderr)
        streamer.start()
        num_times = self.config['observation']['time']['num_times']
        # num_streams = len(self.config['sender_node']['streams'])
        num_streams = self.config['sender_node']['stream_num_channels']

        # Time loop
        for i in range(num_times):
            for j in range(num_streams):
                streamer.payload['complex_visibility'] = \
                    np.ones(streamer._frame_shape) * i
                streamer.payload['timestamp_utc'] = [(i, i+3)]
                streamer.send_heap(heap_index=i, stream_id=j)

        streamer.end()

        # print(streamer.__dict__, file=sys.stderr)
        # streamer.log_stats()


class Test1(unittest.TestCase):
    """ FIXME(BM) Description
    """

    @staticmethod
    def _config1():
        config = {
            "observation": {
                "frequency": dict(num_channels=4),
                "time": dict(num_times=10),
                "telescope": dict(num_baselines=100000)
            },
            "sender_node": {
                "stream_num_channels": 1,
                "streams": [dict(port=8001, host="127.0.0.1")]
            }
        }
        frame_shape = (1, 1, config["sender_node"]["stream_num_channels"],
                       config["observation"]["telescope"]["num_baselines"], 4)
        return config, frame_shape

    def test_get_config_r(self):
        """ Test method to get a configuration setting
        """
        settings_ = dict(a=2, b=3, c=dict(i=5))
        get_config = HeapStreamer._get_config_r
        self.assertEqual(get_config(settings_, 'a', 5), 2)
        self.assertEqual(get_config(settings_, 'z', 5), 5)
        self.assertEqual(get_config(settings_, 'q'), None)
        self.assertEqual(get_config(settings_, ['c', 'i']), 5)
        self.assertEqual(get_config(settings_, ['c', 'j'], 'hi'), 'hi')
        self.assertEqual(get_config(settings_, ['xx', 'yy'], 99), 99)

    def test_send_spead_heaps(self):
        """ Tests sending spead heaps
        """
        config, frame_shape = self._config1()

        # Create the streamer
        streamer = HeapStreamer(config, frame_shape)

        # Check
        self.assertEqual(len(streamer._streams), 1)
        self.assertEqual(len(streamer._streams[0][1].items()), 8)
        self.assertEqual(streamer._streams[0][1]['complex_visibility'].shape,
                         frame_shape)

        sim = TestHeapSimulator(config)
        # sim.sim_blocks(config['observation']['time']['num_times'])
        sim.send_heaps(streamer)
