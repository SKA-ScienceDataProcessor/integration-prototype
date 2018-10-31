# -*- coding: utf-8 -*-
"""Tests of the SDP States API."""
from ..config_db_redis import ConfigDb
from ..sdp_state import SDPState


DB = ConfigDb()


def test_create_sdp_state_object():
    """Test creating SDP state data object."""
    DB.flush_db()
    sdp_state = SDPState()
    assert sdp_state is not None


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
