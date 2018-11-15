# -*- coding: utf-8 -*-
"""Tests of the Service States API."""
import pytest

from ..config_db_redis import ConfigDb
from ..service_state import ServiceState


def test_service_state_create():
    """Test creating a service state data object."""
    ConfigDb().flush_db()
    service_state = ServiceState('ExecutionControl', 'MasterController',
                                 'test')
    assert service_state is not None


def test_service_state_set_target():
    """Test updating the target state."""
    ConfigDb().flush_db()
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
    assert events[0].data['new_state'] == 'off'

    assert service_state.target_state == target_state
    assert service_state.target_timestamp >= set_time


def test_service_state_current_state_simple():
    """Basic test of setting and getting the current state.

    For Service state transitions, see Fig4 of the SIP Report.
    """
    ConfigDb().flush_db()
    service_state = ServiceState('Subsystem', 'Service', '1.0.0')
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
    ConfigDb().flush_db()
    service_subsystem = 'TangoControl'
    service_name = 'SDPMaster'
    service_version = 'test'
    object_id = ServiceState.get_service_state_object_id(
        service_subsystem, service_name, service_version)
    service_state = ServiceState(service_subsystem, service_name,
                                 service_version)
    event_queue = service_state.subscribe('test_update_target')

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
    assert events[0].data['new_state'] == 'off'

    assert service_state.current_state == current_state
    assert service_state.current_timestamp >= set_time
