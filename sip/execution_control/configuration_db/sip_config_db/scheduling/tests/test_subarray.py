# coding=utf-8
"""Tests of the Subarray API."""
import pytest

from .utils import add_mock_sbi_workflow_definitions
from .. import Subarray
from ... import ConfigDb
from ...utils.generate_sbi_config import generate_sbi_config

DB = ConfigDb()


def test_subarray_properties():
    """Test subarray object properties."""
    DB.flush_db()
    subarray = Subarray(0)
    assert not subarray.active
    assert subarray.id == 'subarray_00'

    subarray = Subarray('subarray_01')
    assert not subarray.active
    assert subarray.id == 'subarray_01'
    assert subarray.key == 'subarray:subarray_01'
    assert 'id' in subarray.config
    assert 'active' in subarray.config
    assert isinstance(subarray.config, dict)
    assert subarray.state == 'unknown'
    subarray.state = 'aborted'
    assert subarray.state == 'aborted'


def test_subarray_activate_deactivate():
    """Test activating and deactivating a subarray"""
    DB.flush_db()
    Subarray.subscribe('test_activate_deactivate')
    assert 'test_activate_deactivate' in Subarray.get_subscribers()
    subarray = Subarray(0)
    subarray.activate()
    assert subarray.active
    subarray.deactivate()
    assert not subarray.active


def test_subarray_configure_sbi():
    """Test configuring a new SBI on the subarray."""
    DB.flush_db()
    subarray = Subarray(0)

    sbi_config = generate_sbi_config()
    add_mock_sbi_workflow_definitions(sbi_config)

    with pytest.raises(RuntimeError,
                       match=r'Unable to add SBIs to inactive subarray!'):
        subarray.configure_sbi(sbi_config)

    subarray.activate()
    sbi = subarray.configure_sbi(sbi_config)

    assert sbi.subarray == 'subarray_00'

    sbi.clear_subarray()

    assert sbi.subarray == 'none'


def test_subarray_deactivate():
    """Test deactivating a subarray."""
    DB.flush_db()
    subarray = Subarray(0)

    sbi_config = generate_sbi_config()
    add_mock_sbi_workflow_definitions(sbi_config)

    subarray.activate()
    sbi = subarray.configure_sbi(sbi_config)

    assert sbi.subarray == 'subarray_00'

    subarray.deactivate()

    assert sbi.subarray == 'none'


def test_subarray_remove_sbi():
    """Test removing an SBI from a subarray."""
    DB.flush_db()
    subarray = Subarray(0)

    sbi_config = generate_sbi_config()
    add_mock_sbi_workflow_definitions(sbi_config)

    subarray.activate()
    sbi = subarray.configure_sbi(sbi_config)
    assert sbi.id in subarray.sbi_ids
    assert sbi.subarray == 'subarray_00'
    subarray.remove_sbi_id(sbi.id)
    assert sbi.subarray == 'none'
    assert not subarray.sbi_ids


def test_subarray_abort():
    """Test aborting a subarray."""
    DB.flush_db()
    subarray = Subarray(0)
    subarray.activate()

    sbi_config = generate_sbi_config()
    add_mock_sbi_workflow_definitions(sbi_config)

    subarray.configure_sbi(sbi_config)
    subarray.abort()

    # FIXME(BM) finish this test
