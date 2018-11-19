# coding=utf-8
"""Unit testing for the states.services module."""
from ... import DB
from ..service_state import ServiceState
from ..services import get_service_state_list


def test_states_get_service_list():
    """Get the list of known services."""
    DB.flush_db()
    service = ServiceState('ExecutionControl', 'MasterController',
                           '1.0.0')
    assert service.id == 'ExecutionControl:MasterController:1.0.0'
    assert service.subsystem == 'ExecutionControl'
    assert service.name == 'MasterController'
    assert service.version == '1.0.0'
    ServiceState('TangoControl', 'SDPMaster', '1.0.0')
    ServiceState('TangoControl', 'TangoDatabaseDS', '1.0.0')
    ServiceState('TangoControl', 'TangoMySQL', '1.0.0')
    ServiceState('Platform', 'Redis', '1.0.0')
    ServiceState('Platform', 'Kafka', '1.0.0')

    services = get_service_state_list()
    assert service.id in [service.id for service in services]
