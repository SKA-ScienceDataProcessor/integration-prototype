# -*- coding: utf-8 -*-
"""Utility module to set initial data into the Configuration Database."""
import os

import redis
import simplejson as json


class ConfigInit:
    """Add initial data to the configuration database."""

    def __init__(self):
        """Initialise."""
        # Get Redis database object
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_db_id = os.getenv('REDIS_DB_ID', '0')
        pool = redis.ConnectionPool(host=redis_host, db=redis_db_id,
                                    decode_responses=True)
        self._db = redis.StrictRedis(connection_pool=pool)

        # Initialising variables
        self._master_controller_key = {}
        self._local_processing_controller = {}
        self._logging = {}

    def set_init_data(self, init_data):
        """Add master controller initial data to the configuration database."""
        # Parse the master controller data
        self._split_init_data(init_data)

        # Add keys and values to the configuration database
        master_controller_key = "execution_control:master_controller"
        self._db.hmset(master_controller_key, self._master_controller_key)

        sdp_components_local_key = "sdp_components:processing_controller"
        self._db.hmset(sdp_components_local_key,
                       self._local_processing_controller)

        sdp_components_logging_key = "sdp_components:logging"
        self._db.hmset(sdp_components_logging_key, self._logging)

    def _set_sdp_components_data(self, sdp_components_config):
        """Set class variables relating to SDP components."""
        for service in sdp_components_config:
            if service == 'processing_controller':
                self._local_processing_controller = \
                    sdp_components_config[service]
            if service == 'logging':
                self._logging = sdp_components_config[service]

    def _set_execution_control_data(self, ec_service_config):
        """Set class variables relating to Execution Control services."""
        for service in ec_service_config:
            if service == 'master_controller':
                mc_config = ec_service_config[service]
                for key in mc_config:
                    self._master_controller_key[key] = mc_config[key]

    def _split_init_data(self, init_data):
        """TODO - one line description.

        Split the master controller data into multiple
        keys before adding to the configuration database.
        """
        for top_level_key in init_data:

            if top_level_key == 'execution_control':
                self._set_execution_control_data(init_data[top_level_key])

            if top_level_key == 'sdp_components':
                self._set_sdp_components_data(init_data[top_level_key])


def main():
    """Add initial data to the database."""
    print("Adding Initial Data")
    config_file_path = os.path.join(os.path.dirname(__file__), 'data',
                                    'initial_states.json')
    with open(config_file_path, 'r') as file:
        schema_data = file.read()
    init_data = json.loads(schema_data)
    db_client = ConfigInit()
    db_client.set_init_data(init_data)
    print("Data Added")


if __name__ == '__main__':
    main()
