# -*- coding: utf-8 -*-
"""Master Controller Service health check.

Checks to see that the system is up and running. Exit with value zero for
healthy or non-zero for unhealthy. Current version uses DockerSwarmClient to
check that all members of the swarm are running and dies if any member services
have no replicants.

TODO(NJT): Unit test

"""
from sip_docker_swarm import DockerSwarmClient


class MasterHealthCheck:
    """Master Controller Health Monitoring Interface."""

    def __init__(self):
        """Initialise class."""
        self._dc = DockerSwarmClient()

    ###########################################################################
    # Get functions
    ###########################################################################

    def get_services_health(self) -> dict:
        """Get the health of all services.

        Returns:
            dict, services id and health status

        """
        # Initialise
        services_health = {}

        # Get Service IDs
        services_ids = self._get_services()

        for s_id in services_ids:
            service_name = self._dc.get_service_name(s_id)

            # Check if the current and actual replica levels are the same
            if self._dc.get_replicas(s_id) != self._dc.get_actual_replica(s_id):
                services_health[service_name] = "Unhealthy"
                # TODO(NJT): Exception is required
            else:
                services_health[service_name] = "Healthy"

        return services_health

    def get_service_health(self, service_id: str) -> str:
        """Get the health of a service using service_id.

        Args:
            service_id

        Returns:
            str, health status

        """
        # Check if the current and actual replica levels are the same
        if self._dc.get_replicas(service_id) != self._dc.get_actual_replica(
                service_id):
            # TODO(NJT): Exception is required
            health_status = "Unhealthy"
        else:
            health_status = "Healthy"

        return health_status

    def overall_services_health(self) -> str:
        """Get the overall health of all the services.

        Returns:
            str, overall health status

        """
        services_health_status = self.get_services_health()

        # Evaluate overall health
        health_status = all(status == "Healthy" for status in
                            services_health_status.values())

        # Converting from bool to str
        if health_status:
            overall_status = "Healthy"
        else:
            overall_status = "Unhealthy"

        return overall_status

    ###########################################################################
    # Static methods
    ###########################################################################

    @staticmethod
    def _get_services():
        """Get list of service IDs.

        Returns:
            list, services ids

        """
        services_ids = DockerSwarmClient.services
        return services_ids
