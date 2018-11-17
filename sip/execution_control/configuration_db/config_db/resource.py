# coding=utf-8
"""Resource data object."""
import json


class Resource:
    """Resource data object.

    Use to specify resources required or assigned to PBs and
    workflow stages.
    """

    def __init__(self, config_dict: dict):
        """Create a resource object from a resource dictionary."""
        self._config = config_dict

    @property
    def type(self) -> str:
        """Return the dependency type."""
        return self._config.get('type')

    @property
    def value(self) -> str:
        """Return the dependency value."""
        return self._config.get('value')

    @property
    def parameters(self) -> dict:
        """Return the dependency parameters."""
        return self._config.get('parameters', dict())

    @property
    def config(self) -> dict:
        """Return the resource configuration dict."""
        return self._config

    def __repr__(self) -> str:
        """Return a unambiguous representation of the resource."""
        return json.dumps(self._config)
