# coding=utf-8
"""High Level interface to workflow stage objects."""
import ast
import json
from typing import List
import datetime

from ._keys import PB_KEY
from ._scheduling_object import SchedulingObject
from .dependency import Dependency
from .resource import Resource
from .. import ConfigDb
from ..utils.datetime_utils import datetime_from_isoformat


DB = ConfigDb()


class WorkflowStage:
    """Workflow stage data object."""

    # Class attributes.
    _allowed_types = ['setup', 'cleanup', 'processing']
    _allowed_status = ['none',
                       'waiting_for_dependencies',
                       'waiting_for_resources',
                       'running',
                       'finished',
                       'aborted',
                       'failed']

    def __init__(self, pb_id: str, index: int):
        """Create a workflow stage object from a workflow stage dict."""
        self._pb_id = pb_id
        self._index = index
        self._config = self._load_config()

    @property
    def id(self) -> str:
        """Return the workflow stage Id."""
        return self._config.get('id')

    @property
    def pb_id(self) -> str:
        """Return the PB id that the workflow stage belongs to."""
        return self._pb_id

    @property
    def index(self) -> int:
        """Return the workflow stage index in the PB workflow list."""
        return self._index

    @property
    def version(self) -> str:
        """Return the workflow stage version."""
        return self._config.get('version')

    @property
    def type(self) -> str:
        """Return the workflow stage type."""
        return self._config.get('type')

    @property
    def status(self) -> str:
        """Return the workflow stage status."""
        # As status is a modifiable property, have to reload from the db.
        self._config = self._load_config()
        return self._config.get('status')

    @status.setter
    def status(self, value):
        """Set the workflow stage status."""
        # FIXME(BM) This is currently a hack because workflow stages
        #           don't each have their own db entry.
        pb_key = SchedulingObject.get_key(PB_KEY, self._pb_id)
        stages = DB.get_hash_value(pb_key, 'workflow_stages')
        stages = ast.literal_eval(stages)
        stages[self._index]['status'] = value
        timestamp = datetime.datetime.utcnow().isoformat()
        stages[self._index]['updated'] = timestamp
        DB.set_hash_value(pb_key, 'workflow_stages', stages)
        # FIXME(BM) This method should also publish a workflow status changed
        # event on the PB?!
        self._mark_updated()

    @property
    def timeout(self) -> int:
        """Return the workflow stage timeout."""
        return self._config.get('timeout', -1)

    @property
    def updated(self) -> datetime.datetime:
        """Return the last time the workflow stage was updated."""
        pb_key = SchedulingObject.get_key(PB_KEY, self._pb_id)
        stages = DB.get_hash_value(pb_key, 'workflow_stages')
        stages = ast.literal_eval(stages)
        return datetime_from_isoformat(stages[self._index]['updated'])

    @property
    def dependencies(self) -> List[Dependency]:
        """Return the workflow stage dependencies."""
        return self._config.get('dependencies')

    @property
    def resources_required(self) -> List[Resource]:
        """Return the workflow stage resources required."""
        return self._config.get('resources_required')

    @property
    def resources_assigned(self) -> List[Resource]:
        """Return the workflow stage resources assigned."""
        return self._config.get('resources_assigned')

    @property
    def compose_file(self) -> str:
        """Return the workflow stage Docker Compose template, if present."""
        return self._config.get('compose_file')

    @property
    def parameters(self) -> dict:
        """Return the workflow stage parameters dictionary."""
        return self._config.get('parameters')

    @property
    def args(self) -> str:
        """Return the workflow stage application argument template."""
        return self._config.get('args')

    @property
    def config(self) -> dict:
        """Return the workflow stage as a configuration dictionary."""
        return self._config

    def _load_config(self):
        """Load the workflow stage config from the database."""
        pb_key = SchedulingObject.get_key(PB_KEY, self._pb_id)
        stages = DB.get_hash_value(pb_key, 'workflow_stages')
        stages = ast.literal_eval(stages)
        return stages[self._index]

    def __repr__(self) -> str:
        """Return a unambiguous representation of the stage."""
        return json.dumps(self._config)

    def _mark_updated(self):
        """Update the workflow stage updated timestamp."""
        timestamp = datetime.datetime.utcnow().isoformat()
        pb_key = SchedulingObject.get_key(PB_KEY, self._pb_id)
        stages = DB.get_hash_value(pb_key, 'workflow_stages')
        stages = ast.literal_eval(stages)
        stages[self._index]['updated'] = timestamp
        DB.set_hash_value(pb_key, 'workflow_stages', stages)
