# -*- coding: utf-8 -*-
"""High Level Processing Controller Client API"""

import ast
import json
import logging
import os
from collections import Counter
from copy import copy

from jsonschema import ValidationError, validate

from .config_db_redis import ConfigDB

LOG = logging.getLogger('SIP.EC.PCI.CDB')


class ConfigDbClient:
    """Configuration Database client API for the Processing Controller."""

    def __init__(self):
        self._db = ConfigDB()

        # Initialise Variables
        self.scheduling_event_name = 'scheduling_block_events'
        self.processing_event_name = 'processing_block_events'

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

            # Add status field and value to the data
            updated_block = self._add_status(config_dict)

            # Splitting into different names and fields before
            # adding to the database
            scheduling_block_data, processing_block_data = \
                self._split_scheduling_block(updated_block)

            # Adding Scheduling block instance with id
            name = "scheduling_block:" + updated_block["id"]
            self._db.set_specified_values(name, scheduling_block_data)

            # Add a event to the scheduling block event list to notify
            # of a new scheduling block being added to the db.
            self._db.push_event(self.scheduling_event_name,
                                updated_block["status"],
                                updated_block["id"])

            # Adding Processing block with id
            for value in processing_block_data:
                name = ("scheduling_block:" + updated_block["id"] +
                        ":processing_block:" + value['id'])
                self._db.set_specified_values(name, value)

                # Add a event to the processing block event list to notify
                # of a new processing block being added to the db.
                self._db.push_event(self.processing_event_name,
                                    value["status"], value["id"])
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
        _sub_array_ids = set()
        for block in self.get_block_details(self.get_scheduling_block_ids()):
            _sub_array_ids.add(block['sub_array_id'])
        return list(_sub_array_ids)

    def get_sub_array_sbi_ids(self, sub_array_id):
        """Get scheduling block ids for associated with the given sub-array"""
        _ids = []
        for block in self.get_block_details(self.get_scheduling_block_ids()):
            if block['sub_array_id'] == sub_array_id:
                _ids.append(block['id'])
        return _ids

    def get_block_details(self, block_ids):
        """Get details of scheduling or processing block

        Args:
            block_ids (list): List of block IDs
        """
        # Convert input to list if needed
        if not hasattr(block_ids, "__iter__"):
            block_ids = [block_ids]

        for _id in block_ids:
            block_key = self._db.get_block(_id)[0]
            block_data = self._db.get_all_field_value(block_key)
            # NOTE(BM) unfortunately this doesn't quite work for keys where \
            # the value is a python type (list, dict etc) \
            # The following hack works for now but is probably not infallible
            for key in block_data:
                for char in ['[', '{']:
                    if char in block_data[key]:
                        block_data[key] = ast.literal_eval(
                            str(block_data[key]))
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
                    # self.delete_processing_blocks(blocks)
                    split_key = blocks.split(':')
                    self._db.delete_block(blocks)

                    # Add a event to the processing block event list to notify
                    # about deleting from the db
                    self._db.push_event(self.processing_event_name, "deleted",
                                        split_key[3])

            # Add a event to the scheduling block event list to notify
            # of a deleting a scheduling block from the db
            self._db.push_event(self.scheduling_event_name, "deleted",
                                block_id)

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
        with open(schema_path, 'r') as file_handle:
            schema_data = file_handle.read()
        schema = json.loads(schema_data)
        return schema

    @staticmethod
    def _add_status(scheduling_block):
        """This function adds status fields to all the section
        in the scheduling block instance"""
        scheduling_block['status'] = "created"
        for block in scheduling_block:
            if isinstance(scheduling_block[block], list):
                for field in scheduling_block[block]:
                    field['status'] = 'created'
        return scheduling_block

    @staticmethod
    def _get_duplicates(values):
        """Return a list of any duplicates found in the specified list

        Args:
            values (list): List of values to search for duplicates
        """
        return [value for value, count in Counter(values).items() if count > 1]

    def _split_scheduling_block(self, config):
        """Generate internal representation of an SBI configuration dict.

        Generate a Scheduling Block Instance Configuration dictionary
        suitable for storing in the database.

        Args:
            config (dict): Scheduling Block Instance configuration dictionary.
        """
        LOG.debug('Generating internal (DB) SBI representation.')

        # Get list of Processing Block id's in the SBI
        pb_ids = [block['id'] for block in config['processing_blocks']]

        # Check for duplicate PB ids in SBI configuration.
        duplicates = self._get_duplicates(pb_ids)
        if duplicates:
            raise RuntimeError("Duplicate Processing Block ID's {} found in "
                               "new Scheduling Block Instance config.".
                               format(duplicates))

        # Check for duplicates of PB ids with PBs already in the DB
        known_pb_ids = self.get_processing_block_ids()
        duplicates = self._get_duplicates(pb_ids + known_pb_ids)
        if duplicates:
            raise RuntimeError("Processing Block ID's {} already in the "
                               "database.".format(duplicates))

        # Save a copy of the internal SBI configuration and PB configuration
        # as variables on the instance of this class in order that they can
        # be later added to the database using the `set_specified_values()`
        # method.
        scheduling_block_config = copy(config)
        scheduling_block_config['processing_block_ids'] = pb_ids
        del scheduling_block_config['processing_blocks']
        processing_block_config = config['processing_blocks']

        return scheduling_block_config, processing_block_config
