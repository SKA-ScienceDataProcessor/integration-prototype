# -*- coding: utf-8 -*-
"""Unit tests for the controller client
# A sample schema, like what we'd get from json.load()
schema = {
    "type": "object",
    "properties": {
        "price": {"type": "number"},
        "name": {"type": "string"},
    },
}

# if no exception is raised by validate(), the instance is valid.
validate({'name': "myname", "price": 34.99}, schema)
"""

import unittest
import logging
import sys
from controller_client import controllerClient

class DbClientTests(unittest.TestCase):
    def setUp(self):
        self._db = controllerClient()
        self._log = logging.getLogger("DbClientTests.testPath")

    def tearDown(self):
        """Executed after each test."""
        pass

    def testGetSchema(self):
        pass

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger("DbClientTests.testPath").setLevel(logging.DEBUG)
    unittest.main()