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
from ..config_db_redis import ConfigDb
from ..sdp_state import SDPState


DB = ConfigDb()


def test_create_sdp_state_object():
    """Test creating SDP states data object."""
    DB.flush_db()
    sdp_states = SDPState()
    assert sdp_states is not None


def test_set_target_state():
    """Test updating the target state."""
    DB.flush_db()
    sdp_state = SDPState()

    event_queue = sdp_state.subscribe('test_update_target')

    target_state = "OFF"
    previous_timestamp = sdp_state.get_target_state_timestamp()
    set_time = sdp_state.update_target_state(target_state)
    assert set_time >= previous_timestamp

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'sdp_state'
    assert events[0].type == 'target_state_updated'

    assert sdp_state.get_target_state() == target_state
    assert sdp_state.get_target_state_timestamp() >= set_time


def test_set_current_state():
    """Test updating the current state."""
    DB.flush_db()
    sdp_state = SDPState()
    event_queue = sdp_state.subscribe('test_update_target')

    current_state = "OFF"
    previous_timestamp = sdp_state.get_current_state_timestamp()
    set_time = sdp_state.update_current_state(current_state)
    assert set_time >= previous_timestamp

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'sdp_state'
    assert events[0].type == 'current_state_updated'

    assert sdp_state.get_current_state() == current_state
    assert sdp_state.get_current_state_timestamp() >= set_time
