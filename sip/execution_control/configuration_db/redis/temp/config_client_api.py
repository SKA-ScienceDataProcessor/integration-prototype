# -*- coding: utf-8 -*-
""" Client API"""

import redis
import json
from jsonschema import validate
from pprint import pprint
from flatten_json import flatten
import os
import ast
from time import sleep

class ConfigClient():
    """
    Client API Interface
    

    Get full snapshot of the data in the database
    Set scheduling block instance to the database
        - add status in all the properties (get the correct word)
    Set assigned resources to the processing block
        - requires processing block id, scheduling block instance id
    Update status
        - processing block id, instance id and a the variable name
    Get status of specific processing block
        - requires block block id, scheduling block instance id
    Use rpush, rpop for sending information to processing controller scheduler
        that a new schedule block instance has arrived or deleted. Review the code
        ben has send. A separate is key is required for this
    Get snapshot of of the full processing blocks
    Snapshot of the list of processing blocks for a specific schedule block instance
    Delete scheduling block and processing block associated with it
        - inform proccessing controller scheduler

    Connect to a server. Not hard coded
    Look into key pattern - What does this do?

    Think about how the information is going to be stored in the database
        - validate with the schema
        -
    """

    def __init__(self):
        # Setting up connection with the master and a slave
        # self._conn = redis.ConnectionPool(host='localhost', port=6379, db=0)
        # self._server = redis.Redis(connection_pool=self._conn)

        # Get Redis database object
        REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        REDIS_DB_ID = os.getenv('REDIS_DB_ID', 0)

        # Need to change the name to self._db
        self._db = redis.StrictRedis(host=REDIS_HOST, db=REDIS_DB_ID)

        # Initialising varibales
        self._master_controller_key = {}
        self._service_list = []
        self._local_sky_model = {}
        self._telescope_model = {}
        self._data_queue = {}
        self._logging = {}

    def set_init_data(self, init_data):
        """
        Add master controller initial data to the configuration database
        """
        # Parse the master controller data
        self.split_init_data(init_data)

        # Add keys and values to the configuration database
        # TODO: (NJT) Optimize the code
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


    def handle_key(self, key_list):
        """
        Generic database API
        Gets a handle or points in the database.
        """
        # TODO: (NJT) Implement this function
        construct_key = key_list[0] + ":" + key_list[1] + ":" + key_list[2]
        for i in self._db.lrange(construct_key, 0, -1):
            sleep(.5)
            yield i
        return i

    def get_state(self, service, state, sub_service=None,):
        """Get the state of the service"""
        # TODO: (NJT) Might not need this function. As the state
        # TODO: will always be updated my master controller
        if sub_service != None:
            key_search = self._db.keys(service + '*' + sub_service)
            for key in key_search:
                state = self._db.hget(key, state)
            if state:
                state = state.decode('utf-8')
        else:
            key_search = self._db.keys('*' + service)
            for key in key_search:
                state = self._db.hget(key, state)
            if state:
                state = state.decode('utf-8')
        return state

    def update_state(self, service, state, sub_service=None, m_state=None):
        """Update the status of the"""
        # TODO: (NJT) Implement Error Messages
        if sub_service != None:
            key_search = self._db.keys(service + '*' + sub_service)
            for key in key_search:
                update_state = {"state": state}
                self._db.hmset(key, update_state)
        else:
            key_search = self._db.keys('*' + service)
            for key in key_search:
                update_state = {m_state: state}
                self._db.hmset(key, update_state)

    def get_service_list(self):
        """Get the list of services"""
        # TODO: (NJT) Implement Error Messages
        service_list = []
        key_search = self._db.keys('*master_controller:service_list')
        for key in key_search:
            list = self._db.lrange(key, 0, -1)
            for items in list:
                service_list.append(items.decode('utf-8'))
        return service_list

    def get_service_from_list(self, name):
        """Get the service details from the service list"""
        # TODO: (NJT) Implement Error Messages
        service = []
        service_list = self.get_service_list()
        for items in service_list:
            if name in items:
                service.append(items)
                # TODO: (NJT) Need to check if splitting required here
                # split_value = items.split(",")
                # enabled = split_value[1].split(":")
                # #print(enabled[1])
        return service

    def add_service_to_list(self):
        """Add service to the service list"""
        # TODO: (NJT) Implement the function
        # TODO: (NJT) Test the function
        # TODO: (NJT) Implement Error Messages
        print("Placeholder")

    def set_schedule_block_instance(self, scheduling_block_data):
        """
        Set scheduling block instance
        This includes adding the processing blocks and each of of its stages
        """
        scheduling_block_schema = self.get_schema()

        try:
            # Validates the schema
            validate(scheduling_block_data, scheduling_block_schema)
        except:
            print("Validation Error - Schema")

        # Add status
        self.add_status(scheduling_block_data)

        # Splitting the data into different keys before adding
        # to the database
        scheduling_block_key, processing_key = self.split_scheduling_block(
            scheduling_block_data)
        # Adding Scheduling block instance with id
        instance_key = "schedule_block_instance:" + \
                       scheduling_block_data["sched_block_instance_id"]
        self._db.hmset(instance_key, scheduling_block_key)

        # Add a event to the scheduling block event list to notify
        # of a new scheduling block being added to the db.
        self._db.rpush('scheduling_block_events', dict(
            type=scheduling_block_data["status"],
            id=scheduling_block_data["sched_block_instance_id"]))

        # TODO: (NJT) Add processing blocks
        # TODO: (NJT) Test the function
        # TODO: (NJT) Implement Error Messages

    def get_scheduling_block_event(self):
        """
        Get the latest event added to the scheduling block
        """
        event = self._db.rpoplpush('scheduling_block_events',
                                   'scheduling_block_event_history')
        if event:
            event = ast.literal_eval(event.decode('utf-8'))
        return (event)


    def get_scheduling_block(self, block_id):
        """Get scheduling bock instance for the
        configuration database"""
        instance_search = '*' + block_id
        scheduling_block_key = self._db.keys(instance_search)
        return scheduling_block_key

    def get_processing_block(self, processing_block_id, block_id=None):
        """
        Get processing block using processing block id 
        and using scheduling block id if given
        """
        # TODO: (NJT) Implement the function
        # TODO: (NJT) Test the function
        # TODO: (NJT) Implement Error Messages
        print("Placeholder")

    def delete_processing_block(self, processing_block_id, block_id=None):
        """
        Delete processing block using processing block id 
        and using scheduling block id if given
        """
        # TODO: (NJT) Implement the function
        # TODO: (NJT) Test the function
        # TODO: (NJT) Implement Error Messages
        print("Placeholder")

    def delete_scheduling_block(self, block_id):
        """
        Removes the scheduling block instance and all
        processing blocks associated with it. Any key
        that has the scheduling block instance if is removed
        from the database
        """
        block_instance = self.get_scheduling_block(block_id)
        for i in block_instance:
            self._db.delete(i)

        # Add a event to the scheduling block event list to notify
        # of a deleting a scheduling block from the db
        self._db.rpush('scheduling_block_events',
                       dict(type="deleted", id=block_id))

    def add_status(self, block_data):
        """
        This function adds status key value pair to all the section
        in the scheduling block instance
        """
        block_data['status'] = "created"
        for i in block_data['processing_blocks']:
            i['status'] = 'created'
            i['workflow']['status'] = 'ACTIVE'

    def get_processing_blocks_event(self):
        """Get the latest event added to the scheduling block"""
        event = self._db.rpoplpush('processing_block_events',
                                   'processing_block_event_history')

        # Need to look into more details with this
        # When there is more than one processing blocks in one instance
        if event:
            event = ast.literal_eval(event.decode('utf-8'))
        return event

    def get_schema(self):
        """
        Gets the scheduling block instance schema for validation
        """
        # TODO: (NJT) Need to change how schema is loaded
        with open('schema/scheduling_block_schema.json', 'r') as f:
            schema_top_data = f.read()
        schema = json.loads(schema_top_data)
        return (schema)

    def split_scheduling_block(self, scheduling_block_data):
        """
        Split the scheduling block data into multiple keys 
        before adding to the configuration database
        """
        scheduling_block_key = {}
        processing_key = {}


        for key in scheduling_block_data:
            values = scheduling_block_data[key]
            if key != 'processing_blocks':
                scheduling_block_key[key] = values

            processing_key = scheduling_block_data['processing_blocks']
            # print(len(scheduling_block_data['processing_blocks']))
           # pprint(scheduling_block_data['processing_blocks'][0])
        # for items in scheduling_block_data['processing_blocks']:
        #     for data in items:
        #         if data !='workflow':
        #             processing_values = items[data]
        #
        #
        #
        #             print(processing_values)
        #
        #             processing_key[processing_values] = processing_values
                # if data != 'workflow':
                #     print(data)
        #for items in processing_key:

            # for data in items:
            #     processing_values = items[data]
            #     if data != 'workflows':
            #         processing_key[data] = processing_values

        return scheduling_block_key, processing_key

    def split_init_data(self, init_data):
        """
        Splitting the master controller data into multiple
        keys before adding to the configuration database
        """

        # Experimental - DO NOT DELETE UNTIL YOU ARE SURE
        # flat = flatten(init_data)
        # #pprint(flat)
        # dictlist = []
        # for key, value in flat.items():
        #     temp = key,value
        #     dictlist.append(temp)
        # pprint(dictlist)
        # print(dictlist[0])


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