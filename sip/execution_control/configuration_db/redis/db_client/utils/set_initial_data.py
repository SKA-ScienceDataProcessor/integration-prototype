# -*- coding: utf-8 -*-
"""Set initial data to the configuration database"""

import os

import redis
import simplejson as json


class ConfigInit:
    """Set Initial Data to the configuration database"""

    def __init__(self):
        """Initialisation"""
        # Get Redis database object
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_db_id = os.getenv('REDIS_DB_ID', 0)
        pool = redis.ConnectionPool(host=redis_host, db=redis_db_id,
                                    decode_responses=True)
        self._db = redis.StrictRedis(connection_pool=pool)

        # Initialising variables
        self._master_controller_key = {}
        self._service_list = []
        self._local_sky_model = {}
        self._telescope_model = {}
        self._data_queue = {}
        self._logging = {}

    def set_init_data(self, init_data):
        """Add master controller initial data to the configuration database"""
        # Parse the master controller data
        self._split_init_data(init_data)

        # Add keys and values to the configuration database
        master_controller_key = "execution_control:master_controller"
        self._db.hmset(master_controller_key, self._master_controller_key)

        service_list_key = "execution_control:master_controller:service_list"
        for service_list in self._service_list:
            self._db.lpush(service_list_key, service_list)

        sdp_service_local_key = "sdp_services:local_sky_model"
        self._db.hmset(sdp_service_local_key, self._local_sky_model)

        sdp_service_telescope_key = "sdp_services:telescope_model"
        self._db.hmset(sdp_service_telescope_key, self._telescope_model)

        sdp_service_data_key = "sdp_services:data_queue"
        self._db.hmset(sdp_service_data_key, self._data_queue)

        system_service_logging_key = "system_services:logging"
        self._db.hmset(system_service_logging_key, self._logging)

    def _set_sdp_services_data(self, sdp_service_config):
        """Set class variables relating to SDP services."""
        for service in sdp_service_config:
            if service == 'local_sky_model':
                self._local_sky_model = sdp_service_config[service]

            if service == 'telescope_model':
                self._telescope_model = sdp_service_config[service]

            if service == 'data_queue':
                self._data_queue = sdp_service_config[service]

    def _set_system_services_data(self, system_service_config):
        """Set class variables relating to System services"""
        for service in system_service_config:
            if service == 'logging':
                self._logging = system_service_config[service]

    def _set_execution_control_data(self, ec_service_config):
        """Set class variables relating to Execution Control services"""
        for service in ec_service_config:
            if service == 'master_controller':
                mc_config = ec_service_config[service]
                for key in mc_config:
                    if key == 'service_list':
                        self._service_list = mc_config['service_list']
                    else:
                        self._master_controller_key[key] = mc_config[key]

    def _split_init_data(self, init_data):
        """Splitting the master controller data into multiple
        keys before adding to the configuration database"""

        for top_level_key in init_data:

            if top_level_key == 'execution_control':
                self._set_execution_control_data(init_data[top_level_key])

            if top_level_key == 'sdp_services':
                self._set_sdp_services_data(init_data[top_level_key])

            if top_level_key == 'system_services':
                self._set_system_services_data(init_data[top_level_key])


def main():
    """Add initial data to the database"""
    print("Adding Initial Data")
    config_file_path = os.path.join(os.path.dirname(__file__),
                                    'initial_data.json')
    with open(config_file_path, 'r') as file:
        schema_data = file.read()
    init_data = json.loads(schema_data)
    db_client = ConfigInit()
    db_client.set_init_data(init_data)
    print("Data Added")


if __name__ == '__main__':
    main()
