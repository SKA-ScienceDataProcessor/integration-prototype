# -*- coding: utf-8 -*-
"""High Level Scheduling Block Instance Client API."""
import logging
import json
import os
import ast
import datetime

from jsonschema import validate
from db_client import ConfigDb
from db_client import ProcessingControllerDbClient
from db_client import ProcessingBlockDbClient

LOG = logging.getLogger('SIP.EC.CDB')
AGGREGATE_TYPE = 'sbi'


class SchedulingBlockDbClient(ProcessingControllerDbClient):
    """Configuration Database client API for the Scheduling Block Instance."""

    def __init__(self):
        """Initialise variables."""
        self._db = ConfigDb()
        self._pb = ProcessingBlockDbClient()
        ProcessingControllerDbClient.__init__(self, AGGREGATE_TYPE, self._db)

    ###########################################################################
    # Add functions
    ###########################################################################

    def add_sbi(self, config_dict: dict):
        """Add Scheduling Block to the database.

        Args:
            config_dict (dict): SBI configuration dictionary.
        """
        # Get schema for validation
        schema = self._get_schema()
        LOG.debug('Adding SBI with config: %s', config_dict)

        # Validates the schema
        validate(config_dict, schema)

        # Add status field and value to the data
        sbi_config = self._add_status(config_dict)

        sbi_id = sbi_config['id']
        # sbi_key = self._get_key(sbi_config['id'])get_sbi_id
        sbi_key = self.get_key(sbi_config['id'])

        # Splitting into different names and fields before
        # adding to the database
        scheduling_block_data, processing_block_data = \
            self._split_sbi(sbi_config)

        # Adding Scheduling block instance with id
        self._db.set_hash_values(sbi_key, scheduling_block_data)
        sbi_list_key = '{}:active'.format(AGGREGATE_TYPE)
        self._db.append_to_list(sbi_list_key, sbi_id)

        # Publish an event to notify subscribers of the new SBI
        self.publish(sbi_id, 'created')

        # Adding processing blocks
        self._pb.add_pb(processing_block_data, sbi_key)

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

        sbi_index = self.get_num_sbi()
        return '{}-{}-sbi{:03d}'.format(_date, project, sbi_index)

    def get_num_sbi(self):
        """Get the number of Scheduling Blocks Instance ids in the database.

        Returns:
            int, The number of Scheduling Block Instance IDs

        """
        return len(self.get_active())

    # TODO (NJT) Need to work on this function
    def get_sub_array_ids(self):
        """Get list of sub array ids."""
        # Initialise empty list
        _sub_array_ids = []

        for blocks_id in self.get_active():
            block_details = self.get_block_details(blocks_id)
            _sub_array_ids.append(block_details['sub_array_id'])
        _sub_array_ids = sorted(list(set(_sub_array_ids)))
        return _sub_array_ids

    # TODO (NJT) Need to work on this function
    def get_sub_array_sbi_ids(self, sub_array_id):
        """Get Scheduling Block Instance ID associated with sub array id.

        Args:
            sub_array_id (str):  Sub array ID.

        """
        # Initialise empty list
        _ids = []

        for blocks_id in self.get_active():
            details = self.get_block_details(blocks_id)
            if details['sub_array_id'] == sub_array_id:
                _ids.append(details['id'])
        return _ids

    # #########################################################################
    # Cancel functions
    # #########################################################################

    def cancel_sbi(self, sbi_id: str):
        """Cancel a scheduling block instance.

        Args:
            sbi_id (str): Scheduling block instance id

        """
        LOG.debug('Deleting SBI %s', sbi_id)
        sbi_key = self.get_key(sbi_id)

        # Check that the key exists!
        if not self._db.get_keys(sbi_key):
            raise KeyError('Scheduling Block Instance not found: {}'
                           .format(sbi_id))

        # lists in one atomic transaction (using pipelines)
        self.publish(sbi_id, 'cancelled')
        self._db.remove_element('{}:active'.format(AGGREGATE_TYPE), 0,
                                sbi_id)
        self._db.append_to_list('{}:cancelled'.format(AGGREGATE_TYPE),
                                sbi_id)
        # sbi_pb_ids = get_hash_value(block_id, 'processing_block_ids')
        sbi_pb_ids = ast.literal_eval(self._db.get_hash_value(
            sbi_key, 'processing_block_ids'))

        for pb_id in sbi_pb_ids:
            self._pb.cancel_processing_block(pb_id)

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

    def _split_sbi(self, scheduling_block):
        """Split the scheduling block data into multiple names.

        Args:
            scheduling_block: Scheduling block instance data

        Returns:
            dict: split of scheduling block data and processing block data

        Raises:
            Exception: If processing block already exists in the database

        """
        # Initialise empty list
        _scheduling_block_data = {}
        _processing_block_data = {}
        _processing_block_id = []

        for block_data in scheduling_block:
            block_values = scheduling_block[block_data]
            if block_data != 'processing_blocks':
                _scheduling_block_data[block_data] = block_values
            else:
                # Check if there is a processing block that already exists in
                # the database
                processing_block_id = self._pb.get_active()

                for value in block_values:
                    if value['id'] not in processing_block_id:
                        _processing_block_data = block_values
                    else:
                        raise Exception("Processing block already exists: {}"
                                        .format(value['id']))

        # Adding processing block id to the scheduling block list
        for block_id in _processing_block_data:
            _processing_block_id.append(block_id['id'])
        _scheduling_block_data['processing_block_ids'] = _processing_block_id

        return _scheduling_block_data, _processing_block_data
