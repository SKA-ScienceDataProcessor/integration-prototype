""" Test Spark as a Service

.. moduleauthor:: Arjen Tamerus <at748@cam.ac.uk>
"""

import time
import unittest

import requests

from sip.common.paas import TaskStatus
from sip.common.spark_paas import SparkPaaS, SparkTaskDescriptor


class TestSparkPaaS(unittest.TestCase):
    """ Tests of the Spark PaaS interface."""

    @classmethod
    def setUpClass(cls):
        """ Set up test fixture.

        Skip the tests if it is not possible to connect to the Spark Master.
        """
        paas = SparkPaaS()
        try:
            master_url = "http://{}:{}".format(
                paas.spark_master['url'], paas.spark_master['master_port'])
            req = requests.get(master_url)
            if not req.ok:
                raise unittest.SkipTest('No 200 response from Spark Master '
                                        '@[{}], Skipping tests.'.
                                        format(master_url))
        except requests.exceptions.RequestException:
            print('Exception thrown..')
            raise unittest.SkipTest("Cannot connect to Spark Master @ [{}]. "
                                    "Skipping tests.". format(master_url))
        cls.paas = paas

    def test1_task_submit(self):
        """ Test submitting a Spark task.
        """
        cfg = {
            'jarfile': "mock_spark_task.py",
            'jarpath': "sip/common/tests",
            "spark_args": ""
        }
        task = self.paas.run_service("test_spark", "test_spark", None, cfg)
        self.assertIsInstance(self.paas.find_task("test_spark"),
                              SparkTaskDescriptor)
        self.assertEqual(task.status(), TaskStatus.RUNNING)
        time.sleep(5)
        self.assertEqual(task.status(), TaskStatus.EXITED)

    def test2_task_destroy(self):
        """ Tests destroying a Spark task.
        """
        cfg = {
            'jarfile': "mock_spark_task.py",
            'jarpath': "sip/common/tests",
            "spark_args": ""
        }
        task = self.paas.run_service("test_spark", "test_spark", None, cfg)
        self.assertEqual(task.status(), TaskStatus.RUNNING)
        self.paas.delete_task("test_spark")
        # Killing Spark jobs is not supported in YARN
        if self.paas.spark_mode() != "YARN":
            self.assertEqual(task.status(), TaskStatus.EXITED)

        self.assertIsNone(self.paas.find_task("test_spark"))
