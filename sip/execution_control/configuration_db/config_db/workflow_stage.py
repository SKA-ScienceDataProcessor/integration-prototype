# coding=utf-8
"""High Level interface to workflow stage objects."""
import json
from typing import List

from .dependency import Dependency
from .resource import Resource


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

    def __init__(self, config_dict: dict):
        """Create a workflow stage object from a workflow stage dict."""
        self._config = config_dict

    @property
    def id(self) -> str:
        """Return the workflow stage Id."""
        return self._config.get('id')

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
        return self._config.get('status')

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

    def __repr__(self) -> str:
        """Return a unambiguous representation of the stage."""
        return json.dumps(self._config)
