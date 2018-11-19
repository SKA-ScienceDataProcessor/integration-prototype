# coding=utf-8
"""Module for interacting with services in the Configuration Database."""
from typing import List

from .. import DB, LOG
from .service_state import ServiceState


def get_service_state_list() -> List[ServiceState]:
    """Return a list of ServiceState objects known to SDP."""
    keys = DB.get_keys('states*')
    LOG.debug('Loading list of known services.')
    services = []
    for key in keys:
        _, subsystem, name, version = key.split(':')
        services.append(ServiceState(subsystem, name, version))
    return services
