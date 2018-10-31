# coding=utf-8
"""Test the Service List data object API."""
from ..config_db_redis import ConfigDb
from ..service_list import (register_service, unregister_service,
                            get_num_services, get_service_list)


DB = ConfigDb()


def test_register_services():
    """Test registering a set of services."""
    DB.flush_db()

    register_service('ExecutionControl', 'MasterController', 'test')
    register_service('ExecutionControl', 'ProcessingController', 'test')
    register_service('TangoControl', 'SDPMaster', 'test')
    assert get_num_services() == 3
    assert get_num_services(subsystem='ExecutionControl') == 2
    assert get_num_services(subsystem='TangoControl') == 1

    unregister_service('ExecutionControl', 'ProcessingController', 'test')

    assert get_num_services() == 2
    assert get_num_services(subsystem='ExecutionControl') == 1
    assert get_num_services(subsystem='TangoControl') == 1

    services = get_service_list()
    assert len(services) == 2
