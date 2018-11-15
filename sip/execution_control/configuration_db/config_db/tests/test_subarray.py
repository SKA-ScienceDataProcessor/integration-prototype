# coding=utf-8
"""Tests of the Subarray API."""
from .workflow_test_utils import add_test_sbi_workflow_definitions
from ..subarray import DB, Subarray
from ..utils.generate_sbi_configuration import generate_sbi_config


def test_subarray_initialise():
    """Test initialising the subarray list."""
    DB.flush_db()
    subarray = Subarray(0)
    assert not subarray.active


def test_subarray_activate_deactivate():
    """Test activating and deactivating a subarray"""
    DB.flush_db()
    Subarray.subscribe('test_activate_deactivate')
    subarray = Subarray(0)
    subarray.activate()
    assert subarray.active
    subarray.deactivate()
    assert not subarray.active


def test_subarray_configure_sbi():
    """Test configuring a new SBI on the subarray."""
    DB.flush_db()
    subarray = Subarray(0)
    subarray.activate()

    sbi_config = generate_sbi_config()
    add_test_sbi_workflow_definitions(sbi_config)

    subarray.configure_sbi(sbi_config)


def test_subarray_abort():
    """Test aborting a subarray."""
    DB.flush_db()
    subarray = Subarray(0)
    subarray.activate()

    sbi_config = generate_sbi_config()
    add_test_sbi_workflow_definitions(sbi_config)

    subarray.configure_sbi(sbi_config)
    subarray.abort()

    # FIXME(BM) finish this test
