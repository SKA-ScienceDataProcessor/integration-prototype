# -*- coding: utf-8 -*-
"""Tests of the SDP States API.

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

FIXME(BM) remove subprocess calls --- \
          import init function directly and call method!
"""
import os
import subprocess

from ..config_db_redis import ConfigDb
from ..sdp_state import SDPState


DB = ConfigDb()


def test_create_states_object():
    """Test creating SDP states data object."""
    DB.flush_db()
    sdp_states = SDPState()
    assert sdp_states is not None
    # TODO(BM) initilise default states into database!?


# def test_set_target_state():
#     """Test updating target state to the db."""
#     sdp_state = SDPState()
#     # TODO(BM) Check that this only clears the states not the PB/SBI/subarray
#     # data!
#     sdp_state.clear()
#
#     initial_data = os.path.join(os.path.dirname(__file__), '../utils',
#                                 'initialise_database.py')
#     subprocess.call(["python3", initial_data])
#     mc_event_queue = sdp_state.subscribe('test_update_target')
#     key = 'master_controller'
#     state_field = 'Target_state'
#     value = "OFF"
#     sdp_state.set_target_state(state_field, value)
#     events = mc_event_queue.get_published_events()
#     assert len(events) == 1
#     assert events[0].data['type'] == 'updated'
#     state = sdp_state.get_value(key, state_field)
#     assert state == 'OFF'
#
#     # Update states of the components
#     component_key = ['processing_controller', 'logging']
#     for c_key in component_key:
#         sdp_state.set_service_state(c_key, state_field, value)
#     for test_key in component_key:
#         state = sdp_state.get_value(test_key, state_field)
#         assert state == 'OFF'


# def test_set_sdp_state():
#     """Test updating sdp state to the db """
#     sdp_states = SDPStates()
#     sdp_states.clear()
#
#     subprocess.call(["python3", os.path.dirname(__file__), '../utils',
#                      'initialise_database.py'])
#     mc_event_queue = sdp_states.subscribe('test_update_target')
#     key = 'master_controller'
#     state_field = 'Target_state'
#     value = "OFF"
#     sdp_states.update_target_state(state_field, value)
#     events = mc_event_queue.get_published_events()
#     assert len(events) == 1
#     assert events[0].data['type'] == 'updated'
#     state = sdp_states.get_value(key, state_field)
#     assert state == 'OFF'
#
#     # Update states of the components
#     component_key = ['processing_controller', 'logging']
#     for c_key in component_key:
#         sdp_states.update_component_state(c_key, state_field, value)
#     for test_key in component_key:
#         state = sdp_states.get_value(test_key, state_field)
#         assert state == 'OFF'
#
#     # update completed state
#     sdp_field = "SDP_state"
#     mc_list = sdp_states.get_active()
#     mc_key = mc_list[0]
#     assert mc_key == key
#     sdp_states.update_sdp_state(sdp_field, value)
#     events = mc_event_queue.get_published_events()
#     assert events[-1].type == 'completed'
#     assert events[0].data['type'] == 'completed'
#     state = sdp_states.get_value(mc_key, sdp_field)
#     assert state == 'OFF'
#     completed_list = sdp_states.get_completed()
#     assert len(completed_list) == 1
#     assert completed_list[0] == mc_key
#
#     # Update states of the components
#     current_field = "Current_state"
#     component_key = ['processing_controller', 'logging']
#     for c_key in component_key:
#         sdp_states.update_component_state(c_key, current_field, value)
#     for test_key in component_key:
#         state = sdp_states.get_value(test_key, current_field)
#         assert state == 'OFF'
#
#
# def test_get_state():
#     """Test method to check the correct state is returned."""
#     sdp_states = SDPStates()
#     sdp_states.clear()
#
#     initial_data = os.path.join(os.path.dirname(__file__), '../utils',
#                                 'initialise_database.py')
#     subprocess.call(["python3", initial_data])
#     keys = ['master_controller', 'processing_controller']
#     field = 'Target_state'
#     for key in keys:
#         state = sdp_states.get_value(key, field)
#         assert state == "ON"
#     state = sdp_states.get_value('logging', 'Current_state')
#     assert state == "ON"
