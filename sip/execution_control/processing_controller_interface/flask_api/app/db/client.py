# -*- coding: utf-8 -*-
"""High Level Processing Controller Client API"""

import ast
import json
import logging
import os

from jsonschema import validate

from .config_db_redis import ConfigDB


LOG = logging.getLogger('SIP.EC.PCI.DB')


class ConfigDb:
    """Configuration Database client API for the Processing Controller."""

    def __init__(self):
        self._db = ConfigDB()

        # Initialise Variables
        self.scheduling_event_name = 'scheduling_block_events'
        self.processing_event_name = 'processing_block_events'

    ###########################################################################
    # Add functions
    ###########################################################################

    def add_sched_block_instance(self, config_dict):
        """Add Scheduling Block to the database.

        Args:
            config_dict (dict): SBI configuration

        """
        # Get schema for validation
        schema = self._get_schema()
        LOG.debug('Adding SBI with config: %s', config_dict)

        # Validates the schema
        validate(config_dict, schema)

        # Add status field and value to the data
        updated_block = self._add_status(config_dict)

        # Splitting into different names and fields before
        # adding to the database
        scheduling_block_data, processing_block_data = \
            self._split_sched_block_instance(updated_block)

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
                                value["status"],
                                value["id"])

    # #########################################################################
    # Get functions
    # #########################################################################

    def get_sched_block_instance_ids(self):
        """Get unordered list of scheduling block ids"""

        # Initialise empty list
        scheduling_block_ids = []

        # Pattern used to search scheduling block ids
        pattern = 'scheduling_block:*'
        block_ids = self._db.get_ids(pattern)

        for block_id in block_ids:
            if 'processing_block' not in block_id:
                id_split = block_id.split(':')[-1]
                scheduling_block_ids.append(id_split)
        return sorted(scheduling_block_ids)

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
        return sorted(_processing_block_ids)

    def get_num_processing_block_ids(self):
        """"Get number of processing block ids"""
        return len(self.get_processing_block_ids())

    def get_sub_array_ids(self):
        """Get list of sub array ids"""

        # Initialise empty list
        _scheduling_block_ids = []
        _sub_array_ids = []

        for blocks_id in self.get_sched_block_instance_ids():
            _scheduling_block_ids.append(blocks_id)
        block_details = self.get_block_details(_scheduling_block_ids)
        for details in block_details:
            _sub_array_ids.append(details['sub_array_id'])
        _sub_array_ids = sorted(list(set(_sub_array_ids)))
        return _sub_array_ids

    def get_sub_array_sbi_ids(self, sub_array_id):
        """Get Scheduling Block Instance ID associated with sub array id"""
        _ids = []
        sbi_ids = self.get_sched_block_instance_ids()
        for details in self.get_block_details(sbi_ids):
            if details['sub_array_id'] == sub_array_id:
                _ids.append(details['id'])
        return sorted(_ids)

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

    def delete_sched_block_instance(self, block_id):
        """Delete the specified Scheduling Block Instance.

        Removes the Scheduling Block Instance, and all Processing Blocks
        that belong to it from the database"""
        LOG.debug('Deleting SBI %s', block_id)

        scheduling_blocks = self._db.get_all_blocks(block_id)
        if not scheduling_blocks:
            raise RuntimeError('Scheduling block not found: {}'.
                               format(block_id))

        if scheduling_blocks:
            for blocks in scheduling_blocks:
                if "processing_block" not in blocks:
                    self._db.delete_block(blocks)
                else:
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

    def delete_processing_block(self, processing_block_id):
        """Delete Processing Block(s).

        Uses Processing Block IDs
        """
        LOG.debug("Deleting Processing Block %s ...", processing_block_id)
        processing_block = self._db.get_block(processing_block_id)
        if not processing_block:
            raise RuntimeError('Invalid Processing Block ID: {}'
                               .format(processing_block_id))

        for block in processing_block:
            if 'processing_block' in block:
                self._db.delete_block(block)

                # Remove processing block id from scheduling block id
                scheduling_block_id = block.split(':')
                scheduling_block_details = self.get_block_details(
                    [scheduling_block_id[1]])
                for block_details in scheduling_block_details:
                    block_list = block_details['processing_block_ids']
                    if processing_block_id in block_list:
                        block_list.remove(processing_block_id)
                    self.update_value(scheduling_block_id[1],
                                      'processing_block_ids', block_list)

                # Add a event to the processing block event list to notify
                # about deleting from the db
                self._db.push_event(self.processing_event_name, "deleted",
                                    id)

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
        with open(schema_path, 'r') as file:
            schema_data = file.read()
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

    def _split_sched_block_instance(self, scheduling_block):
        """Split the scheduling block data into multiple names
        before adding to the configuration database"""

        # Initialise empty list
        _scheduling_block_data = {}
        _processing_block_data = {}
        _processing_block_id = []

        for block in scheduling_block:
            values = scheduling_block[block]

            if block != 'processing_blocks':
                _scheduling_block_data[block] = values
            else:
                # Check if there is a processing block that already exits in
                # the database
                processing_block_id = self.get_processing_block_ids()

                for value in values:
                    if value['id'] not in processing_block_id:
                        _processing_block_data = values
                    else:
                        raise Exception("Processing block already exits",
                                        value['id'])

        # Adding processing block id to the scheduling block list
        for block_id in _processing_block_data:
            _processing_block_id.append(block_id['id'])
        _scheduling_block_data['processing_block_ids'] = _processing_block_id

        return _scheduling_block_data, _processing_block_data
