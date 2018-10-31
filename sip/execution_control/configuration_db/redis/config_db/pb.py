# coding=utf-8
"""High Level interface to Processing Block (PB) objects."""
import ast
import warnings
import datetime
from random import randint

from .scheduling_object import SchedulingObject
from .config_db_redis import ConfigDb


DB = ConfigDb()


class ProcessingBlock(SchedulingObject):
    """Processing Block Configuration Database API."""

    def __init__(self, pb_id):
        """Construct a Configuration Database Processing Block Object.

        Args:
            pb_id (str): Processing Block Identifier
        """
        SchedulingObject.__init__(self, 'pb', DB)
        self._id = pb_id
        self._key = self.primary_key(pb_id)

    def get_config(self):
        """Return the Processing Block Configuration."""
        return self.get_block_details([self._id])

    def add_assigned_resources(self, resources: dict):
        """Add assigned resources to db.

        Args:
            pb_id (str): Processing block id
            resources (dict): Assigned resources to a specific pb

        """
        warnings.warn("Warning this function is untested", FutureWarning)
        # Initialising empty list
        workflow_list = []
        workflow_dict = {}

        # Get key
        pb_key = self.primary_key(self._id)

        # Check that the key exists!
        if not DB.get_keys(pb_key):
            raise KeyError('Processing Block not found: {}'
                           .format(self._id))

        # Add assigned resources to workflow
        for stages in ast.literal_eval(DB.get_hash_value(
                pb_key, 'workflow')):
            workflow_stage = dict(stages)
            workflow_stage['assigned_resources'] = resources
            workflow_list.append(workflow_stage)

        workflow_dict['workflow'] = workflow_list
        DB.set_hash_values(pb_key, workflow_dict)

    def get_workflow_stage(self, stage: str):
        """Return details of a workflow stage associated to the PB.

        Args:
            pb_id (str): Processing block id
            stage (str): Workflow stage name

        Returns:
            dict, resources of a specified pb

        """
        warnings.warn("Warning this function is untested", FutureWarning)
        pb_key = self.primary_key(self._id)

        # Check that the key exists!
        if not DB.get_keys(pb_key):
            raise KeyError('Processing Block not found: {}'
                           .format(self._id))

        workflow_list = DB.get_hash_value(pb_key, 'workflow')
        for stages in ast.literal_eval(workflow_list):
            workflow_stage = dict(stages)[stage]
            return workflow_stage

    def abort(self):
        """Abort the processing_block."""
        pb_key = self.primary_key(self._id)

        # Check that the key exists!
        if not DB.get_keys(pb_key):
            raise KeyError('Processing Block not found: {}'.format(self._id))

        pb_type = DB.get_hash_value(pb_key, 'type')
        self.publish(self._id, 'aborted')
        DB.remove_element('{}:active'.format(self.aggregate_type), 0, self._id)
        DB.remove_element('{}:active:{}'.format(self.aggregate_type,
                                                pb_type), 0, self._id)
        DB.append_to_list('{}:aborted'.format(self.aggregate_type), self._id)
        DB.append_to_list('{}:aborted:{}'.format(self.aggregate_type,
                                                 pb_type), self._id)

    @staticmethod
    def get_id(date: datetime.datetime) -> str:
        """Generate a Processing Block (PB) Instance ID.

        Args:
            date (datetime.datetime): UTC date of the PB

        Returns:
            str, Processing Block ID

        """
        date = date.strftime('%Y%m%d')
        return 'PB-{}-{}-{:03d}'.format(date, 'sip', randint(0, 100))
