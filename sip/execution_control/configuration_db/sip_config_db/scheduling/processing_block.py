# coding=utf-8
"""High Level interface to Processing Block (PB) objects."""
import ast
import datetime
from random import randint
from typing import List, Union

from . import Dependency, Resource, WorkflowStage
from ._keys import PB_KEY
from ._scheduling_object import SchedulingObject
from .. import DB, LOG
from ..utils.datetime_utils import datetime_from_isoformat


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

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def version(self) -> str:
        """Return the PB version."""
        return DB.get_hash_value(self.key, 'version')

    @property
    def status(self) -> str:
        """Return the Processing Block status."""
        return DB.get_hash_value(self.key, 'status')

    @property
    def updated(self) -> datetime.datetime:
        """Return the last time the PB was updated."""
        return datetime_from_isoformat(DB.get_hash_value(self.key, 'updated'))

    @property
    def created(self) -> datetime.datetime:
        """Return the datetime the PB was created."""
        return datetime_from_isoformat(DB.get_hash_value(self.key, 'created'))

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
    def resources_assigned(self) -> List[Resource]:
        """Return list of resources assigned to the PB."""
        resources_str = DB.get_hash_value(self.key, 'resources_assigned')
        resources_assigned = []
        for resource in ast.literal_eval(resources_str):
            resources_assigned.append(Resource(resource))
        return resources_assigned

    @property
    def resources_required(self) -> List[Resource]:
        """Return list of resources required by the PB.

        This is resources common to all workflow stages.
        """
        resources_str = DB.get_hash_value(self.key, 'resources_required')
        resources_assigned = []
        for resource in ast.literal_eval(resources_str):
            resources_assigned.append(Resource(resource))
        return resources_assigned

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

    ###########################################################################
    # Public methods
    ###########################################################################

    def add_assigned_resource(self, resource_type: str,
                              value: Union[str, int, float, bool],
                              parameters: dict = None):
        """Add assigned resource to the processing block.

        Args:
            resource_type (str): Resource type
            value: Resource value
            parameters (dict, optional): Parameters specific to the resource

        """
        if parameters is None:
            parameters = dict()
        resources = DB.get_hash_value(self.key, 'resources_assigned')
        resources = ast.literal_eval(resources)
        resources.append(dict(type=resource_type, value=value,
                              parameters=parameters))
        DB.set_hash_value(self.key, 'resources_assigned', resources)

    def clear_assigned_resources(self):
        """Clear all resources assigned to the processing block."""
        DB.set_hash_value(self.key, 'resources_assigned', [])

    def remove_assigned_resource(self, resource_type: str,
                                 value: Union[str, int, float, bool] = None,
                                 parameters: dict = None):
        """Remove assigned resources from the processing block.

        All matching resources will be removed. If only type is specified
        all resources of the specified type will be removed.
        If value and/or parameters are specified they will be used
        for matching the resource to remove.

        Args:
            resource_type (str): Resource type
            value: Resource value
            parameters (dict, optional): Parameters specific to the resource

        """
        resources = DB.get_hash_value(self.key, 'resources_assigned')
        resources = ast.literal_eval(resources)
        new_resources = []
        for resource in resources:
            if resource['type'] != resource_type:
                new_resources.append(resource)
            elif value is not None and resource['value'] != value:
                new_resources.append(resource)
            elif parameters is not None and \
                    resource['parameters'] != parameters:
                new_resources.append(resource)
        DB.set_hash_value(self.key, 'resources_assigned', new_resources)

    def abort(self):
        """Abort the processing_block."""
        LOG.debug('Aborting PB %s', self._id)
        self.set_status('aborted')
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

    ###########################################################################
    # Private methods
    ###########################################################################

    def _mark_updated(self):
        """Update the updated timestamp."""
        timestamp = datetime.datetime.utcnow().isoformat()
        DB.set_hash_value(self.key, 'updated', timestamp)
