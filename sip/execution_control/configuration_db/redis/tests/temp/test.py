# -*- coding: utf-8 -*-
"""Unit tests for the configuration database mock API

- http://flask.pocoo.org/docs/0.12/testing/
"""
import unittest

from config_db import config_db

class DbClientTests(unittest.TestCase):
    """Tests of the configuration database API."""

    def setUp(self):
        """Executed prior to each test."""
        self.h = config_db();
        self.h.db_ = {
                       'execution_control': {
                          'master_controller': {
                             'SDP_state': "None",
                             'enabled': "False",
                             'service_list': [
                                {
                                  'name': 'sdp_services.local_sky_model',
                                  'enabled': 'True'
                                },
                                {
                                  'name': 'sdp_services.telescope_model',
                                  'enabled': 'True'
                                }
                             ]
                          }
                       },
                       'sdp_services': {
                         'local_sky_model': {
                           'state': 'running'
                         }
                       }
                     }

    def tearDown(self):
        """Executed after each test."""
        pass

    def testGetValue(self):
        SDP_state_h = self.h.handle(['execution_control', 'master_controller',
                'SDP_state'])
        SDP_state_v = SDP_state_h.get_eval()
        self.assertEqual(SDP_state_v, None)

    def testSetValue(self):
        SDP_state_h = self.h.handle(['execution_control', 'master_controller',
                'SDP_state'])
        SDP_state_h.set("running")
        SDP_state_v = SDP_state_h.get()
        self.assertEqual(SDP_state_v, "running")

    def testBoolean(self):
        enabled_h = self.h.handle(['execution_control', 'master_controller',
                'enabled'])
        self.assertEqual(enabled_h.get_eval(), False)
        enabled_h.set(True)
        self.assertEqual(enabled_h.get_eval(), True)

    def testLength(self):
        list_h = self.h.handle(['execution_control', 'master_controller'])
        self.assertEqual(list_h.length(), 0)
        list_h = list_h.handle(['service_list'])
        self.assertEqual(list_h.length(), 2)

    def testListAccess(self):
        list_h = self.h.handle(['execution_control', 'master_controller',
                'service_list'])
        element_h = list_h.element_handle(0)
        self.assertEqual(element_h.handle(['name']).get(),
                'sdp_services.local_sky_model')
        element_h = list_h.element_handle(1)
        self.assertEqual(element_h.handle(['name']).get(),
                'sdp_services.telescope_model')

    def testAddList(self):
        list_h = self.h.handle(['execution_control', 'master_controller',
                'service_list'])
        dict = {
                  'name': 'sdp_services.data_queue',
                  'enabled': 'False'
               }
        list_h.add_element(dict)
        element_h = list_h.element_handle(2)
        self.assertEqual(element_h.handle(['name']).get(),
                'sdp_services.data_queue')
        self.assertEqual(element_h.handle(['enabled']).get_eval(), False)

    def testPath(self):
        path = self.h.handle(['execution_control', 'master_controller',
                'service_list']).element_handle(0).handle(['name']).get_path()
        service_h = self.h.handle(path)
        self.assertEqual(service_h.handle(['state']).get(), 'running')

