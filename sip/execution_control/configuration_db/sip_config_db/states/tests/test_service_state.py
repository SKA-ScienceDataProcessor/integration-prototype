# -*- coding: utf-8 -*-
"""Tests of the Service States API."""
import pytest

from .. import ServiceState
from ... import ConfigDb

DB = ConfigDb()


def test_service_state_create():
    """Test creating a service state data object."""
    DB.flush_db()
    _service_state = ServiceState('ExecutionControl', 'MasterController',
                                  'test')

    # Creating the state object again should be allowed
    service_state = ServiceState('ExecutionControl', 'MasterController',
                                 'test')
    assert service_state.id == _service_state.id
    assert service_state is not None

    # Expect error message if subsystem is invalid.
    with pytest.raises(ValueError, match=r'Invalid subsystem'):
        ServiceState('InvalidSubsystem', 'MasterController', '1.0.0')

    assert 'init' in service_state.allowed_target_states
    assert 'on' in service_state.allowed_target_states
    assert 'alarm' in service_state.allowed_target_states
    assert 'fault' in service_state.allowed_target_states
    assert 'off' in service_state.allowed_target_states

    assert repr(service_state) == 'ExecutionControl:MasterController:test'


def test_service_state_properties():
    """Test service state object properties."""
    DB.flush_db()
    state = ServiceState('ExecutionControl', 'MasterController', 'test')

    # The total set of allowed states for SDP services
    assert state.allowed_states == ['init', 'on', 'off', 'alarm', 'fault']

    # Dictionary of allowed state transitions for SDP services
    for allowed_state in state.allowed_states:
        assert allowed_state in state.allowed_state_transitions

    # Check behaviour of current state setter and getter
    assert state.current_state == 'unknown'

    # Cant set the target when the current state is undefined
    with pytest.raises(RuntimeError, match=r"Unable to set target state"):
        state.target_state = 'on'

    # Set the current state to init
    state.current_state = 'init'
    assert state.current_state == 'init'

    # Set the current state to on
    state.current_state = 'on'
    assert state.current_state == 'on'

    # Check behaviour of target state setter and getter
    assert state.target_state == 'unknown'

    # Try to set the target state to an invalid state results in an error.
    with pytest.raises(ValueError, match=r'Invalid target state'):
        state.target_state = 'undefined_state'

    state.target_state = 'off'
    assert state.target_state == 'off'


def test_service_state_set_target():
    """Test updating the target state."""
    DB.flush_db()
    service_subsystem = 'TangoControl'
    service_name = 'SDPMaster'
    service_version = 'test'
    object_id = ServiceState.get_service_state_object_id(
        service_subsystem, service_name, service_version)
    service_state = ServiceState(service_subsystem, service_name,
                                 service_version)
    event_queue = service_state.subscribe('test_update_target')

    service_state.update_current_state('on')

    events = event_queue.get_published_events()
    assert len(events) == 1

    target_state = "off"
    previous_timestamp = service_state.target_timestamp
    set_time = service_state.update_target_state(target_state)
    assert set_time >= previous_timestamp

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == object_id
    assert events[0].type == 'target_state_updated'
    assert events[0].data['old_state'] == 'unknown'
    assert events[0].data['state'] == 'off'

    assert service_state.target_state == target_state
    assert service_state.target_timestamp >= set_time


def test_service_state_current_state_simple():
    """Basic test of setting and getting the current state.

    For Service state transitions, see Fig4 of the SIP Report.
    """
    DB.flush_db()
    service_state = ServiceState('TangoControl', 'SDPMaster', '1.0.0')
    assert service_state.current_state == 'unknown'
    # Set the current state to 'init'.
    service_state.current_state = 'init'
    # From the 'init' state it should be possible to stay in init!
    service_state.current_state = 'init'
    service_state.current_state = 'on'
    service_state.current_state = 'alarm'
    service_state.current_state = 'fault'
    with pytest.raises(ValueError, message='Invalid current state update'):
        service_state.current_state = 'alarm'


def test_service_state_set_current():
    """Test updating the current state."""
    DB.flush_db()
    service_subsystem = 'TangoControl'
    service_name = 'SDPMaster'
    service_version = 'test'
    object_id = ServiceState.get_service_state_object_id(
        service_subsystem, service_name, service_version)
    service_state = ServiceState(service_subsystem, service_name,
                                 service_version)
    service_state.subscribe('test_update_target')
    event_queue = service_state.get_event_queue('test_update_target')

    assert 'test_update_target' in service_state.get_subscribers()

    current_state = "off"
    previous_timestamp = service_state.current_timestamp
    set_time = service_state.update_current_state(current_state)
    assert set_time >= previous_timestamp

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == object_id
    assert events[0].type == 'current_state_updated'
    assert events[0].data['old_state'] == 'unknown'
    assert events[0].data['state'] == 'off'

    assert service_state.current_state == current_state
    assert service_state.current_timestamp >= set_time
