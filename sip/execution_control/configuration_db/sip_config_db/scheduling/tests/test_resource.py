# -*- coding: utf-8 -*-
"""Tests of the Resource object."""
from ..resource import Resource


def test_resource_properties():
    """Test resource object class properties."""
    resource = Resource(dict(type='nodes'))
    assert resource.type == 'nodes'
    assert resource.config == dict(type='nodes')
    assert repr(resource) == '{"type": "nodes"}'
