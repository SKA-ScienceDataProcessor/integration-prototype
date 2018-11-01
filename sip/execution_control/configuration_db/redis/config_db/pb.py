# coding=utf-8
"""High Level interface to Processing Block (PB) objects."""
import ast
import datetime
import warnings
from random import randint

from .config_db_redis import ConfigDb
from .scheduling_object import SchedulingObject

DB = ConfigDb()
AGGREGATE_TYPE = 'pb'


class ProcessingBlock(SchedulingObject):
    """Processing Block Configuration Database API."""

    def __init__(self, pb_id):
        """Create a PB object.

        Args:
            pb_id (str): Processing Block Identifier

        Raises:
            KeyError, if the specified PB does not exist

        """
        SchedulingObject.__init__(self, AGGREGATE_TYPE, pb_id)
        self._check_exists()

    def add_assigned_resources(self, resources: dict):
        """Add assigned resources to db.

        Args:
            resources (dict): Assigned resources to a specific pb

        """
        warnings.warn("Warning this function is untested", FutureWarning)
        # Initialising empty list
        workflow_list = []
        workflow_dict = {}

        # Add assigned resources to workflow
        workflow = DB.get_hash_value(self._key, 'workflow')
        for stages in ast.literal_eval(workflow):
            workflow_stage = dict(stages)
            workflow_stage['assigned_resources'] = resources
            workflow_list.append(workflow_stage)

        workflow_dict['workflow'] = workflow_list
        DB.set_hash_values(self._key, workflow_dict)

    def get_workflow_stage(self, stage_id: str):
        """Return details of a workflow stage associated to the PB.

        Args:
            stage_id (str): Workflow stage identifier

        Returns:
            dict, resources of a specified pb

        """
        warnings.warn("Warning this function is untested", FutureWarning)
        workflow_list = DB.get_hash_value(self._key, 'workflow')
        for stages in ast.literal_eval(workflow_list):
            workflow_stage = dict(stages)[stage_id]
            return workflow_stage

    def abort(self):
        """Abort the processing_block."""
        pb_type = DB.get_hash_value(self._key, 'type')
        key = '{}:active'.format(self._type)
        DB.remove_from_list(key, self._id)
        key = '{}:active:{}'.format(self._type, pb_type)
        DB.remove_from_list(key, self._id)
        key = '{}:aborted'.format(self._type)
        DB.append_to_list(key, self._id)
        key = '{}:aborted:{}'.format(self._type, pb_type)
        DB.append_to_list(key, self._id)
        self.publish('aborted')

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
