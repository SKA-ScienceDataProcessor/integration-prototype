# -*- coding: utf-8 -*-
""" Configuration Service Client API"""

import redis
import json
from jsonschema import validate
from pprint import pprint
from flatten_json import flatten
import os
import ast
from time import sleep

class ConfigDB():
    """Client API Interface"""
    def __init__(self):
        """Initialisation"""
        # Get Redis database object
        REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        REDIS_DB_ID = os.getenv('REDIS_DB_ID', 0)

        self._db = redis.StrictRedis(host=REDIS_HOST, db=REDIS_DB_ID)

    def get_state(self, key, field):
        """Get the state of the key"""
        key = ':'.join(key)
        state = self._db.hget(key, field)
        if state:
            return state.decode('utf-8')
        else:
            return None

    def add_state(self, key, field, value):
        """Add the state of the key and field"""
        self._db.hset(key, field, value)

    def get_list_length(self, key):
        """ Returns the number of elements in a list
        If the does not point to a list 0 is return"""
        key = ':'.join(key)
        len = self._db.llen(key)
        if len:
            return len
        else:
            return 0

    def get_list(self, key):
        """ Get list of service"""
        key = ':'.join(key)
        for i in self._db.lrange(key, 0, -1):
            list_eval = ast.literal_eval(i.decode('utf-8'))
            sleep(.5)
            yield list_eval
        return list_eval

    def get_element(self, key, n):
        """ Get the n'th element of a list
        If the does not point to an element 0 is return"""
        key = ':'.join(key)
        n_element = self._db.lindex(key, n)
        if n_element:
            n_element_eval = ast.literal_eval(n_element.decode('utf-8'))
            return n_element_eval
        else:
            return 0


    def add_element(self, key, element):
        """ Add an new entry to the end of a list"""
        key = ':'.join(key)
        self._db.lpush(key, element)

    def to_key(self, v_path):
        """ Converts a value from the database to a service path list"""
        s_path = v_path.split('.')
        key = ':'.join(s_path)
        return key

    def update_state(self, v_path, state, value):
        """ Update the state of the service"""
        key = self.to_key(v_path)
        self.add_state(key, state, value)

    ############################################################################

    def set_scheduling_block(self, scheduling_block):
        """Set scheduling block instance. 
        This includes adding the processing blocks"""
        schema = self.get_schema()
        try:
            # Validates the schema
            validate(scheduling_block, schema)
        except:
            print("Schema Validation Error")

        json_dump = json.dumps(scheduling_block)
        block_object = json.loads(json_dump)

        # Add status
        updated_block = self.add_status(block_object)

        # Splitting the data into different keys before adding
        # to the database
        block_key, processing_key = self.split_scheduling_block(
            updated_block)

        # Adding Scheduling block instance with id
        instance_key = "scheduling_block_instance:" + \
                       updated_block["sched_block_instance_id"]
        self._db.hmset(instance_key, block_key)

        # Add a event to the scheduling block event list to notify
        # of a new scheduling block being added to the db.
        self._db.rpush('scheduling_block_events', dict(
            type=updated_block["status"],
            id=updated_block["sched_block_instance_id"]))

        # Adding Processing block with id
        for value in processing_key:
            p_instance_key = "scheduling_block_instance:" + \
                             updated_block["sched_block_instance_id"] + \
                             ":processing_block" + ":" + value['id']
            self._db.hmset(p_instance_key, value)

            # Add a event to the processing block event list to notify
            # of a new processing block being added to the db.
            self._db.rpush('processing_block_events', dict(
                type=value["status"],
                id=value["id"]))

    def delete_key(self, key):
        """Delete key"""
        if type(key) != list:
            self._db.delete(key)
        else:
            j_key = ':'.join(key)
            self._db.delete(j_key)

    def get_key(self, id):
        """Search keys"""
        key_search = '*' + id
        if key_search:
            key = self._db.keys(key_search)
        return key

    def get_all_keys(self, id):
        """Search all keys associated with the id"""
        key_search = '*' + id + '*'
        if key_search:
            keys = self._db.keys(key_search)
        return keys

    def get_event(self, event):
        """Get the latest event added"""
        event_join = event + '_events'
        history_join = event + '_event_history'
        event = self._db.rpoplpush(event_join, history_join)
        if event:
            event = ast.literal_eval(event.decode('utf-8'))
        return event

    def get_schema(self):
        """Gets the scheduling block instance schema for validation"""
        # TODO: (NJT) Need to change how schema is loaded
        with open('schema/scheduling_block_schema.json', 'r') as f:
            schema_top_data = f.read()
        schema = json.loads(schema_top_data)
        return schema

    def add_status(self, scheduling_block):
        """This function adds status key value pair to all the section
        in the scheduling block instance"""
        scheduling_block['status'] = "created"
        for key in scheduling_block:
            # print(type(scheduling_block[key]))
            if type(scheduling_block[key]) == list:
                for p in scheduling_block[key]:
                    p['status'] = 'created'
        return scheduling_block

    def update_status(self, key, field, value):
        """ Update status"""
        key_join = ":".join(key)
        s_key = self.get_key(key_join)
        if s_key:
            for u_key in s_key:
                self.add_state(u_key, field, value)

    def delete_block(self, key):
        """Removes the scheduling block instance and all processing blocks 
        associated with it. Any key that has the scheduling block instance 
        if is removed from the database"""
        s_keys = self.get_all_keys(key)
        if s_keys:
            for k in s_keys:
                key_decode = k.decode('utf-8')
                if "processing_block" not in key_decode:
                    self._db.delete(key_decode)
                else:
                    self.delete_processing_block(key_decode)

            # Add a event to the scheduling block event list to notify
            # of a deleting a scheduling block from the db
            self._db.rpush('scheduling_block_events',
                           dict(type="deleted", id=key))

    def delete_processing_block(self, processing__block):
        """Delete processing block using processing block id 
        and using scheduling block id if given"""
        if type(processing__block) is list:
            for id in processing__block:
                key = self.get_key(id)
                for k in key:
                    self._db.delete(k.decode('utf-8'))

                    # Add a event to the processing block event list to notify
                    # about deleting from the db
                    self._db.rpush('processing_block_events',
                                   dict(type="deleted", id=id))
        else:
            split_key = processing__block.split(':')
            self._db.delete(processing__block)

            # Add a event to the processing block event list to notify
            # about deleting from the db
            self._db.rpush('processing_block_events',
                           dict(type="deleted", id=split_key[3]))

    def split_scheduling_block(self, scheduling_block):
        """Split the scheduling block data into multiple keys 
        before adding to the configuration database"""
        scheduling_block_key = {}
        processing_key = {}
        for key in scheduling_block:
            values = scheduling_block[key]
            if type(scheduling_block[key]) != list:
                 scheduling_block_key[key] = values
            else:
                processing_key = values
        return scheduling_block_key, processing_key

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