# -*- coding: utf-8 -*-
"""Unit tests for the Master Controller REST variant.

- http://flask.pocoo.org/docs/0.12/testing/
"""
import unittest
import json

from app.app import APP


class ProcessingControllerInterfaceTests(unittest.TestCase):
    """Tests of the Master Controller"""

    def setUp(self):
        """Executed prior to each test."""
        APP.config['TESTING'] = True
        APP.config['DEBUG'] = False
        APP.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        self.app = APP.test_client()
        self.assertEqual(APP.debug, False)

    def tearDown(self):
        """Executed after each test."""
        pass

    def test_get_scheduling_block_list(self):
        """Test GET request of scheduling block list"""
        pass

    def test_post_invalid_scheduling_block(self):
        """Test request of a new scheduling block."""
        # response = self.app.get('/state')
        # self.assertEqual(response.mimetype,
        #                  'application/json')
        # self.assertEqual(response.status_code, 200)
        # data = json.loads(response.get_data())
        # self.assertTrue(data['state'] in states)

    def test_post_successful_scheduling_block(self):
        """Test request of a new scheduling block."""
        pass

    def test_delete_scheduling_block(self):
        """Test delete of a scheduling block"""
        pass

