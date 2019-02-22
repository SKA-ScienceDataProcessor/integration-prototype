# -*- coding: utf-8 -*-
"""Master Controller Service Health Monitoring."""
import logging
from sip_docker_swarm import DockerSwarmClient

DC = DockerSwarmClient()
LOG = logging.getLogger('sip.ec.mc.health_check')


class MasterHealthCheck:
    """Master Controller Health Monitoring Interface."""

    ###########################################################################
    # Properties / attributes
    ###########################################################################

    @property
    def services_health(self) -> dict:
        """Get dict of services id and health status.

        Returns:
            dict, services ids and health status

        """
        return self.get_services_health()

    @property
    def overall_health(self) -> str:
        """Get overall health status of all the services.

        Returns:
            str, overall health of all the services

        """
        return self.get_overall_services_health()

    ##########################################################################
    # Get functions
    ##########################################################################

    def get_services_health(self) -> dict:
        """Get the health of all services.

        Returns:
            dict, services id and health status

        """
        # Initialise
        services_health = {}

        # Get Service IDs
        services_ids = self._get_services()

        for service_id in services_ids:
            service_name = DC.get_service_name(service_id)

            # Check if the current and actual replica levels are the same
            if DC.get_replicas(service_id) != \
                    DC.get_actual_replica(service_id):
                services_health[service_name] = "Unhealthy"
            else:
                services_health[service_name] = "Healthy"

        return services_health

    def get_overall_services_health(self) -> str:
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

    ##########################################################################
    # Static methods
    ##########################################################################

    @staticmethod
    def get_service_health(service_id: str) -> str:
        """Get the health of a service using service_id.

        Args:
            service_id

        Returns:
            str, health status

        """
        # Check if the current and actual replica levels are the same
        if DC.get_replicas(service_id) != DC.get_actual_replica(service_id):
            health_status = "Unhealthy"
        else:
            health_status = "Healthy"

        return health_status

    @staticmethod
    def _get_services():
        """Get list of service IDs.

        Returns:
            list, services ids

        """
        services_ids = DC.services
        LOG.debug("Service IDS %s", services_ids)
        return services_ids
