# -*- coding: utf-8 -*-
"""Unit tests for the Master Controller REST variant.

- http://flask.pocoo.org/docs/0.12/testing/
"""
import unittest
import json
import os

os.environ['UNIT_TESTING'] = 'yes'

from app.app import APP

class MasterControllerTests(unittest.TestCase):
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

    def test_get_state_successful(self):
        """Test of successfully returning the SDP state."""
        states = ['OFF', 'INIT', 'STANDBY', 'ON', 'DISABLE', 'FAULT', 'ALARM',
                  'UNKNOWN']
        response = self.app.get('/state')
        self.assertEqual(response.mimetype,
                         'application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data().decode('utf-8'))
        self.assertTrue(data['state'] in states)

    def test_put_state_successful(self):
        """Test of successfully setting the SDP state."""
        pass
        response = self.app.put('/state', data={'state': 'STANDBY'})
        self.assertEqual(response.mimetype,
                         'application/json')
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/state')
        data = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(data['state'], 'STANDBY' )

    def test_put_state_failure(self):
        """Test of failing to set the SDP state."""
        pass
        response = self.app.put('/state', data={'state': 'BAD'})
        self.assertEqual(response.mimetype,
                         'application/json')
        self.assertEqual(response.status_code, 400)
