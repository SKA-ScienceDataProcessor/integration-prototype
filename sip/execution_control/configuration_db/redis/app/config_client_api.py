# -*- coding: utf-8 -*-
""" Client API"""

import redis
import json
from jsonschema import validate
from pprint import pprint
import os
import ast


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

    def set_master_controller(self):
        """
        Add master controller initial data to the configuration database
        """
        print("Add initial data")

    def set_schedule_block_instance(self, scheduling_block_instance):
        """
        Set scheduling block instance
        This includes adding the processing blocks and each of of its stages
        """
        scheduling_block_schema = self.get_schema()

        try:
            # Validates the schema
            validate(scheduling_block_instance, scheduling_block_schema)
        except:
            print("Validation Error - Schema")

        # Add status
        self.add_status(scheduling_block_instance)

        # Splitting the data into different keys before adding
        # to the database
        scheduling_block_key, processing_key = self.parse_data(scheduling_block_instance)
        # Adding Scheduling block instance with id
        instance_key = "schedule_block_instance:" + \
                       scheduling_block_instance["sched_block_instance_id"]
        self._db.hmset(instance_key, scheduling_block_key)

        # Add a event to the scheduling block event list to notify
        # of a new scheduling block being added to the db.
        self._db.rpush('scheduling_block_events', dict(
            type=scheduling_block_instance["status"],
            id=scheduling_block_instance["sched_block_instance_id"]))

        # # Adding Processing blocks instance with id
        # for key in processing_key:
        #     processing_key = "schedule_block_instance:" + \
        #                      scheduling_block_data["sched_block_instance_id"] + \
        #                      ":" + key["id"]
        #     self._db.hmset(processing_key, key)
        #
        #     # Add a event to the processing block event list to notify
        #     # of a new processing block being added to the db.
        #     self._db.rpush('processing_block_events', dict(
        #         type=key["status"],
        #         id=key["id"]))

    def get_scheduling_block_event(self):
        """
        Get the latest event added to the scheduling block
        """
        event = self._db.rpoplpush('scheduling_block_events',
                                   'scheduling_block_event_history')
        if event:
            event = ast.literal_eval(event.decode('utf-8'))
        return (event)

    # def get_scheduling_block(self, block_id):
    #     """Return the Scheduling Block configuration for a specified ID"""
    #     config = self._db.get('scheduling_block/{}'.format(block_id))
    #
    #     print(ast.literal_eval(config.decode('utf-8')))
    #     return ast.literal_eval(config.decode('utf-8'))


    def get_scheduling_block(self, block_id):
        """Get scheduling bock instance for the
        configuration database"""
        instance_search = '*' + block_id
        scheduling_block_key = self._db.keys(instance_search)
        return scheduling_block_key

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

            # Remove the resource requirement
            i['resources_requirement']['status'] = 'ACTIVE'
            i['workflow']['status'] = 'ACTIVE'

            # Dont require any of these for the time being
            # for j in i['workflow']['stages']:
            #     j['status'] = 'ACTIVE'
            #     j['processing_stage']['status'] = 'ACTIVE'
            #     j['service_stage']['status'] = 'ACTIVE'
            #     j['dependency']['status'] = 'ACTIVE'
            #     j['processing_stage']['processing_component']['status'] =\
            #         'ACTIVE'
            #     j['processing_stage']['execution_engine']['status'] = 'ACTIVE'
        # pprint(data)

    def get_processing_blocks_event(self):
        """Get the latest event added to the scheduling block"""
        event = self._db.rpoplpush('processing_block_events',
                                   'processing_block_event_history')

        # Need to look into more details with this
        # When there is more than one processing blocks in one instance
        if event:
            event = ast.literal_eval(event.decode('utf-8'))
        return event

    #
    # def get_status(self):
    #     print("Get Status")
    #
    # def update_status(self, sched_blk_inst_id, sched_blk_inst_status=None,
    #                   process_blk_id=None, process_blk_status=None, stage=None):
    #     """
    #     This function updates the status of the scheduling block or
    #     processing block or both
    #     """
    #     if process_blk_id != None:
    #         # Updates the status either the processing blocks or stages inside
    #         # the processing blocks
    #         if stage != None:
    #             process_blk_key = self.get_scheduling_block_instance(
    #                 sched_blk_inst_id, process_blk_id, False)
    #             for i in process_blk_key:
    #                 workflow = self._server.hget(i, "workflow")
    #                 workflow_eval = eval(workflow)
    #                 pprint(workflow_eval)
    #                 for j in workflow_eval['stages']:
    #                     j[stage]['status'] = process_blk_status
    #                 pprint(workflow_eval)
    #                 join = {"workflow": workflow_eval}
    #                 self._server.hmset(i, join)
    #
    #                 # This is not good as it updates the full key
    #                 # If the status of the processing stage is updated then it
    #                 # needs to remain
    #                 # One way to do is to split the stages maybe into a different key
    #                 # or same them as a list in a key -> Look into this
    #
    #
    #
    #
    #
    #
    #         else:
    #             process_blk_key = self.get_scheduling_block_instance(
    #                 sched_blk_inst_id, process_blk_id, False)
    #             for i in process_blk_key:
    #                 self._server.hmset(i, {'status': process_blk_status})
    #     else:
    #         # Updates the status of the scheduling block instance
    #         sched_blk_key = self.get_scheduling_block_instance(
    #             sched_blk_inst_id, True)
    #         for i in sched_blk_key:
    #             self._server.hmset(i, {'status': sched_blk_inst_status})
    #
    # def set_resouces(self):
    #     print("Set assigned resources")
    #

    #
    # # def get_processing_blocks(self, sched_bl_instance_id, proc_block_id):
    # #     """Get processing blocks for a specified
    # #     scheduling block instance by ID"""
    # #
    # #     # Searching for processing block associated with
    # #     # the scheduling instance
    # #     for i in scheduling_block_instance_key:
    # #         for p in proc_block_id:
    # #             if p in i.decode():
    # #                 print("Processing Blocks - ", p)
    #

    #
    def get_schema(self):
        """
        Gets the scheduling block instance schema for validation
        """
        with open('schema/scheduling_block_instance_schema.json', 'r') as f:
            schema_top_data = f.read()
        schema = json.loads(schema_top_data)
        return (schema)

    def parse_data(self, scheduling_block_data):
        """Parse the schema before adding to the
        database"""
        scheduling_block_key = {}
        processing_key = []

        for key in scheduling_block_data:
            values = scheduling_block_data[key]

            # Need to add processing block id
            if key != 'processing_blocks':
                scheduling_block_key[values] = values

            processing_key = scheduling_block_data['processing_blocks']

        # print("Processsing Key !!!!!!!")
        # print(processing_key)

        #
        # for proc_data in data:
        #     processing_key = data['processing_blocks']
        #
        # for x in processing_key:
        #     processing_key = "schedule_block_instance:" + data["sched_block_instance_id"] +\
        #                          ":" + x["id"]
        #     self._server.hmset(processing_key, x)
        #
        #     Need to think about if the having a different for the stages is useful or not
        #     Currently put on hold
        #
        #     for stages in x['workflow']['stages']:
        #         stages_key = stages
        #         print(stages_key)
        #
        #         stage_key = "schedule_block_instance:" + data["sched_block_instance_id"] +\
        #                          ":" + x["id"] + ":" +

        return scheduling_block_key, processing_key