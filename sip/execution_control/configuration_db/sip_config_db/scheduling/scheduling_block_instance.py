# coding=utf-8
"""High Level interface to Scheduling Block Instance (SBI) objects."""
import ast
import copy
import datetime
import json
from os.path import dirname, join
from random import randint
from typing import List

from jsonschema import validate

from ._keys import PB_KEY, SBI_KEY, WORKFLOW_DEFINITION_KEY
from ._scheduling_object import SchedulingObject
from .processing_block import ProcessingBlock
from .workflow_definition import get_workflow
from .. import ConfigDb

DB = ConfigDb()


class SchedulingBlockInstance(SchedulingObject):
    """Scheduling Block Instance Configuration Database API."""

    def __init__(self, sbi_id: str):
        """Create a SBI object.

        Args:
            sbi_id (str): SBI Identifier

        Raises:
              KeyError, if the specified SBI does not exist.

        """
        SchedulingObject.__init__(self, SBI_KEY, sbi_id)
        self._check_object_exists()

    @classmethod
    def from_config(cls, config_dict: dict):
        """Create an SBI object from the specified configuration dict.

        NOTE(BMo) This should really be done as a single atomic db transaction.

        Args:
            config_dict(dict): SBI configuration dictionary

        """
        # Validate the SBI config using the SBI schema
        schema_path = join(dirname(__file__), 'schema',
                           'configure_sbi_2.0.json')
        with open(schema_path, 'r') as file:
            schema = json.loads(file.read())
            validate(config_dict, schema)

        # Add SBI status field
        config_dict['status'] = 'created'

        # Set the subarray field to None if not defined.
        if 'subarray_id' not in config_dict:
            config_dict['subarray_id'] = 'None'

        # Add created, and updated timestamps.
        timestamp = datetime.datetime.utcnow().isoformat()
        config_dict['created'] = timestamp
        config_dict['updated'] = timestamp

        # Split out the processing block data array
        pb_list = copy.deepcopy(config_dict['processing_blocks'])

        # Remove processing blocks from the SBI configuration.
        config_dict.pop('processing_blocks', None)

        # Add list of PB ids to the SBI configuration
        config_dict['processing_block_ids'] = []
        for pb in pb_list:
            config_dict['processing_block_ids'].append(pb['id'])

        # Check that the PBs do not already exist and workflow definitions
        # are known about before adding anything to the DB!
        # This prevents adding SBIs data objects with invalid PBs!
        for pb in pb_list:
            _pb_key = '{}:{}'.format(PB_KEY, pb['id'])
            if DB.key_exists(_pb_key):
                raise KeyError("PB '{}' already exists!".format(pb['id']))
            _workflow = pb['workflow']
            _workflow_key = '{}:{}:{}'.format(
                WORKFLOW_DEFINITION_KEY, _workflow['id'], _workflow['version'])
            if not DB.key_exists(_workflow_key):
                raise KeyError("Unknown workflow definition: {}:{}"
                               .format(_workflow['id'], _workflow['version']))

        # Add the SBI data object to the database.
        key = SchedulingObject.get_key(SBI_KEY, config_dict['id'])
        DB.save_dict(key, config_dict, hierarchical=False)

        # Add the SBI id to the list of active SBIs
        key = '{}:active'.format(SBI_KEY)
        DB.append_to_list(key, config_dict['id'])

        # Publish notification to subscribers
        sbi = SchedulingObject(SBI_KEY, config_dict['id'])
        sbi.status = 'created'

        for pb in pb_list:
            pb['sbi_id'] = config_dict['id']
            pb['version'] = config_dict['version']
            cls._add_pb(pb)

        return cls(config_dict['id'])

    @property
    def processing_block_ids(self) -> List[str]:
        """Get the PB IDs associated with the SBI.

        Returns:
            list, Processing block ids

        """
        values = DB.get_hash_value(self._key, 'processing_block_ids')
        return ast.literal_eval(values)

    @property
    def num_processing_blocks(self) -> int:
        """Get the number of PBs associated with the SBI."""
        return len(self.processing_block_ids)

    @property
    def num_pbs(self) -> int:
        """Get the number of PBs associated with the SBI."""
        return self.num_processing_blocks

    @property
    def subarray(self) -> str:
        """Get the subarray identifier for this SBI."""
        return DB.get_hash_value(self._key, 'subarray_id')

    def abort(self):
        """Abort the SBI (and associated PBs)."""
        self.status = 'aborted'
        DB.remove_from_list('{}:active'.format(self._type), self._id)
        DB.append_to_list('{}:aborted'.format(self._type), self._id)
        sbi_pb_ids = ast.literal_eval(
            DB.get_hash_value(self._key, 'processing_block_ids'))

        for pb_id in sbi_pb_ids:
            pb = ProcessingBlock(pb_id)
            pb.abort()

    def clear_subarray(self):
        """Clear the subarray_id associated with the SBI.

        This is used when deactivating a subarray.
        """
        DB.set_hash_value(self._key, 'subarray_id', 'none')

    @staticmethod
    def generate_sbi_id(date=None, project: str = 'sip',
                        instance_id: int = None) -> str:
        """Generate a SBI Identifier.

        Args:
            date (str or datetime.datetime, optional): UTC date of the SBI
            project (str, optional ): Project Name
            instance_id (int, optional): SBI instance identifier

        Returns:
            str, Scheduling Block Instance (SBI) ID.

        """
        if date is None:
            date = datetime.datetime.utcnow()

        if isinstance(date, datetime.datetime):
            date = date.strftime('%Y%m%d')

        if instance_id is None:
            instance_id = randint(0, 9999)

        return 'SBI-{}-{}-{:04d}'.format(date, project, instance_id)

    @staticmethod
    def _add_pb(pb_config: dict):
        """."""
        # Add status field to the PB
        pb_config['status'] = 'created'

        # Add created and updated timestamps to the PB
        timestamp = datetime.datetime.utcnow().isoformat()
        pb_config['created'] = timestamp
        pb_config['updated'] = timestamp

        # set default priority, if not defined
        if 'priority' not in pb_config:
            pb_config['priority'] = 0

        # Retrieve the workflow definition
        SchedulingBlockInstance._associate_workflow(pb_config)

        # If needed, add resources and dependencies fields
        if 'dependencies' not in pb_config:
            pb_config['dependencies'] = []

        pb_workflow_params = pb_config['workflow_parameters']
        for stage in pb_config['workflow_stages']:
            stage['resources_assigned'] = []
            stage['status'] = 'created'
            stage['updated'] = timestamp
            if 'args' not in stage:
                stage['args'] = ''
            if 'compose_file' not in stage:
                stage['compose_file'] = ''
            if 'parameters' not in stage:
                stage['parameters'] = dict()
            if stage['id'] in pb_workflow_params:
                stage['parameters'] = {**pb_workflow_params[stage['id']],
                                       **stage['parameters']}

        # Add PB to the the database
        key = SchedulingObject.get_key(PB_KEY, pb_config['id'])
        # DB.set_hash_values(key, pb_config)
        DB.save_dict(key, pb_config, hierarchical=False)

        # Add to list of PB ids
        key = '{}:active'.format(PB_KEY)
        DB.append_to_list(key, pb_config['id'])
        key = '{}:active:{}'.format(PB_KEY, pb_config['type'])
        DB.append_to_list(key, pb_config['id'])

        # Publish an event to to notify subscribers of the new PB
        pb = SchedulingObject(PB_KEY, pb_config['id'])
        pb.status = 'created'

    @staticmethod
    def _associate_workflow(pb_config: dict):
        """Update the PB configuration workflow definition.

        Args:
            pb_config (dict): PB configuration dictionary

        Raises:
            RunTimeError, if the workflow definition (id, version)
            specified in the sbi_config is not known.

        """
        workflow_id = pb_config['workflow']['id']
        workflow_version = pb_config['workflow']['version']
        workflow = get_workflow(workflow_id, workflow_version)
        for stage in workflow['stages']:
            stage['status'] = 'none'
        pb_config['workflow_parameters'] = pb_config['workflow']['parameters']
        pb_config['workflow_id'] = pb_config['workflow']['id']
        pb_config['workflow_version'] = pb_config['workflow']['version']
        pb_config['workflow_stages'] = workflow['stages']
        pb_config.pop('workflow', None)
