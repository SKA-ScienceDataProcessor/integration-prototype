# coding=utf-8
"""High Level interface to workflow stage objects."""
import json
from typing import List
import ast

from .dependency import Dependency
from .resource import Resource
from .config_db_redis import ConfigDb
from .scheduling_object import SchedulingObject

# FIXME(BM) it would be nice for this to be able to import ProcessingBlock
# but it breaks import rules as ProcessingBlock also imports this module.
PB_AGGREGATE_TYPE = 'pb'

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
        pb_key = SchedulingObject.get_key(PB_AGGREGATE_TYPE, self._pb_id)
        stages = DB.get_hash_value(pb_key, 'workflow_stages')
        stages = ast.literal_eval(stages)
        stages[self._index]['status'] = value
        DB.set_hash_value(pb_key, 'workflow_stages', stages)
        # FIXME(BM) This method should also publish a workflow status changed
        # event on the PB?!

    @property
    def timeout(self) -> int:
        """Return the workflow stage timeout."""
        return self._config.get('timeout', -1)

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
    def ee_config(self) -> dict:
        """Return the workflow stage Execution Engine configuration."""
        return self._config.get('ee_config')

    @property
    def compose_template(self) -> str:
        """Return the workflow stage Docker Compose template, if present."""
        if 'compose_template' in self.ee_config:
            return self.ee_config['compose_template']
        return ''

    @property
    def app_config(self) -> dict:
        """Return the workflow application configuration."""
        return self._config.get('app_config')

    @property
    def args_template(self) -> str:
        """Return the workflow stage application argument template."""
        if 'args_template' in self.app_config:
            return self.app_config['args_template']
        return ''

    @property
    def config(self) -> dict:
        """Return the workflow stage as a configuration dictionary."""
        return self._config

    def _load_config(self):
        """Load the workflow stage config from the database."""
        pb_key = SchedulingObject.get_key(PB_AGGREGATE_TYPE, self._pb_id)
        stages = DB.get_hash_value(pb_key, 'workflow_stages')
        stages = ast.literal_eval(stages)
        return stages[self._index]

    def __repr__(self) -> str:
        """Return a unambiguous representation of the stage."""
        return json.dumps(self._config)
