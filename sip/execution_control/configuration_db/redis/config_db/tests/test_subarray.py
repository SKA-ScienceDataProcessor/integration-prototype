# coding=utf-8
"""Tests of the Subarray API."""
from ..config_db_redis import ConfigDb
from ..subarray import Subarray
from ..utils.generate_sbi_configuration import generate_sbi_config
from ..utils.workflow_test_utils import add_test_sbi_workflow_definitions


def test_subarray_initialise():
    """Test initialising the subarray list."""
    ConfigDb().flush_db()
    subarray = Subarray(0)
    assert not subarray.is_active()


def test_subarray_activate_deactivate():
    """Test activating and deactivating a subarray"""
    ConfigDb().flush_db()
    Subarray.subscribe('test_activate_deactivate')
    subarray = Subarray(0)
    subarray.activate()
    assert subarray.is_active()
    subarray.deactivate()
    assert not subarray.is_active()


def test_subarray_configure_sbi():
    """Test configuring a new SBI on the subarray."""
    ConfigDb().flush_db()
    subarray = Subarray(0)
    subarray.activate()

    sbi_config = generate_sbi_config()
    add_test_sbi_workflow_definitions(sbi_config)

    subarray.configure_sbi(sbi_config)


def test_subarray_abort():
    """Test aborting a subarray."""
    ConfigDb().flush_db()
    subarray = Subarray(0)
    subarray.activate()

    sbi_config = generate_sbi_config()
    add_test_sbi_workflow_definitions(sbi_config)

    subarray.configure_sbi(sbi_config)
    subarray.abort()

    # FIXME(BM) finish this test
