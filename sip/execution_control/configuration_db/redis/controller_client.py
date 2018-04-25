# -*- coding: utf-8 -*-
"""High Level Processing Controller Client API"""

import json
import ast
from jsonschema import validate
from config_db import configDB

class controllerClient():
    """ Processing Controller Client Interface"""
    def __init__(self):
        print("Controller Client")
        self._db = configDB()

    def get_schema(self):
        """Get the schema for validation"""
        with open('schema/scheduling_block_schema.json', 'r') as f:
            schema_data = f.read()
        schema = json.loads(schema_data)
        return schema

    def set_scheduling_block(self, scheduling_block):
        """Set scheduling block and processing block to the database"""
        # Get schema for validation
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

        # Splitting into different names and fields before
        # adding to the database
        scheduling_blk, processing_blk = self.split_scheduling_block(
            updated_block)

        # Adding Scheduling block instance with id
        block_name = "scheduling_block_instance:" + \
                       updated_block["sched_block_instance_id"]

        self._db.set_hm_value(block_name, scheduling_blk)

        # Add a event to the scheduling block event list to notify
        # of a new scheduling block being added to the db.
        scheduling_event_name = 'scheduling_block_events'
        self._db.push_event(scheduling_event_name, updated_block["status"],
                            updated_block["sched_block_instance_id"])

        # Adding Processing block with id
        for value in processing_blk:
            processing_name = "scheduling_block_instance:" + \
                             updated_block["sched_block_instance_id"] + \
                             ":processing_block" + ":" + value['id']
            # self._db.hmset(processing_name, value)
            self._db.set_hm_value(processing_name, value)

            # Add a event to the processing block event list to notify
            # of a new processing block being added to the db.
            processing_event_name = 'processing_block_events'
            self._db.push_event(processing_event_name, value["status"],
                                value["id"])

    def get_scheduling_block(self, block_id):
        print("Placeholder")

    def get_processing_block(self):
        print("Placeholder")

    def get_latest_event(self, event_block):
        """Get the latest event added"""
        block_event = event_block + '_events'
        block_history = event_block + '_event_history'
        event = self._db.get_event(block_event, block_history)
        return ast.literal_eval(event)

    def update_status(self):
        print("Placeholder")


    def delete_scheduling_block(self, block_id):
        """Removes the scheduling block instance and all processing blocks
        associated with it. Any data associated withscheduling block instance
        is removed from the database"""
        scheduling_blocks = self._db.get_all_blocks(block_id)
        if scheduling_blocks:
            for blocks in scheduling_blocks:
                if "processing_block" not in blocks:
                    self._db.delete_block(blocks)
                else:
                    self.delete_processing_block(blocks)

            # Add a event to the scheduling block event list to notify
            # of a deleting a scheduling block from the db
            self._db.push_event('scheduling_block_events',"deleted", block_id)

    def delete_processing_block(self, processing_block):
        """Delete processing block using processing block id
        and using scheduling block id if given"""
        if type(processing_block) is list:
            for processing_id in processing_block:
                processing_blocks = self._db.get_block(processing_id)
                for blocks in processing_blocks:
                    self._db.delete_block(blocks)

                    # Add a event to the processing block event list to notify
                    # about deleting from the db
                    processing_event_name = 'processing_block_events'
                    self._db.push_event(processing_event_name, "deleted",
                                        processing_id)
        else:
            split_key = processing_block.split(':')
            self._db.delete_block(processing_block)

            # Add a event to the processing block event list to notify
            # about deleting from the db
            processing_event_name = 'processing_block_events'
            self._db.push_event(processing_event_name, "deleted",split_key[3])

    def add_status(self, scheduling_block):
        """This function adds status fields to all the section
        in the scheduling block instance"""
        scheduling_block['status'] = "created"
        for block in scheduling_block:
            # print(type(scheduling_block[block]))
            if type(scheduling_block[block]) == list:
                for p in scheduling_block[block]:
                    p['status'] = 'created'
        return scheduling_block

    def split_scheduling_block(self, scheduling_block):
        """Split the scheduling block data into multiple names
        before adding to the configuration database"""
        scheduling_blk = {}
        processing_blk = {}
        for block in scheduling_block:
            values = scheduling_block[block]
            if type(scheduling_block[block]) != list:
                scheduling_blk[block] = values
            else:
                processing_blk = values
        return scheduling_blk, processing_blk
