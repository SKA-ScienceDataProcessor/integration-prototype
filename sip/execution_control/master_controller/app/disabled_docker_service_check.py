# -*- coding: utf-8 -*-
"""Master Controller Service health check.

Checks to see that the system is up and running. Exit with value zero for
healthy or non-zero for unhealthy. Current version uses DockerSwarmClient to
check that all members of the swarm are running and dies if any member services
have no replicants.

TODO(NJT): Add number of replicants in each service and compare.
"""
# import argparse
# import random
import sched
import time
# from typing import List

# from sip_config_db._events.event import Event
# from sip_config_db.states import SDPState, ServiceState
# from sip_config_db.states.services import get_service_state_list
# from sip_logging import init_logger

from sip_docker_swarm import DockerSwarmClient

# from .__init__ import LOG, __service_id__, __service_name__

SCHEDULER = sched.scheduler(time.time, time.sleep)

DC = DockerSwarmClient()


class MasterHealthException(Exception):
    """Class for master health exception."""

    print("placeholder for master health exception class")


def _get_services():
    """Get list of service IDs."""
    services = DC.services
    if not services:
        raise MasterHealthException('No services running')
    return services


def _check_replicants(services):
    """Check the number of replicants to ensure that all are running."""
    for s_id in services:
        if DC.get_replicas(s_id) == 0:
            raise MasterHealthException(
                "No running tasks for service {}".format(s_id))
    # if we get here everything is OK


def main():
    """Entrypoint for this component."""
    services = _get_services()
    _check_replicants(services)


if __name__ == "__main__":
    try:
        main()
    except MasterHealthException as err:
        print("MasterHealthException")
        # return 1
    print("Return 0")
    # return 0
