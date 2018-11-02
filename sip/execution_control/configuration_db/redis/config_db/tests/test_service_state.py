# -*- coding: utf-8 -*-
"""Tests of the Service States API."""
from ..config_db_redis import ConfigDb
from ..service_state import ServiceState


DB = ConfigDb()


def test_create_service_object():
    """Test creating a service state data object."""
    DB.flush_db()
    service_state = ServiceState('ExecutionControl', 'MasterController',
                                 'test')
    assert service_state is not None


def test_set_target_state():
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

    target_state = "off"
    previous_timestamp = service_state.target_timestamp
    set_time = service_state.update_target_state(target_state)
    assert set_time >= previous_timestamp

    events = event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].object_type == 'states'
    assert events[0].object_id == object_id
    assert events[0].type == 'target_state_updated'

    assert service_state.target_state == target_state
    assert service_state.target_timestamp >= set_time


def test_set_current_state():
    """Test updating the current state."""
    DB.flush_db()
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

    assert service_state.current_state == current_state
    assert service_state.current_timestamp >= set_time
