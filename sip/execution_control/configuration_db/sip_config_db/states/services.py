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
        values = key.split(':')
        if len(values) == 4:
            services.append(ServiceState(*values[1:4]))
    return services


def get_service_id_list() -> List[tuple]:
    """Return list of Services."""
    keys = DB.get_keys('states*')
    services = []
    for key in keys:
        values = key.split(':')
        if len(values) == 4:
            services.append(':'.join(values[1:]))
    return services
