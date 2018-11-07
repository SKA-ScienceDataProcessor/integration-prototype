# coding=utf-8
"""Dependency data object."""
import json


class Dependency:
    """Dependency data object.

    Use to specify dependencies between PBs, workflow stages, and SBIs?
    """

    def __init__(self, config_dict: dict):
        """Create a dependency object from a DB dependency dict."""
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
    def condition(self) -> str:
        """Return the dependency condition."""
        return self._config.get('condition')

    @property
    def parameters(self) -> dict:
        """Return the dependency parameters."""
        return self._config.get('parameters', dict())

    @property
    def config(self) -> dict:
        """Return a dict representing the dependency."""
        return self._config

    def __repr__(self) -> str:
        """Return a unambiguous representation of the stage."""
        return json.dumps(self._config)
