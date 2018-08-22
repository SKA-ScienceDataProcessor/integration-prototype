# -*- coding: utf-8 -*-
"""Tests of the Config db client API Master Controller resources.

For instructions of how to run these tests see the README.md file in the
`sip/configuration_db/redis` folder.

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
import datetime
import pytest
import jsonschema

from ..master_client import MasterDbClient


def test_create_client_object():
    """Test creating a client object."""
    db_client = MasterDbClient()
    assert db_client is not None


def test_set_state():
    """TODO test description."""
    db_client = MasterDbClient()
    db_client.clear()

    name = ['execution_control', 'master_controller']
    field = 'Target_state'
    value = "OFF"
    db_client.update_value(name, field, value)
    state =  db_client.get_value(name, field)
    assert state == "OFF"


def test_get_state():
    """TODO test description."""
    db_client = MasterDbClient()
    db_client.clear()

    name = ['execution_control', 'master_controller']
    field = 'SDP_state'
    state = db_client.get_value(name, field)
    assert state == "ON"


def test_get_all_states():
    """TODO test description."""
    db_client = MasterDbClient()
    db_client.clear()

    name = ['execution_control', 'master_controller']
    values = db_client.get_all_value(name)
    # TODO
    # CHECK WHAT IT DOES
    # assertNotEqual(values, None)


def test_path():
    """TODO test description."""
    db_client = MasterDbClient()
    db_client.clear()

    service_list_name = ['execution_control', 'master_controller',
                         'service_list']
    element = db_client.get_service_from_list(service_list_name, 0)
    # log.debug(element['name'])
    field = 'state'
    value = "stopped"
    db_client.update_service(element['name'], field, value)
    service_name = ['sdp_services', 'data_queue']
    service = db_client.get_value(service_name, field)

    # TODO
    # self.assertEqual(service, 'stopped')


# DON'T REQUIRE THIS ANYMORE  NO LIST IN MASTER CONTROLLER ATM
# def test_add_to_list():
#     """TODO test description."""
#     db_client = MasterDbClient()
#     db_client.clear()
#
#     service_list_name = ['execution_control', 'master_controller',
#                          'service_list']
#     service = {'name': 'sdp_services.data_queue', 'enabled': 'False'}
#     db_client.add_service_to_list(service_list_name, service)
#     element = db_client.get_service_from_list(service_list_name, 0)
#
#     # TODO
#     # self.assertEqual(element['name'], 'sdp_services.data_queue')
#     # Value in string
#     # self.assertEqual(element['enabled'], 'False')

# DON'T REQUIRE FUNCTION
# def test_length():
#     db_client = MasterDbClient()
#     db_client.clear()
#
#     """TODO test description."""
#     service_list_name = ['execution_control', 'master_controller',
#                          'service_list']
#     # TODO
#     # self.assertEqual(db_client.get_service_list_length(service_list_name), 6)

# NOT REQUIRED
# def test_list_access():
#     """TODO test description."""
#     db_client = MasterDbClient()
#     db_client.clear()
#
#     service_list_name = ['execution_control', 'master_controller',
#                          'service_list']
#     element = db_client.get_service_from_list(service_list_name, 0)
#
#     #TODO
#     # self.assertEqual(element['name'], 'sdp_services.data_queue')
#     element = db_client.get_service_from_list(service_list_name, 1)
#
#     #TODO
#     # self.assertEqual(element['name'], 'sdp_services.local_sky_model')

# def test_boolean():
#     """TODO test description."""
#     db_client = MasterDbClient()
#     db_client.clear()
#
#     service_list_name = ['execution_control', 'master_controller',
#                          'service_list']
#     element = db_client.get_service_from_list_bool(service_list_name, 0)
#
#     #TODO
#     # self.assertTrue(element['enabled'], False)