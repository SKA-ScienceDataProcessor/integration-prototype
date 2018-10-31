# -*- coding: utf-8 -*-
"""SDP services data object."""
from typing import List
import ast

from .config_db_redis import ConfigDb

DB = ConfigDb()


def register_service(subsystem: str, name: str, version: str):
    """Register a service with the Configuration Database."""
    DB.append_to_list('services', dict(subsystem=subsystem,
                                       name=name,
                                       version=version))


def unregister_service(subsystem: str, name: str, version: str):
    """Unregister a service with the Configuration Database.

    Raises:
        ValueError, if service is not found

    """
    service_descriptor = dict(subsystem=subsystem, name=name, version=version)
    DB._db.lrem('services', 0, service_descriptor)


def get_num_services(subsystem: str = None) -> int:
    """Return the number of services."""
    return len(get_service_list(subsystem))


def get_service_list(subsystem: str = None, name: str = None,
                     version: str = None) -> List[str]:
    """Return the list of services."""
    services = DB.get_list('services')
    services = [ast.literal_eval(service) for service in services]
    if subsystem is not None:
        services = [service for service in services
                    if service['subsystem'] == subsystem]

    if name is not None:
        services = [service for service in services
                    if service['name'] == name]

    if version is not None:
        services = [service for service in services
                    if service['version'] == version]

    return services
