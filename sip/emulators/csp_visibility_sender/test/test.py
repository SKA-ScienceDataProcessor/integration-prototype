# -*- coding: utf-8 -*-
"""Unittest for the csp_visibility_sender.

Run with:
python -m unittest emulators.csp_visibility_sender.test.test

or to run just 1 test:
python -m unittest emulators.csp_visibility_sender.test.test.Test1.test_get_config_r
"""
import sys

import logging
import numpy as np
import unittest

from sip.emulators.csp_visibility_sender import HeapStreamer


class TestHeapSimulator:

    def __init__(self, config, log):
        self.config = config
        self.log = log

    def send_heaps(self, streamer: HeapStreamer):
        self.streamer.start()
        num_times = 1
        num_streams = 1

        # Time loop
        for i in range(num_times):
            for j in range(num_streams):
                self.streamer.payload['complex_visibility'] = \
                    np.ones(self.streamer.frame_shape) * i
                self.streamer.payload['timestamp_utc'] = [(i, i+3)]
                self.streamer.send_heap(heap_index=i, stream_id=j)

        self.streamer.end()
        self.streamer.log_stats()


class Test1(unittest.TestCase):

    @staticmethod
    def _create_log():
        log = logging.getLogger(__file__)
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s: %(message)s',
                                      '%Y/%m/%d-%H:%M:%S')
        ch.setFormatter(formatter)
        log.addHandler(ch)
        return log

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
        settings_ = dict(a=2, b=3, c=dict(i=5))
        get_config = HeapStreamer._get_config_r
        self.assertEqual(get_config(settings_, 'a', 5), 2)
        self.assertEqual(get_config(settings_, 'z', 5), 5)
        self.assertEqual(get_config(settings_, 'q'), None)
        self.assertEqual(get_config(settings_, ['c', 'i']), 5)
        self.assertEqual(get_config(settings_, ['c', 'j'], 'hi'), 'hi')
        self.assertEqual(get_config(settings_, ['xx', 'yy'], 99), 99)

    def test1(self):
        # Create the log
        log = self._create_log()

        config, frame_shape = self._config1()

        # Create the streamer
        streamer = HeapStreamer(config, frame_shape, log)

        # Check
        self.assertEqual(len(streamer._streams), 1)
        self.assertEqual(len(streamer._streams[0][1].items()), 8)
        self.assertEqual(streamer._streams[0][1]['complex_visibility'].shape,
                         frame_shape)

        sim = TestHeapSimulator(streamer, log)
        sim.sim_blocks(config['observation']['time']['num_times'])


if __name__ == '__main__':
    unittest.main()
