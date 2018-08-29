# -*- coding: utf-8 -*-
"""High Level Processing Controller Client API."""
import ast
import json
import logging
import os
import datetime
from typing import List
from jsonschema import validate

from .config_db_redis import ConfigDb
from . import events
from .event_keys import aggregate_events_data, aggregate_events_list

LOG = logging.getLogger('SIP.EC.CDB')
SBI_AGGREGATE_TYPE = 'sbi'
PB_AGGREGATE_TYPE = 'pb'


class ProcessingControllerDbClient:
    """Configuration Database client API for the Processing Controller."""

    def __init__(self):
        """Initialise the client."""
        self._db = ConfigDb()
        self._events = events

    ###########################################################################
    # Pub Sub functions
    ###########################################################################

    def subscribe(self, subscriber: str, aggregate_type: str) -> \
            events.EventQueue:
        """Subscribe to Scheduling Block Instance (SBI) events.

        Args:
            subscriber (str): Subscriber name.
            aggregate_type (str): Aggregate type

        Returns:
            events.EventQueue, Event queue object for querying PB events.

        """
        return self._events.subscribe(aggregate_type, subscriber)

    def get_subscribers(self, aggregate_type: str):
        """Get the list of subscribers to Scheduling Block Instance (SBI) events.

        Args:
            aggregate_type (str): Aggregate type

        Returns:
            List[str], list of subscriber names.

        """
        return self._events.get_subscribers(aggregate_type)

    def publish(self, block_id: str, event_type: str, aggregate_type: str,
                event_data: dict = None):
        """Publish a SBI event.

        Args:
            block_id (str): Scheduling block instance or processing block id.
            event_type (str): Type of event.
            aggregate_type (str): Aggregate type
            event_data (dict, optional): Event data.

        """
        self._events.publish(aggregate_type, block_id, event_type, event_data)

    ###########################################################################
    # Add functions
    ###########################################################################

    def add_scheduling_block_instance(self, config_dict: dict,
                                      sbi_aggregate_type=None,
                                      pb_aggregate_type=None):
        """Add Scheduling Block to the database.

        Args:
            config_dict (dict): SBI configuration dictionary.
            sbi_aggregate_type (str): Aggregate type for Scheduling block
                                      instance
            pb_aggregate_type (str): Aggregate type for processing block
        """

        # Checking for aggregate types
        if sbi_aggregate_type:
            sbi_aggregate_type = sbi_aggregate_type
        else:
            sbi_aggregate_type = SBI_AGGREGATE_TYPE

        if pb_aggregate_type:
            pb_aggregate_type = pb_aggregate_type
        else:
            pb_aggregate_type = PB_AGGREGATE_TYPE

        # Get schema for validation
        schema = self._get_schema()
        LOG.debug('Adding SBI with config: %s', config_dict)

        # Validates the schema
        validate(config_dict, schema)

        # Add status field and value to the data
        sbi_config = self._add_status(config_dict)

        sbi_id = sbi_config['id']
        sbi_key = self._get_key(sbi_config['id'], sbi_aggregate_type)

        # Splitting into different names and fields before
        # adding to the database
        scheduling_block_data, processing_block_data = \
            self._split_scheduling_block(sbi_config)

        # Adding Scheduling block instance with id
        # name = "scheduling_block:" + sbi_config["id"]
        self._db.set_hash_values(sbi_key, scheduling_block_data)
        sbi_list_key = '{}:active'.format(sbi_aggregate_type)
        self._db.append_to_list(sbi_list_key, sbi_id)

        # Publish an event to notify subscribers of the new SBI
        self.publish(sbi_id, 'created', sbi_aggregate_type)

        # Adding Processing block with id
        for sbi_pb_config in processing_block_data:
            pb_id = sbi_pb_config['id']
            pb_key = self._get_key(pb_id, pb_aggregate_type)
            sbi_pb_config['scheduling_block_id'] = sbi_key
            self._db.set_hash_values(pb_key, sbi_pb_config)
            self._db.append_to_list('{}:active'.format(pb_aggregate_type), pb_id)
            self._db.append_to_list('{}:active:{}'.format(
                pb_aggregate_type, sbi_pb_config['type']), pb_id)

            # Publish an event to notify subscribers of the new PB
            self.publish(sbi_pb_config["id"], 'created', pb_aggregate_type)

    # #########################################################################
    # Get functions
    # #########################################################################

    def get_scheduling_block_instance_id(self, date=None, project='sip'):
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

    def get_scheduling_block_instance_ids(self):
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

    def get_num_scheduling_block_instance(self):
        """Get the number of Scheduling Blocks Instance ids in the database.

        Returns:
            int, The number of Scheduling Block Instance IDs

        """
        return len(self.get_sbi_ids())

    def get_pb_ids(self, sbi_id: str) -> List[str]:
        """Return the list of PB ids associated with the SBI.

        Args:
            sbi_id (str): SBI id

        Returns:
            list,

        """
        # TODO(BM) move this hardcoded key to a function?
        key = 'processing_block_ids'
        return ast.literal_eval(self._db.get_hash_value(self._get_key(
            sbi_id, SBI_AGGREGATE_TYPE), key))

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
        _sub_array_ids = []

        for blocks_id in self.get_scheduling_block_ids():
            block_details = self.get_block_details(blocks_id)
            _sub_array_ids.append(block_details['sub_array_id'])
        _sub_array_ids = sorted(list(set(_sub_array_ids)))
        return _sub_array_ids

    def get_sub_array_sbi_ids(self, sub_array_id):
        """Get Scheduling Block Instance ID associated with sub array id."""
        _ids = []

        for blocks_id in self.get_scheduling_block_ids():
            details = self.get_block_details(blocks_id)
            if details['sub_array_id'] == sub_array_id:
                _ids.append(details['id'])
        return _ids

    def get_block_details(self, block_ids: list, aggregate_type: str):
        """Get the details of a Scheduling or Processing block.

        Args:
            block_ids (list): List of block IDs
            aggregate_type (str): Aggregate type

        Returns:
            dict, details of the scheduling or processing block

        """
        # Initialise empty dict
        block_data = {}

        # Convert input to list, if needed
        if not isinstance(block_ids, (list, tuple)):
            block_ids = [block_ids]

        for _id in block_ids:
            sbi_key = self._get_key(_id, aggregate_type)

            # Check that the key exists
            if not self._db.get_keys(sbi_key):
                raise KeyError('Scheduling Block Instance not found: {}'
                               .format(_id))

            block_key = self._db.get_keys(sbi_key)[0]
            block_data = self._db.get_hash_dict(block_key)
            # NOTE(BM) unfortunately the following hack doesn't quite work \
            # for keys where the value is a Python object (list, dict etc.) \
            # but is good enough for now where objects are stored as strings.
            for key in block_data:
                for char in ['[', '{']:
                    if char in block_data[key]:
                        block_data[key] = ast.literal_eval(str(block_data[key]))
        return block_data

    def get_status(self, block_id: str, aggregate_type: str) -> str:
        """Get the status of an SBI.

        Args:
            block_id (str): Scheduling block instance or processing block id.
            aggregate_type (str): Aggregate type

        Returns:
            str,

        """
        sbi_key = self._get_key(block_id, aggregate_type)

        # Check that the key exists
        if not self._db.get_keys(sbi_key):
            raise KeyError('Scheduling Block Instance not found: {}'
                           .format(block_id))

        key = self.get_event_list_key(block_id, aggregate_type)
        last_event = self._db.get_hash_value(self.get_event_data_key(
            block_id, aggregate_type), self._db.get_list_value(key, -1))
        last_event = ast.literal_eval(last_event)
        return last_event['type']

    def get_active(self, aggregate_type: str):
        """Get the list of active SBI from the database.

        Args:
            aggregate_type (str): Aggregate type

        Returns:
            list, SBI ids

        """
        return self._db.get_list('{}:active'.format(aggregate_type))

    def get_cancelled(self, aggregate_type: str):
        """Get the list of cancelled SBI from the database.

        Args:
            aggregate_type (str): Aggregate type

        Returns:
            list, SBI ids


        """
        return self._db.get_list('{}:cancelled'.format(aggregate_type))

    def get_completed(self, aggregate_type: str):
        """Get the list of completed SBI from the database.

        Args:
            aggregate_type (str): Aggregate type

        Returns:
            list, SBI ids

        """
        return self._db.get_list('{}:completed'.format(aggregate_type))

    def get_event_list_key(self, sbi_id: str, aggregate_type: str) -> str:
        """Return the SBI events list db key.

        Args:
            sbi_id (str): SBI id.
            aggregate_type (str): Aggregate type

        Returns:
            str, db key for the specified SBI event data.

        """
        return aggregate_events_list(self._get_key(sbi_id, aggregate_type))

    def get_event_data_key(self, sbi_id: str, aggregate_type: str) -> str:
        """Return the SBI events data db key.

        Args:
            sbi_id (str): SBI id.
            aggregate_type (str): Aggregate type

        Returns:
            str, db key for the specified SBI event data.

        """
        return aggregate_events_data(self._get_key(sbi_id, aggregate_type))

    def get_cancelled(self, aggregate_type: str):
        """Get the list of cancelled SBI from the database.

        Returns:
            list, SBI ids
            aggregate_type (str): Aggregate type

        """
        return self._db.get_list('{}:cancelled'.format(aggregate_type))

    def get_events(self, pb_id: str) -> List[events.Event]:
        """Get event data for the specified PB.

        Args:
            pb_id (str): PB Id.

        Returns:
            list of event data dictionaries

        """
        event_data_key = self.get_event_data_key(pb_id, 'pb')
        event_list = []
        for event_id, data in self._db.get_hash_dict(event_data_key).items():
            data = ast.literal_eval(data)
            event_list.append(events.Event(event_id, 'pb', '', data))
        return event_list

    # #########################################################################
    # Update functions
    # #########################################################################

    def update_value(self, block_id :str, field: str, value: str,
                     aggregate_type: str):
        """Update the value of the given block id and field.

        Args:
            block_id (str):
            field (str):
            value(str):
            aggregate_type (str): Aggregate type

        """
        block_key = self._get_key(block_id, aggregate_type)
        for key in block_key:
            self._db.set_hash_value(key, field, value)

    # #########################################################################
    # Cancel functions
    # #########################################################################

    def cancel_scheduling_block_instance(self, block_id: str):
        """Cancel a SBI.

        Args:
            block_id (str): the SBI Id

        """
        LOG.debug('Deleting SBI %s', block_id)
        sbi_key = self._get_key(block_id, 'sbi')

        # Check that the key exists!
        if not self._db.get_keys(sbi_key):
            raise KeyError('Scheduling Block Instance not found: {}'
                           .format(block_id))

        # lists in one atomic transaction (using pipelines)
        self.publish(block_id, 'cancelled', SBI_AGGREGATE_TYPE)
        self._db.remove_element('{}:active'.format(SBI_AGGREGATE_TYPE), 0,
                                block_id)
        self._db.append_to_list('{}:cancelled'.format(SBI_AGGREGATE_TYPE),
                                block_id)
        # sbi_pb_ids = get_hash_value(block_id, 'processing_block_ids')
        sbi_pb_ids = ast.literal_eval(self._db.get_hash_value(sbi_key,
                                      'processing_block_ids'))

        for pb_id in sbi_pb_ids:
            self.cancel_processing_block(pb_id)

    def cancel_processing_block(self, pb_id: str):
        """Cancel a PB.

        Args:
            pb_id (str): the PB Id

        """
        pb_key = self._get_key(pb_id, 'pb')

        # Check that the key exists!
        if not self._db.get_keys(pb_key):
            raise KeyError('Processing Block not found: {}'
                           .format(pb_id))

        pb_type = self._db.get_hash_value(pb_key, 'type')
        # publish(pb_id, 'cancelled')
        self.publish(pb_id, 'cancelled', PB_AGGREGATE_TYPE)
        self._db.remove_element('{}:active'.format(PB_AGGREGATE_TYPE), 0, pb_id)
        self._db.remove_element('{}:active:{}'.format(PB_AGGREGATE_TYPE,
                                                      pb_type), 0, pb_id)
        self._db.append_to_list('{}:cancelled'.format(PB_AGGREGATE_TYPE), pb_id)
        self._db.append_to_list('{}:cancelled:{}'.format(PB_AGGREGATE_TYPE,
                                                         pb_type), pb_id)

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
    def _get_key(sbi_id: str, aggregate_type: str) -> str:
        """Return a Scheduling Block Instance db key.

        Args:
            sbi_id (str): Scheduling block instance id
            aggregate_type (str): Aggregate key

        Returns:
            str, db key for the specified SBI

        """
        return '{}:{}'.format(aggregate_type, sbi_id)

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
        _scheduling_block_data['processing_block_ids'] = _processing_block_id

        return _scheduling_block_data, _processing_block_data
