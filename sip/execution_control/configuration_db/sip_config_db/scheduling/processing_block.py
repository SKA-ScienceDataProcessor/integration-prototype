# coding=utf-8
"""Interface to Processing Block (PB) data objects."""
import ast
import datetime
from random import randint
from typing import List

from ._keys import PB_KEY
from ._scheduling_object import SchedulingObject
from .dependency import Dependency
from .workflow_stage import WorkflowStage
from .. import ConfigDb, LOG

DB = ConfigDb()


class ProcessingBlock(SchedulingObject):
    """Processing Block Configuration Database API."""

    def __init__(self, pb_id):
        """Create a PB object.

        Args:
            pb_id (str): Processing Block Identifier

        Raises:
            KeyError, if the specified PB does not exist

        """
        SchedulingObject.__init__(self, PB_KEY, pb_id)
        self._check_object_exists()

    @property
    def type(self) -> str:
        """Return the PB type."""
        return DB.get_hash_value(self.key, 'type')

    @property
    def priority(self) -> int:
        """Return the PB priority."""
        return ast.literal_eval(DB.get_hash_value(self.key, 'priority'))

    @property
    def sbi_id(self) -> str:
        """Return the PB SBI Id."""
        return DB.get_hash_value(self.key, 'sbi_id')

    @property
    def dependencies(self) -> List[Dependency]:
        """Return the PB dependencies."""
        dependencies_str = DB.get_hash_value(self.key, 'dependencies')
        dependencies = []
        for dependency in ast.literal_eval(dependencies_str):
            dependencies.append(Dependency(dependency))
        return dependencies

    @property
    def workflow_id(self) -> str:
        """Return the PB workflow ID."""
        return DB.get_hash_value(self.key, 'workflow_id')

    @property
    def workflow_version(self) -> str:
        """Return the PB workflow version."""
        return DB.get_hash_value(self.key, 'workflow_version')

    @property
    def workflow_parameters(self) -> dict:
        """Return the PB workflow parameters."""
        return ast.literal_eval(DB.get_hash_value(self.key,
                                                  'workflow_parameters'))

    @property
    def workflow_stages(self) -> List[WorkflowStage]:
        """Return list of workflow stages.

        Returns:
            dict, resources of a specified pb

        """
        workflow_stages = []
        stages = DB.get_hash_value(self.key, 'workflow_stages')
        for index in range(len(ast.literal_eval(stages))):
            workflow_stages.append(WorkflowStage(self.id, index))
        return workflow_stages

    @staticmethod
    def generate_pb_id(date: datetime.datetime) -> str:
        """Generate a Processing Block (PB) Instance ID.

        Args:
            date (datetime.datetime): UTC date of the PB

        Returns:
            str, Processing Block ID

        """
        date = date.strftime('%Y%m%d')
        return 'PB-{}-{}-{:03d}'.format(date, 'sip', randint(0, 100))

    def abort(self):
        """Abort the Processing Block."""
        LOG.debug('Aborting PB %s', self._id)
        self.status = 'aborted'
        pb_type = DB.get_hash_value(self.key, 'type')
        key = '{}:active'.format(self._type)
        DB.remove_from_list(key, self._id)
        key = '{}:active:{}'.format(self._type, pb_type)
        DB.remove_from_list(key, self._id)
        key = '{}:aborted'.format(self._type)
        DB.append_to_list(key, self._id)
        key = '{}:aborted:{}'.format(self._type, pb_type)
        DB.append_to_list(key, self._id)
        self._mark_updated()
