# -*- coding: utf-8 -*-
"""High-level interface for Scheduling Block Instance (SBI) objects."""
import ast
import datetime
import json
import logging
import os
from typing import List, Union

from jsonschema import validate

from .config_db_redis import ConfigDb
from .pb_list import ProcessingBlockList
from .scheduling_object import (PB_TYPE_PREFIX, SBI_TYPE_PREFIX,
                                SchedulingObject)
from .workflow_definitions import (get_workflow_definition,
                                   get_workflow_definitions)
from .subarray import Subarray

LOG = logging.getLogger('SIP.EC.CDB')
DB = ConfigDb()


class SchedulingBlockInstanceList(SchedulingObject):
    """Configuration Database client API for Scheduling Block Instances."""

    _pb_list = ProcessingBlockList()

    def __init__(self, schema_path=None):
        """Initialise variables."""
        SchedulingObject.__init__(self, SBI_TYPE_PREFIX, DB)
        if schema_path is None:
            schema_path = os.path.join(os.path.dirname(__file__), 'schema',
                                       'sbi_configure_schema.json')
        LOG.debug('Loading SBI Schema: %s', schema_path)
        self._schema = self._get_schema(schema_path)

    ###########################################################################
    # Add functions
    ###########################################################################

    def add(self, sbi_config: dict, subarray_id: Union[str, int] = None):
        """Add Scheduling Block Instance to the database.

        Expected to be used by configure() commands on the Tango Control
        interface devices.

        This method takes an SBI configuration dictionary, populates
        the SBI and associated PB data models in the Configuration Database
        and issues events to notify that the new SBI and PBs have been
        created.

        FIXME(BM) The add transition should be a single atomic operation!

        Args:
            sbi_config (dict): SBI configuration dictionary.
            subarray_id (str or int, optional): SBI subarray Id or index

        Raises:
            ValidationError, if the supplied config_dict is invalid.
            RuntimeError, if a PB workflow definition (id, version) is not
            known.

        """
        LOG.debug('Adding SBI with config: %s', sbi_config)

        # Validate the SBI schema
        LOG.debug('Validating configuration')
        validate(sbi_config, self._schema)

        # Split into different names and fields before adding to the db
        sbi_data, pb_data_list = self._split_sbi(sbi_config)

        LOG.debug('Initialising data object fields.')
        # Add status field and value to SBI data object
        self._init_status(sbi_data)

        # Add the subarray id to the SBI object
        if subarray_id is not None:
            # TODO(BM) Validate subarray id
            if isinstance(subarray_id, int):
                subarray_id = Subarray.get_id(subarray_id)
            sbi_data['subarray_id'] = subarray_id
            Subarray(subarray_id).add_sbi_id(sbi_data['id'])
        else:
            sbi_data['subarray_id'] = 'none'

        # Add a created date to the SBI object
        utc_now = datetime.datetime.utcnow()
        sbi_data['created'] = utc_now.isoformat()
        sbi_data['updated'] = utc_now.isoformat()

        # Add SBI data object to the database
        LOG.debug('Adding SBI data object to the configuration database.')
        DB.set_hash_values(self.primary_key(sbi_data['id']), sbi_data)

        # Add the SBI key to the list of active SBIs
        LOG.debug('Updating list of active SBIs')
        sbi_list_key = '{}:active'.format(self.aggregate_type)
        DB.append_to_list(sbi_list_key, sbi_data['id'])

        # Publish an event to notify subscribers of the new SBI
        LOG.debug('Publishing SBI created event')
        self.publish(sbi_data['id'], 'created')

        # Add workflow definitions
        # self._add_workflow_definitions(pb_data)

        # Add processing blocks belonging to the SBI
        for pb_data in pb_data_list:
            pb_data['sbi_id'] = sbi_data['id']
            self._add_pb(pb_data)

    # #########################################################################
    # Get functions
    # #########################################################################

    def len(self):
        """Get the number of Scheduling Blocks Instance ids in the database.

        Returns:
            int, The number of Scheduling Block Instance IDs

        """
        return len(self.get_active())

    def get_pb_ids(self, sbi_id: str) -> List[str]:
        """Return the list of PB ids associated with the SBI.

        Args:
            sbi_id (str): Scheduling block instance id

        Returns:
            list, Processing block ids

        """
        # TODO(BM) move this hardcoded key to a function?
        key = 'processing_block_ids'
        return ast.literal_eval(DB.get_hash_value(
            self.primary_key(sbi_id), key))

    # #########################################################################
    # Abort functions
    # #########################################################################

    def abort(self, sbi_id: str):
        """Abort / Cancel a Scheduling Block Instance.

        Args:
            sbi_id (str): Scheduling block instance id

        """
        LOG.debug('Deleting SBI %s', sbi_id)
        sbi_key = self.primary_key(sbi_id)

        # Check that the key exists!
        if not DB.get_keys(sbi_key):
            raise KeyError('Scheduling Block Instance not found: {}'
                           .format(sbi_id))

        # lists in one atomic transaction (using pipelines)
        self.publish(sbi_id, 'aborted')
        DB.remove_element('{}:active'.format(self.aggregate_type), 0, sbi_id)
        DB.append_to_list('{}:aborted'.format(self.aggregate_type), sbi_id)
        # sbi_pb_ids = get_hash_value(block_id, 'processing_block_ids')
        sbi_pb_ids = ast.literal_eval(
            DB.get_hash_value(sbi_key, 'processing_block_ids'))

        for pb_id in sbi_pb_ids:
            self._pb_list.abort(pb_id)

    def delete_all(self):
        """Delete all SBIs from the database.

        This function will delete all SBI keys as well as associated PB
        keys from the database.

        Warning: Use with extreme care! (not to be used in normal operation)

        """
        # TODO

    # #########################################################################
    # Private functions
    # #########################################################################

    @staticmethod
    def _get_schema(schema_path: str) -> dict:
        """Get the schema for validation."""
        with open(schema_path, 'r') as file:
            schema_data = file.read()
        schema = json.loads(schema_data)
        return schema

    @staticmethod
    def _init_status(sbi_data: dict, initial_status: str = 'created'):
        """Add status fields to the SBI data object.

        Args:
            sbi_data (dict): SBI data object dictionary.
            initial_status (str): Initial SBI status
        """
        sbi_data['status'] = initial_status

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
                processing_block_id = self._pb_list.get_active()
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

    def _add_pb(self, pb_config: dict):
        """Add a Processing Block data object to the db.

        Args:
            pb_config (dict): Processing block data

        Raises:
            RuntimeError, if the parent sbi_id is not set or doesnt exist

        """
        if 'sbi_id' not in pb_config:
            raise RuntimeError('Parent SBI missing from PB configuration!')
        if pb_config['sbi_id'] not in self.get_active():
            raise RuntimeError('Specified parent SBI not known!')

        LOG.debug('Adding PB %s', pb_config['id'])

        # Add status fields to the PB object
        pb_config['status'] = 'created'

        # Add a created date and updated fields
        utc_now = datetime.datetime.utcnow()
        pb_config['created'] = utc_now.isoformat()
        pb_config['updated'] = utc_now.isoformat()

        # set default priority, if not defined
        if 'priority' not in pb_config:
            pb_config['priority'] = 0

        # Retrieve the workflow definition
        workflow = self._get_workflow_definition(pb_config)
        # Add workflow stage status fields
        for stage in workflow['stages']:
            stage['status'] = 'none'
        pb_config['workflow_parameters'] = pb_config['workflow']['parameters']
        pb_config['workflow_id'] = pb_config['workflow']['id']
        pb_config['workflow_version'] = pb_config['workflow']['version']
        pb_config['workflow_stages'] = workflow['stages']
        pb_config.pop('workflow', None)

        # Add resources and dependencies to PB and workflow stages if not
        # defined
        for key in ['resources_required', 'resources_assigned',
                    'dependencies']:
            if key not in pb_config:
                pb_config[key] = []
            for stage in pb_config['workflow_stages']:
                if key not in stage:
                    stage[key] = []

        # Adding Processing block with id
        pb_key = '{}:{}'.format(PB_TYPE_PREFIX, pb_config['id'])
        DB.set_hash_values(pb_key, pb_config)
        # for stage in pb_config['workflow_stages']:
        #     DB.append_to_list('{}:workflow_stages'.format(pb_key), stage)
        DB.append_to_list('{}:active'.format(PB_TYPE_PREFIX), pb_config['id'])
        DB.append_to_list('{}:active:{}'.format(
            PB_TYPE_PREFIX, pb_config['type']), pb_config['id'])

        # Publish an event to notify subscribers of the new PB
        self._events.publish(PB_TYPE_PREFIX, pb_config["id"], 'created')

    @staticmethod
    def _get_workflow_definition(pb_config):
        """Add a workflow definition to the PB.

        Args:
            pb_config (dict): List of PB data objects.

        Returns:
            dict, updated SBI data object dictionary.

        Raises:
            RunTimeError, if the workflow definition (id, version)
            specified in the sbi_config is not known.

        """
        known_workflows = get_workflow_definitions()
        workflow_id = pb_config['workflow']['id']
        workflow_version = pb_config['workflow']['version']
        if workflow_id not in known_workflows or \
           workflow_version not in known_workflows[workflow_id]:
            raise RuntimeError("Unknown workflow definition: {}:{}"
                               .format(workflow_id, workflow_version))
        workflow_config = get_workflow_definition(workflow_id,
                                                  workflow_version)
        return workflow_config
