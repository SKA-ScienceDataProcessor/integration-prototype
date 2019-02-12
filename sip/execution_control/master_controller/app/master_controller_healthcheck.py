# -*- coding: utf-8 -*-
"""Master Controller Service health check.

Checks to see that the system is up and running. Exit with value zero for
healthy or non-zero for unhealthy. Current version uses DockerSwarmClient to
check that all members of the swarm are running and dies if any member services
have no replicants.

TODO(NJT): Unit test

"""
import sched
import time

from sip_docker_swarm import DockerSwarmClient

SCHEDULER = sched.scheduler(time.time, time.sleep)

DC = DockerSwarmClient()


# class MasterHealthException(Exception):
#     """Class for master health exception."""
#
#     print("placeholder for master health exception class")


def _get_services():
    """Get list of service IDs.

    Returns:
        list, services ids

    """
    services_ids = DC.services
    return services_ids


def get_services_health():
    """Get the health of all services.

    Returns:
        dict, services id and health status

    """
    # Initialise
    services_health = {}

    # Get Service IDs
    services_ids = _get_services()
    # print(type(services_ids))
    # print("Services - ", services_ids)

    for s_id in services_ids:
        service_name = DC.get_service_name(s_id)
        # print("Service Name - {}", service_name)

        # Check if the current and actual replica levels are the same
        if DC.get_replicas(s_id) != DC.get_actual_replica(s_id):
            # print("Service in Unhealthy")
            services_health[service_name] = "Unhealthy"
            # TODO(NJT): Exception is required
        else:
            # print("Service {} is healthy", s_id)
            services_health[service_name] = "Healthy"

    print("Services Health - ", services_health)
    return services_health


def get_service_health(service_id: str):
    """Get the health of a service using service_id.

    Args:
        service_id

    Returns:
        str, health status

    """
    # Check if the current and actual replica levels are the same
    if DC.get_replicas(service_id) != DC.get_actual_replica(service_id):
        print("Service in Unhealthy")

        # TODO(NJT): Exception is required
        health_status = "Unhealthy"
    else:
        print("Service {} is healthy", service_id)
        health_status = "Healthy"

    return health_status


def overall_service_health():
    """Get the overall health of all the services.

    Returns:
        str, overall health status

    """
    services_health_status = get_services_health()

    # Evaluate overall health
    print("services_health_status: ", services_health_status)
    health_status = all(status == "Healthy" for status in
                        services_health_status.values())

    # Converting from bool to str
    if health_status:
        overall_status = "Healthy"
    else:
        overall_status = "Unhealthy"

    print("OVERALL STATUS:", overall_status)
    return overall_status


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
    get_services_health()
    overall_service_health()


if __name__ == "__main__":
    main()
    # try:
    #     main()
    # except MasterHealthException as err:
    #     print("MasterHealthException")
    #     # return 1
    # print("Return 0")
    # # return 0
