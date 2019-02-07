# -*- coding: utf-8 -*-
"""Master Controller Service health check.

Checks to see that the system is up and running. Exit with value zero for
healthy or non-zero for unhealthy. Current version uses DockerSwarmClient to
check that all members of the swarm are running and dies if any member services
have no replicants.

TODO(NJT): Function that queries the health of each services (expected vs replication level)
TODO(NJT): Return the value
TODO(NJT): Unit test

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

from .__init__ import LOG, __service_id__, __service_name__

SCHEDULER = sched.scheduler(time.time, time.sleep)

DC = DockerSwarmClient()


def _get_services():
    """Get list of service IDs

    Returns:

    """
    services_ids = DC.services

    # TODO(NJT): Require Exception

    return services_ids


def service_health():
    """This function queries the health of each services.

    Returns:
        str, health status
    """

    # Get Service IDs
    services_ids = _get_services()
    print(type(services_ids))
    print("Services - ", services_ids)

    for s_id in services_ids:
        service_name = DC.get_service_name(s_id)
        print("Service Name - {}", service_name)

        # Check if the current and actual replica levels are the same
        if DC.get_replicas(s_id) != DC.get_actual_replica(s_id):
            print("Service in Unhealthy")
            # TODO(NJT): Exception is required
        else:
            print("Service {} is healthy", s_id)

    # TODO(NJT): Need to return either service name or id with the health status


# class MasterHealthException(Exception):
#     """Class for master health exception."""
#
#     print("placeholder for master health exception class")
#
#
# def _get_services():
#     """Get list of service IDs."""
#     services = DC.services
#     if not services:
#         raise MasterHealthException('No services running')
#     return services
#
#
# def _check_replicants(services):
#     """Check the number of replicas to ensure that all are running."""
#     for s_id in services:
#         service_name = DC.get_service_name(s_id)
#         if service_name == "sip_ec_master_controller":
#             print("Master Controller Service name - ", service_name)
#             num_replica = DC.get_replicas(s_id)
#             print("MC Replica -", num_replica)
#
#             # Check if the current and actual replica levels are the same
#             if DC.get_replicas(s_id) != DC.get_actual_replica(s_id):
#                 raise MasterHealthException(
#                     "No running tasks for service {}".format(s_id))
#     # if we get here everything is OK


def main():
    """Entrypoint for this component."""
    # services = _get_services()
    # _check_replicants(services)
    service_health()


if __name__ == "__main__":
    main()
    # try:
    #     main()
    # except MasterHealthException as err:
    #     print("MasterHealthException")
    #     # return 1
    # print("Return 0")
    # # return 0
