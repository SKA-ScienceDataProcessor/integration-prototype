# -*- coding: utf-8 -*-
"""High Level Processing Controller Client API"""

import ast
import json
import os

from jsonschema import validate, ValidationError

from .config_db_redis import ConfigDB


class ConfigDbClient:
    """Configuration Database client API for the Processing Controller"""

    def __init__(self):
        self._db = ConfigDB()

        # Initialise Variables
        self.scheduling_event_name = 'scheduling_block_events'
        self.processing_event_name = 'processing_block_events'
        self.scheduling_block_data = {}
        self.processing_block_data = {}

    # #########################################################################
    # Set functions
    # #########################################################################

    def set_scheduling_block(self, scheduling_block):
        """Set scheduling block and processing block to the database"""
        # Get schema for validation
        schema = self._get_schema()
        try:
            # Validates the schema
            validate(scheduling_block, schema)

            json_dump = json.dumps(scheduling_block)
            block_object = json.loads(json_dump)

            # Add status field and value to the data
            updated_block = self._add_status(block_object)

            # Splitting into different names and fields before
            # adding to the database
            self._split_scheduling_block(updated_block)

            # Adding Scheduling block instance with id
            name = ("scheduling_block:" +
                    updated_block["sched_block_instance_id"])
            self._db.set_specified_values(name, self.scheduling_block_data)

            # Add a event to the scheduling block event list to notify
            # of a new scheduling block being added to the db.
            self._db.push_event(self.scheduling_event_name,
                                updated_block["status"],
                                updated_block["sched_block_instance_id"])

            # Adding Processing block with id
            for value in self.processing_block_data:
                name = ("scheduling_block:" +
                        updated_block["sched_block_instance_id"] +
                        ":processing_block" + ":" + value['id'])
                self._db.set_specified_values(name, value)

                # Add a event to the processing block event list to notify
                # of a new processing block being added to the db.
                self._db.push_event(self.processing_event_name, value["status"],
                                    value["id"])
        except ValidationError:
            print("Schema Validation Error")
            raise

    # #########################################################################
    # Get functions
    # #########################################################################

    def get_scheduling_block_ids(self):
        """Get list of scheduling block ids"""
        # Initialise empty list
        scheduling_block_ids = []

        # Pattern used to search scheduling block ids
        pattern = 'scheduling_block:*'

        block_ids = self._db.get_ids(pattern)
        for block_id in block_ids:
            if 'processing_block' not in block_id:
                id_split = block_id.split(':')[-1]
                scheduling_block_ids.append(id_split)
        return scheduling_block_ids

    def get_num_scheduling_block_ids(self):
        """"Get number of scheduling blocks ids"""
        return len(self.get_scheduling_block_ids())

    def get_processing_block_ids(self):
        """Get list of processing block ids using the processing block id"""
        # Initialise empty list
        processing_block_ids = []

        # Pattern used to search processing block ids
        pattern = '*:processing_block:*'

        block_ids = self._db.get_ids(pattern)
        for block_id in block_ids:
            id_split = block_id.split(':')[-1]
            processing_block_ids.append(id_split)
        return processing_block_ids

    def get_num_processing_block_ids(self):
        """"Get number of processing block ids"""
        return len(self.get_processing_block_ids())

    def get_sub_array_ids(self):
        """Get list of sub array ids"""
        # Initialise empty list
        scheduling_block_ids = []
        sub_array_ids = []

        for blocks_id in self.get_scheduling_block_ids():
            scheduling_block_ids.append(blocks_id)
        block_details = self.get_block_details(scheduling_block_ids)
        for details in block_details:
            sub_array_ids.append(details['sub_array_id'])
        return sub_array_ids

    def get_scheduling_block_id_using_sub_array_id(self, sub_array_id):
        """Get scheduling block id (note the instance id) associated with
         sub array id"""
        # Initialise empty list
        scheduling_block_ids = []

        for block_id in self.get_scheduling_block_ids():
            scheduling_block_ids.append(block_id)
        block_details = self.get_block_details(scheduling_block_ids)
        for details in block_details:
            if details['sub_array_id'] == sub_array_id:
                sched_blocks_id = details['sched_block_id']
                return sched_blocks_id

    def get_block_details(self, block_id):
        """Get details of scheduling or processing block"""
        for _id in block_id:
            block_name = self._db.get_block(_id)
            for name in block_name:
                blocks = self._db.get_all_field_value(name)
                yield blocks
        return blocks  # FIXME(BM) blocks can be never assigned!

    def get_latest_event(self, event_block):
        """Get the latest event added"""
        block_event = event_block + '_events'
        block_history = event_block + '_event_history'
        event = self._db.get_event(block_event, block_history)
        return ast.literal_eval(event)

    # #############################################################################
    # Update functions
    # #############################################################################

    def update_value(self, block_id, field, value):
        """"Update the value of the given block id and field"""
        block_name = self._db.get_block(block_id)
        for name in block_name:
            self._db.set_value(name, field, value)

    # #############################################################################
    # Delete functions
    # #############################################################################

    def delete_scheduling_block(self, block_id):
        """Delete the specified Scheduling Block Instance.

        Removes the scheduling block instance and all processing blocks
        associated with it. Any data associated with scheduling block instance
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
            self._db.push_event(self.scheduling_event_name, "deleted", block_id)

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
                    self._db.push_event(self.processing_event_name, "deleted",
                                        processing_id)
        else:
            split_key = processing_block.split(':')
            self._db.delete_block(processing_block)

            # Add a event to the processing block event list to notify
            # about deleting from the db
            self._db.push_event(self.processing_event_name, "deleted",
                                split_key[3])

    # #########################################################################
    # Utility functions
    # #########################################################################
    def clear(self):
        """Clear / drop the entire database."""
        self._db.clear()

    # #########################################################################
    # Private functions
    # #########################################################################

    @staticmethod
    def _get_schema():
        """Get the schema for validation"""
        schema_path = os.path.join(os.path.dirname(__file__),
                                   'schema', 'scheduling_block_schema.json')
        with open(schema_path, 'r') as f:
            schema_data = f.read()
        schema = json.loads(schema_data)
        return schema

    @staticmethod
    def _add_status(scheduling_block):
        """This function adds status fields to all the section
        in the scheduling block instance"""
        scheduling_block['status'] = "created"
        for block in scheduling_block:
            if type(scheduling_block[block]) == list:
                for field in scheduling_block[block]:
                    field['status'] = 'created'
        return scheduling_block

    def _split_scheduling_block(self, scheduling_block):
        """Split the scheduling block data into multiple names
        before adding to the configuration database"""
        for block in scheduling_block:
            values = scheduling_block[block]
            if type(scheduling_block[block]) != list:
                self.scheduling_block_data[block] = values
            else:
                self.processing_block_data = values
