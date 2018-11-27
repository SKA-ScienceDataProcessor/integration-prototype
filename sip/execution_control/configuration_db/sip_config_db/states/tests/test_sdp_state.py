# -*- coding: utf-8 -*-
"""Tests of the SDP States API."""
from .. import SDPState
from ... import ConfigDb

DB = ConfigDb()


def test_sdp_state_create():
    """Test creating SDP state data object."""
    DB.flush_db()
    sdp_state = SDPState()
    assert sdp_state is not None
    assert sdp_state.allowed_states == ['init', 'standby', 'on', 'off',
                                        'disable', 'alarm', 'fault']


def test_sdp_state_set_target_state():
    """Test updating the target state."""
    # pylint: disable=too-many-statements
    # import sip_logging
    # print()
    # sip_logging.init_logger(log_level='DEBUG')
    DB.flush_db()

    sdp_state = SDPState()
    event_queue = sdp_state.subscribe('test_sdp_state_subscriber')

    assert sdp_state.current_state == 'unknown'
    assert sdp_state.target_state == 'unknown'
    sdp_state.update_current_state('init')
    assert sdp_state.current_state == 'init'
    assert sdp_state.target_state == 'unknown'

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'SDP'
    assert events[0].object_type == 'states'
    assert events[0].type == 'current_state_updated'
    assert events[0].data['old_state'] == 'unknown'
    assert events[0].data['state'] == 'init'

    # Set into standby state. This state is transitioned to by the EC
    # Master Controller when all SDP services are 'on'
    sdp_state.update_current_state('standby')
    event_queue.get_published_events()

    target_state = "on"
    previous_timestamp = sdp_state.target_timestamp
    set_time = sdp_state.update_target_state(target_state)
    assert sdp_state.target_state == target_state
    assert set_time >= previous_timestamp
    sdp_state.update_current_state(target_state)
    assert sdp_state.current_state == target_state

    events = event_queue.get_published_events()
    assert len(events) == 2
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'SDP'
    assert events[0].type == 'target_state_updated'
    assert events[0].data['old_state'] == 'unknown'
    assert events[0].data['state'] == 'on'
    assert sdp_state.target_state == target_state
    assert sdp_state.target_timestamp >= set_time

    target_state = "disable"
    previous_timestamp = sdp_state.target_timestamp
    set_time = sdp_state.update_target_state(target_state)
    assert sdp_state.target_state == target_state
    assert set_time >= previous_timestamp

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'SDP'
    assert events[0].type == 'target_state_updated'
    assert events[0].data['old_state'] == 'on'
    assert events[0].data['state'] == 'disable'
    assert sdp_state.target_state == target_state
    assert sdp_state.target_timestamp >= set_time

    target_state = "standby"
    previous_timestamp = sdp_state.target_timestamp
    set_time = sdp_state.update_target_state(target_state)
    assert sdp_state.target_state == target_state
    assert set_time >= previous_timestamp

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'SDP'
    assert events[0].type == 'target_state_updated'
    assert events[0].data['old_state'] == 'disable'
    assert events[0].data['state'] == 'standby'
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
    assert events[0].object_id == 'SDP'
    assert events[0].type == 'target_state_updated'
    assert events[0].data['old_state'] == 'standby'
    assert events[0].data['state'] == 'off'
    assert sdp_state.target_state == target_state
    assert sdp_state.target_timestamp >= set_time


def test_sdp_state_set_current_state():
    """Test updating the current state."""
    DB.flush_db()
    sdp_state = SDPState()
    event_queue = sdp_state.subscribe('test_update_target')

    current_state = "off"
    previous_timestamp = sdp_state.current_timestamp
    set_time = sdp_state.update_current_state(current_state)
    assert set_time >= previous_timestamp

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == 'SDP'
    assert events[0].type == 'current_state_updated'

    assert sdp_state.current_state == current_state
    assert sdp_state.current_timestamp >= set_time
