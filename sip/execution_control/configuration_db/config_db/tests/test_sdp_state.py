# -*- coding: utf-8 -*-
"""Tests of the SDP States API."""
from ..config_db_redis import ConfigDb
from ..sdp_state import SDPState


def test_sdp_state_create():
    """Test creating SDP state data object."""
    ConfigDb().flush_db()
    sdp_state = SDPState()
    assert sdp_state is not None
    assert sdp_state.allowed_states == ['init', 'standby', 'on', 'off',
                                        'disable', 'alarm', 'fault']


def test_sdp_state_set_target_state():
    """Test updating the target state.

        unknown->init->standby->off

    """
    ConfigDb().flush_db()
    sdp_state = SDPState()
    event_queue = sdp_state.subscribe('test_update_target')

    assert sdp_state.current_state == 'unknown'
    assert sdp_state.target_state == 'unknown'
    sdp_state.update_current_state('init')
    assert sdp_state.current_state == 'init'
    assert sdp_state.target_state == 'unknown'

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'sdp_state'
    assert events[0].type == 'current_state_updated'
    assert events[0].data['old_state'] == 'unknown'
    assert events[0].data['new_state'] == 'init'

    target_state = "standby"
    previous_timestamp = sdp_state.target_timestamp
    set_time = sdp_state.update_target_state(target_state)
    assert sdp_state.target_state == target_state
    assert set_time >= previous_timestamp
    sdp_state.update_current_state(target_state)
    assert sdp_state.current_state == target_state

    events = event_queue.get_published_events()
    assert len(events) == 2
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'sdp_state'
    assert events[0].type == 'target_state_updated'
    assert events[0].data['old_state'] == 'unknown'
    assert events[0].data['new_state'] == 'standby'
    assert sdp_state.target_state == target_state
    assert sdp_state.target_timestamp >= set_time

    target_state = "off"
    previous_timestamp = sdp_state.target_timestamp
    set_time = sdp_state.update_target_state(target_state)
    assert sdp_state.target_state == target_state
    assert set_time >= previous_timestamp

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'sdp_state'
    assert events[0].type == 'target_state_updated'
    assert events[0].data['old_state'] == 'standby'
    assert events[0].data['new_state'] == 'off'
    assert sdp_state.target_state == target_state
    assert sdp_state.target_timestamp >= set_time


def test_sdp_state_set_current_state():
    """Test updating the current state."""
    ConfigDb().flush_db()
    sdp_state = SDPState()
    event_queue = sdp_state.subscribe('test_update_target')

    current_state = "off"
    previous_timestamp = sdp_state.current_timestamp
    set_time = sdp_state.update_current_state(current_state)
    assert set_time >= previous_timestamp

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'sdp_state'
    assert events[0].type == 'current_state_updated'

    assert sdp_state.current_state == current_state
    assert sdp_state.current_timestamp >= set_time
