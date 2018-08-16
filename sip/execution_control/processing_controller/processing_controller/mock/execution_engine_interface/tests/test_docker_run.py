# -*- coding: utf-8 -*-
"""Unittests of the docker run interface

Run with:

python3 -m unittest tests.test_docker_run
"""

import time
import unittest
import logging
import json

from ..docker_run import RunDockerContainer


class TestDockerRun(unittest.TestCase):

    def test_run(self):
        LOG = logging.getLogger('sip')
        LOG.setLevel(logging.DEBUG)
        LOG.addHandler(logging.StreamHandler())

        docker = RunDockerContainer()
        docker.run(image='skasip/mock_task_vis_receive_01',
                   command='{}')
        time.sleep(1)
        # docker.wait()
        info = docker.info()
        print(json.dumps(info, indent=2))
        # time.sleep(1)
        # docker.kill()


if __name__ == '__main__':
    unittest.main()
