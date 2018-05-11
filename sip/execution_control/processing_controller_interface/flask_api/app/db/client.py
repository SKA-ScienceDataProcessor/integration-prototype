# -*- coding: utf-8 -*-
"""High Level Processing Controller Client API"""

import ast
import json
import logging
import os

from jsonschema import ValidationError, validate

from .config_db_redis import ConfigDB

LOG = logging.getLogger('SIP.PCI.DB')


class ConfigDbClient:
    """Configuration Database client API for the Processing Controller."""

    def __init__(self):
        self._db = ConfigDB()

        # Initialise Variables
        self.scheduling_event_name = 'scheduling_block_events'
        self.processing_event_name = 'processing_block_events'
        self.scheduling_block_data = {}
        self.processing_block_data = {}

    # #########################################################################
    # Add functions
    # #########################################################################

    def add_scheduling_block(self, config_dict):
        """Add Scheduling Block to the database"""
        # Get schema for validation
        schema = self._get_schema()
        LOG.debug('Adding SBI with config: %s', config_dict)
        try:
            # Validates the schema
            validate(config_dict, schema)

            # FIXME(BM) These two lines seem redundant!?
            json_dump = json.dumps(config_dict)
            block_object = json.loads(json_dump)

            # Add status field and value to the data
            updated_block = self._add_status(block_object)

            # Splitting into different names and fields before
            # adding to the database
            self._split_scheduling_block(updated_block)

            # Adding Scheduling block instance with id
            name = "scheduling_block:" + updated_block["id"]
            self._db.set_specified_values(name, self.scheduling_block_data)

            # Add a event to the scheduling block event list to notify
            # of a new scheduling block being added to the db.
            self._db.push_event(self.scheduling_event_name,
                                updated_block["status"],
                                updated_block["id"])

            # Adding Processing block with id
            for value in self.processing_block_data:
                name = ("scheduling_block:" + updated_block["id"] +
                        ":processing_block:" + value['id'])
                self._db.set_specified_values(name, value)

                # Add a event to the processing block event list to notify
                # of a new processing block being added to the db.
                self._db.push_event(self.processing_event_name, value["status"],
                                    value["id"])
        except ValidationError:
            print("Schema Validation Error")
            raise

    # ##########################################################################
    # Get functions
    # ##########################################################################

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
        _processing_block_ids = []

        # Pattern used to search processing block ids
        pattern = '*:processing_block:*'
        block_ids = self._db.get_ids(pattern)

        for block_id in block_ids:
            id_split = block_id.split(':')[-1]
            _processing_block_ids.append(id_split)
        return _processing_block_ids

    def get_num_processing_block_ids(self):
        """"Get number of processing block ids"""
        return len(self.get_processing_block_ids())

    def get_sub_array_ids(self):
        """Get list of sub array ids"""
        # Initialise empty list
        _scheduling_block_ids = []
        _sub_array_ids = []

        for blocks_id in self.get_scheduling_block_ids():
            _scheduling_block_ids.append(blocks_id)
        block_details = self.get_block_details(_scheduling_block_ids)
        for details in block_details:
            _sub_array_ids.append(details['sub_array_id'])
        return _sub_array_ids

    def get_scheduling_block_id_using_sub_array_id(self, sub_array_id):
        """Get Scheduling Block Instance ID associated with sub array id"""

        _scheduling_block_ids = []

        for block_id in self.get_scheduling_block_ids():
            _scheduling_block_ids.append(block_id)
        block_details = self.get_block_details(_scheduling_block_ids)

        for details in block_details:
            if details['sub_array_id'] == sub_array_id:
                return details['id']

    def get_sub_array_scheduling_block_ids(self, sub_array_id):
        """Get scheduling block ids for associated with the given sub array"""
        _ids = []
        for block in self.get_block_details(self.get_scheduling_block_ids()):
            if block['sub_array_id'] == sub_array_id:
                _ids.append(block['id'])
        return _ids

    def get_block_details(self, block_id):
        """Get details of scheduling or processing block

        Args:
            block_id (list): List of block IDs
        """
        # Check for any duplicates
        block_ids = set([x for x in block_id if block_id.count(x) > 0])
        block_ids = sorted(block_ids)

        for _id in block_ids:
            block_key = self._db.get_block(_id)[0]
            block_data = self._db.get_all_field_value(block_key)
            # FIXME(BM) unfortunately this doesnt quite work for keys where
            # the value is an object. eg. processing_blocks.
            # The following hack seems to work but is probably not infallible
            for key in block_data:
                for char in ['[', '{']:
                    if char in block_data[key]:
                        block_data[key] = ast.literal_eval(str(block_data[key]))
            yield block_data

    def get_latest_event(self, event_block):
        """Get the latest event added"""
        block_event = event_block + '_events'
        block_history = event_block + '_event_history'
        event = self._db.get_event(block_event, block_history)
        return ast.literal_eval(event)

    # #########################################################################
    # Update functions
    # #########################################################################

    def update_value(self, block_id, field, value):
        """"Update the value of the given block id and field"""
        block_name = self._db.get_block(block_id)
        for name in block_name:
            self._db.set_value(name, field, value)

    # #########################################################################
    # Delete functions
    # #########################################################################

    def delete_scheduling_block(self, block_id):
        """Delete the specified Scheduling Block Instance.

        Removes the Scheduling Block Instance, and all Processing Blocks
        that belong to it from the database"""
        scheduling_blocks = self._db.get_all_blocks(block_id)
        if scheduling_blocks:
            for blocks in scheduling_blocks:
                if "processing_block" not in blocks:
                    self._db.delete_block(blocks)
                else:
                    self.delete_processing_block(blocks)
                    split_key = blocks.split(':')
                    self._db.delete_block(blocks)

                    # Add a event to the processing block event list to notify
                    # about deleting from the db
                    self._db.push_event(self.processing_event_name, "deleted",
                                        split_key[3])

            # Add a event to the scheduling block event list to notify
            # of a deleting a scheduling block from the db
            self._db.push_event(self.scheduling_event_name, "deleted", block_id)

    def delete_processing_blocks(self, processing_block_ids):
        """Delete Processing Block(s).

        Uses Processing Block IDs and Scheduling Block IDs if given.
        """
        for _id in processing_block_ids:
            processing_blocks = self._db.get_block(_id)
            for blocks in processing_blocks:
                if 'processing_block' in blocks:
                    self._db.delete_block(blocks)
                    # Add a event to the processing block event list to notify
                    # about deleting from the db
                    self._db.push_event(self.processing_event_name,
                                        "deleted", _id)

    # #########################################################################
    # Utility functions
    # #########################################################################

    def clear(self):
        """Clear / drop the entire database."""
        self._db.flush_db()

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
        _processing_block_id = []
        for block in scheduling_block:
            values = scheduling_block[block]
            if type(scheduling_block[block]) != list:
                self.scheduling_block_data[block] = values
            else:
                # Check if there is a processing block that already exits in
                # the database
                processing_block_id = self.get_processing_block_ids()
                for v in values:
                    if v['id'] not in processing_block_id:
                        self.processing_block_data = values
                    else:
                        raise RuntimeError("Processing block already exits",
                                           v['id'])

        # Adding processing block id to the scheduling block list
        for block_id in self.processing_block_data:
            _processing_block_id.append(block_id['id'])

        self.scheduling_block_data['processing_blocks'] = _processing_block_id
