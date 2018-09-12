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
import os
import subprocess

from ..master_client import MasterDbClient


def test_create_client_object():
    """Test creating a client object."""
    db_client = MasterDbClient()
    assert db_client is not None


def test_set_target_state():
    """Test updating target state to the db."""
    db_client = MasterDbClient()
    db_client.clear()

    initial_data = os.path.join(os.path.dirname(__file__), '../utils',
                                'set_initial_data.py')
    subprocess.call(["python3", initial_data])
    mc_event_queue = db_client.subscribe('test_update_target')
    key = 'master_controller'
    # # key = ['execution_control', 'master_controller']
    field = 'Target_state'
    value = "OFF"
    db_client.update_target_state(value)
    events = mc_event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].data['type'] == 'updated'
    state = db_client.get_value(key, field)
    assert state == 'OFF'

    # Update states of the components
    component_key = ['processing_controller', 'logging']
    for c_key in component_key:
        db_client.update_component_state(c_key, field, value)
    for test_key in component_key:
        state = db_client.get_value(test_key, field)
        assert state == 'OFF'


def test_set_sdp_state():
    """Test updating sdp state to the db """
    db_client = MasterDbClient()
    db_client.clear()
    subprocess.call(["python3", os.path.dirname(__file__), '../utils',
                     'set_initial_data.py'])
    mc_event_queue = db_client.subscribe('test_update_target')
    key = 'master_controller'
    field = 'Target_state'
    value = "OFF"
    db_client.update_target_state(value)
    events = mc_event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].data['type'] == 'updated'
    state = db_client.get_value(key, field)
    assert state == 'OFF'

    # Update states of the components
    component_key = ['processing_controller', 'logging']
    for c_key in component_key:
        db_client.update_component_state(c_key, field, value)
    for test_key in component_key:
        state = db_client.get_value(test_key, field)
        assert state == 'OFF'

    # update completed state
    sdp_field = "SDP_state"
    mc_list = db_client.get_active()
    mc_key = mc_list[0]
    assert mc_key == key
    db_client.update_sdp_state(value)
    events = mc_event_queue.get_published_events()
    assert events[-1].type == 'completed'
    assert events[0].data['type'] == 'completed'
    state = db_client.get_value(mc_key, sdp_field)
    assert state == 'OFF'
    completed_list = db_client.get_completed()
    assert len(completed_list) == 1
    assert completed_list[0] == mc_key

    # Update states of the components
    current_field = "Current_state"
    component_key = ['processing_controller', 'logging']
    for c_key in component_key:
        db_client.update_component_state(c_key, current_field, value)
    for test_key in component_key:
        state = db_client.get_value(test_key, current_field)
        assert state == 'OFF'


def test_get_state():
    """Test method to check the correct state is returned."""
    db_client = MasterDbClient()
    db_client.clear()

    initial_data = os.path.join(os.path.dirname(__file__), '../utils',
                                'set_initial_data.py')
    subprocess.call(["python3", initial_data])
    keys = ['master_controller', 'processing_controller']
    field = 'Target_state'
    for key in keys:
        state = db_client.get_value(key, field)
        assert state == "ON"
    state = db_client.get_value('logging', 'Current_state')
    assert state == "ON"
