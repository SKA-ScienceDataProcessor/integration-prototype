# -*- coding: utf-8 -*-
"""Master Controller Service health check.

    Checks to see that the system is up and running.
    Exit with value zero for healthy or non-zero for unhealthy
    Current version uses DockerSwarmClient to check that all members
    of the swarm are running and dies if any member services have no replicants.
    
    TODO: Add number of replicants in each service and compare running replicants
    with this number
"""

import argparse
import random
import sched
import time
from typing import List

from sip_config_db._events.event import Event
from sip_config_db.states import SDPState, ServiceState
from sip_config_db.states.services import get_service_state_list
from sip_logging import init_logger

from skasip-docker_swarm import DockerSwarmClient  

from .__init__ import LOG, __service_id__, __service_name__

SCHEDULER = sched.scheduler(time.time, time.sleep)

DC = DockerSwarmClient()

class MasterHealthException(exception):
    pass

def _get_services():
    """Get list of service IDs"""
    services = DC.services
    if len(services) == 0:
        raise MasterHealthException('No services running')
    return services


def _check_replicants(services):
    """Check the number of replicants to ensure that all are running"""
    for s_id in services:
        if DC.get_replicas(s_id) == 0:
            raise MasterHealthException("No running tasks for service {}".format(s_id))
    # if we get here everything is A-OK


def main():
    """Entrypoint for this component"""
    services = _get_services()
    _check_replicants(services)


if __name__ == "__main__":
    try:
        main()
    except MasterHealthException as err:
        return 1
    return 0
