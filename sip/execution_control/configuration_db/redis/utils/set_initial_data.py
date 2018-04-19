# -*- coding: utf-8 -*-
""" Set initial data to the configuration database"""

import simplejson as json
import os
import redis

class ConfigInit():
    """Set Initial Data to the configuration database"""
    def __init__(self):
        """Initialisation"""
        # Get Redis database object
        REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        REDIS_DB_ID = os.getenv('REDIS_DB_ID', 0)
        self._db = redis.StrictRedis(host=REDIS_HOST, db=REDIS_DB_ID)

        # Initialising varibales
        self._master_controller_key = {}
        self._service_list = []
        self._local_sky_model = {}
        self._telescope_model = {}
        self._data_queue = {}
        self._logging = {}

    def set_init_data(self, init_data):
        """Add master controller initial data to the configuration database"""
        # Parse the master controller data
        self.split_init_data(init_data)

        # Add keys and values to the configuration database
        # TODO: (NJT) Optimize the code
        master_controller_key = "execution_control:master_controller"
        print(self._master_controller_key)
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

    def split_init_data(self, init_data):
        """Splitting the master controller data into multiple
        keys before adding to the configuration database"""
        for top_level_key in init_data:
            for nested_key in init_data[top_level_key]:
                if nested_key == 'master_controller':
                    self._service_list = init_data[top_level_key][nested_key][
                        'service_list']
                    for keys in init_data[top_level_key][nested_key]:
                        if keys != 'service_list':
                            self._master_controller_key[keys] = init_data[
                                top_level_key][nested_key][keys]

            if top_level_key == 'sdp_services':
                for key in init_data[top_level_key]:
                    if key == 'local_sky_model':
                        self._local_sky_model = init_data[top_level_key][key]

                    if key == 'telescope_model':
                        self._telescope_model = init_data[top_level_key][key]

                    if key == 'data_queue':
                        self._data_queue = init_data[top_level_key][key]

            if top_level_key == 'system_services':
                for key in init_data[top_level_key]:
                    if key == 'logging':
                        self._logging = init_data[top_level_key][key]

def main():
    """Add initial data to the database"""
    print("Adding Initial Data")
    with open('utils/initial_data.json', 'r') as f:
        schema_data = f.read()
    init_data = json.loads(schema_data)
    db = ConfigInit()
    db.set_init_data(init_data)
    print("Data Added")

if __name__ == '__main__':
    main()
