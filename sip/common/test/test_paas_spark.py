""" Test Spark as a Service

.. moduleauthor:: Arjen Tamerus <at748@cam.ac.uk>
"""

import unittest
import requests
import time

from sip.common.spark_paas import SparkPaaS, SparkTaskDescriptor
from sip.common.paas import TaskStatus

paas = SparkPaaS()


@unittest.skip("Need to add skip condition based on spark found.")
class TestSparkPaaS(unittest.TestCase):

    def setUp(self):
        master_url = "http://{}:{}".format(
                paas.spark_master['url'],
                paas.spark_master['master_port']
            )
        try:
            req = requests.get(master_url)
            if not req.ok:
                    self.fail(
                        "No 200 response from Spark Master @[{}]".format(master_url)
                    )
        except Exception:
            self.fail("Cannot connect to Spark Master @ [{}]".format(master_url))

    def test1TaskSubmit(self):
        cfg = {'jarfile': "spark_sleep.py", 'jarpath': "sip/common/test", "spark_args": ""}
        task = paas.run_service("test_spark", "test_spark", None, cfg)
        self.assertIsInstance(paas.find_task("test_spark"), SparkTaskDescriptor)
        self.assertEqual(task.status(),TaskStatus.RUNNING)
        time.sleep(5)
        self.assertEqual(task.status(),TaskStatus.EXITED)

    def test2TaskDestroy(self):
        cfg = {'jarfile': "spark_sleep.py", 'jarpath': "sip/common/test", "spark_args": ""}
        task = paas.run_service("test_spark", "test_spark", None, cfg)
        self.assertEqual(task.status(),TaskStatus.RUNNING)
        paas.delete_task("test_spark")
        # Killing Spark jobs is not supported in YARN
        if paas.spark_mode() != "YARN":
            self.assertEqual(task.status(),TaskStatus.EXITED)
        
        self.assertIsNone(paas.find_task("test_spark"))
