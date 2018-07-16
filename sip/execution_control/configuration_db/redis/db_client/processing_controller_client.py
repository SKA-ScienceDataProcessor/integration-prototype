# -*- coding: utf-8 -*-
"""High Level Processing Controller Client API."""
import ast
import json
import logging
import os
import datetime

from jsonschema import ValidationError, validate

from .config_db_redis import ConfigDbRedis


LOG = logging.getLogger('SIP.EC.CDB')


class ProcessingControllerDbClient:
    """Configuration Database client API for the Processing Controller."""

    def __init__(self):
        """Initialise the client."""
        self._db = ConfigDbRedis()
        self.scheduling_event_name = 'scheduling_block_events'
        self.processing_event_name = 'processing_block_events'

    ###########################################################################
    # Add functions
    ###########################################################################

    def add_scheduling_block(self, config_dict):
        """Add Scheduling Block to the database.

        Args:
            config_dict (dict): SBI configuration dictionary.

        Raises:
            jsonschema.ValidationError, if the SBI configuration is invalid.
            Exception, if ??

        """
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
            self._db.set_hash_values(name, scheduling_block_data)

            # Add a event to the scheduling block event list to notify
            # of a new scheduling block being added to the db.
            self._db.push_event(self.scheduling_event_name,
                                updated_block["status"],
                                updated_block["id"])

            # Adding Processing block with id
            for value in processing_block_data:
                name = ("scheduling_block:" + updated_block["id"] +
                        ":processing_block:" + value['id'])
                self._db.set_hash_values(name, value)

                # Add a event to the processing block event list to notify
                # of a new processing block being added to the db.
                self._db.push_event(self.processing_event_name,
                                    value["status"],
                                    value["id"])
        except ValidationError:
            raise

    # #########################################################################
    # Get functions
    # #########################################################################

    def get_sbi_id(self, date=None, project='sip'):
        """Return a Scheduling Block Instance ID string.

        Args:
            date (str or datetime, optional): Date of the Scheduling Block
                                              Instance, if not specified use
                                              current date.
            project (str, optional): Project

        Returns:
            str, A valid Scheduling Block Instance ID.

        """
        if date is None:
            date = datetime.datetime.utcnow()

        if isinstance(date, str):
            _date = date
        elif isinstance(date, datetime.datetime):
            _date = date.strftime('%Y%m%d')
        else:
            raise RuntimeError('Unknown date type.')

        sbi_index = self.get_num_scheduling_blocks()
        return '{}-{}-sbi{:03d}'.format(_date, project, sbi_index)

    def get_scheduling_block_ids(self):
        """Get the sorted list of Scheduling Block Instance ids.

        Returns:
            list, All Scheduling Block Instance IDs in the database

        """
        scheduling_block_ids = []

        # Pattern used to search scheduling block ids
        pattern = 'scheduling_block:*'
        block_ids = self._db.get_keys(pattern)

        for block_id in block_ids:
            if 'processing_block' not in block_id:
                id_split = block_id.split(':')[-1]
                scheduling_block_ids.append(id_split)
        return sorted(scheduling_block_ids)

    def get_num_scheduling_blocks(self):
        """Get the number of Scheduling Blocks Instance ids in the database.

        Returns:
            int, The number of Scheduling Block Instance IDs

        """
        return len(self.get_scheduling_block_ids())

    def get_processing_block_ids(self):
        """Get the sorted list of Processing Block ids.

        Returns:
            list, All Processing Block IDs in the database

        """
        _processing_block_ids = []

        # Pattern used to search processing block ids
        pattern = '*:processing_block:*'
        block_ids = self._db.get_keys(pattern)

        for block_id in block_ids:
            id_split = block_id.split(':')[-1]
            _processing_block_ids.append(id_split)
        return sorted(_processing_block_ids)

    def get_num_processing_blocks(self):
        """Get number of processing block ids."""
        return len(self.get_processing_block_ids())

    def get_sub_array_ids(self):
        """Get list of sub array ids."""
        # Initialise empty list
        _scheduling_block_ids = []
        _sub_array_ids = []

        for blocks_id in self.get_scheduling_block_ids():
            _scheduling_block_ids.append(blocks_id)
        block_details = self.get_block_details(_scheduling_block_ids)
        for details in block_details:
            _sub_array_ids.append(details['sub_array_id'])
        _sub_array_ids = sorted(list(set(_sub_array_ids)))
        return _sub_array_ids

    def get_sub_array_sbi_ids(self, sub_array_id):
        """Get Scheduling Block Instance ID associated with sub array id."""
        _ids = []
        for details in self.get_block_details(self.get_scheduling_block_ids()):
            if details['sub_array_id'] == sub_array_id:
                _ids.append(details['id'])
        return _ids

    def get_block_details(self, block_ids):
        """Get the details of a Scheduling or Processing block.

        Args:
            block_ids (list): List of block IDs

        Returns:
            generator?!

        """
        # Convert input to list, if needed
        if not isinstance(block_ids, (list, tuple)):
            block_ids = [block_ids]

        for _id in block_ids:
            block_key = self._db.get_block(_id)[0]
            block_data = self._db.get_hash_dict(block_key)
            # NOTE(BM) unfortunately the following hack doesn't quite work \
            # for keys where the value is a Python object (list, dict etc.) \
            # but is good enough for now where objects are stored as strings.
            for key in block_data:
                for char in ['[', '{']:
                    if char in block_data[key]:
                        block_data[key] = ast.literal_eval(
                            str(block_data[key]))
            yield block_data

    def get_latest_event(self, event_class):
        """Get the latest event added.

        Args:
            event_class (str): Class of event, either 'processing_block' or
                               'scheduling_block'

        Returns:
            dict, event data.

        Raises:
            Keyerror, if an invalid event class is specified.

        """
        if event_class not in ('processing_block', 'scheduling_block'):
            raise KeyError('Invalid event class')
        block_event = event_class + '_events'
        block_history = event_class + '_event_history'
        event = self._db.get_event(block_event, block_history)
        return ast.literal_eval(event)

    # #########################################################################
    # Update functions
    # #########################################################################

    def update_value(self, block_id, field, value):
        """Update the value of the given block id and field."""
        block_name = self._db.get_block(block_id)
        for name in block_name:
            self._db.set_hash_value(name, field, value)

    # #########################################################################
    # Delete functions
    # #########################################################################

    def delete_scheduling_block(self, block_id):
        """Delete the specified Scheduling Block Instance.

        Removes the Scheduling Block Instance, and all Processing Blocks
        that belong to it from the database.

        Args:
            block_id (str): Scheduling Block ID

        Raises:
            KeyError: If the specified block_id is not found.

        """
        LOG.debug('Deleting SBI %s', block_id)
        scheduling_blocks = self._db.get_all_blocks(block_id)

        if not scheduling_blocks:
            raise KeyError('Scheduling Block Instance not found: {}'
                           .format(block_id))

        if scheduling_blocks:
            for blocks in scheduling_blocks:
                if "processing_block" not in blocks:
                    self._db.delete_key(blocks)
                else:
                    split_key = blocks.split(':')
                    self._db.delete_key(blocks)

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

        Args:
            processing_block_id (str): Processing Block ID

        Raises:
            KeyError if the specified processing_block_id is not found.

        """
        LOG.debug('Deleting Processing Block %s', processing_block_id)
        processing_block = self._db.get_block(processing_block_id)

        if not processing_block:
            raise KeyError('Processing Block not found: {}'
                           .format(processing_block_id))

        for block in processing_block:
            if 'processing_block' in block:
                self._db.delete_key(block)

                # Remove processing block id from scheduling block id
                scheduling_block_id = block.split(':')
                scheduling_block_details = self.get_block_details(
                    [scheduling_block_id[1]])
                for block_details in scheduling_block_details:
                    block_list = block_details['processing_blocks']
                    if processing_block_id in block_list:
                        block_list.remove(processing_block_id)
                    self.update_value(scheduling_block_id[1],
                                      'processing_blocks', block_list)

                # Add a event to the processing block event list to notify
                # about deleting from the db
                self._db.push_event(self.processing_event_name, "deleted",
                                    processing_block_id)

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
        """Get the schema for validation."""
        schema_path = os.path.join(os.path.dirname(__file__),
                                   'schema', 'scheduling_block_schema.json')
        with open(schema_path, 'r') as file:
            schema_data = file.read()
        schema = json.loads(schema_data)
        return schema

    @staticmethod
    def _add_status(scheduling_block):
        """Add status fields to all sections in the SBI."""
        scheduling_block['status'] = "created"
        for block in scheduling_block:
            if isinstance(scheduling_block[block], list):
                for field in scheduling_block[block]:
                    field['status'] = 'created'
        return scheduling_block

    def _split_scheduling_block(self, scheduling_block):
        """Split the scheduling block data into multiple names.

        Args:
            scheduling_block: ??

        Returns:
            ??

        Raises:
            Exception: ???

        """
        # Initialise empty list
        _scheduling_block_data = {}
        _processing_block_data = {}
        _processing_block_id = []

        for block in scheduling_block:
            values = scheduling_block[block]

            if block != 'processing_blocks':
                _scheduling_block_data[block] = values
            else:
                # Check if there is a processing block that already exists in
                # the database
                processing_block_id = self.get_processing_block_ids()

                for value in values:
                    if value['id'] not in processing_block_id:
                        _processing_block_data = values
                    else:
                        raise Exception("Processing block already exists: {}"
                                        .format(value['id']))

        # Adding processing block id to the scheduling block list
        for block_id in _processing_block_data:
            _processing_block_id.append(block_id['id'])
        _scheduling_block_data['processing_blocks'] = _processing_block_id

        return _scheduling_block_data, _processing_block_data
