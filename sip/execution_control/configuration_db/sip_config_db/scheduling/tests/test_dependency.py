# -*- coding: utf-8 -*-
"""Tests of the Dependency object."""
from ..dependency import Dependency


def test_dependency_properties():
    """Test dependency object class properties."""
    config = dict(type='stage', value='stage-01', condition='complete')
    dependency = Dependency(config)
    assert dependency.type == 'stage'
    assert dependency.value == 'stage-01'
    assert dependency.condition == 'complete'
    assert dependency.config == config
    assert dependency.parameters == dict()
    assert repr(dependency) == \
        '{"type": "stage", "value": "stage-01", "condition": "complete"}'
