# -*- coding: utf-8 -*-
"""Unit tests for the configuration database mock API
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

import numpy as np
import unittest
from app.config_api import ConfigDB

class DbClientTests(unittest.TestCase):
    def setup(self):
        self._db = ConfigDB()

    def tearDown(self):
        """Executed after each test."""
        pass

    def testGetSDPState(self):

        key = ['execution_control', 'master_controller']
        field = 'SDP_state'
        value = self._db.get_state(key, field)
        self.assertEqual(value, 'on')


if __name__ == '__main__':
    unittest.main()