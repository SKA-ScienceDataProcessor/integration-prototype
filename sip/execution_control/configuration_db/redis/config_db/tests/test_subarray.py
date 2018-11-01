# coding=utf-8
"""Tests of the Subarray API."""
from ..subarray import Subarray
from ..config_db_redis import ConfigDb
from ..utils.generate_sbi_configuration import generate_sbi_config
from ..utils.load_test_workflow_definition import load_test_workflow_definition
from ..workflow_definitions import add_workflow_definition


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

    # TODO(BM) register workflow definitions for the SBI config
    sbi_config = generate_sbi_config()
    # FIXME(BM) HACK: Register test workflow definitions needed for this SBI.
    for i in range(len(sbi_config['processing_blocks'])):
        workflow_config = load_test_workflow_definition(
            sbi_config['processing_blocks'][i]['workflow']['id'],
            sbi_config['processing_blocks'][i]['workflow']['version']
        )
        add_workflow_definition(workflow_config, '')

    subarray.configure_sbi(sbi_config)


def test_subarray_abort():
    """Test aborting a subarray."""
    ConfigDb().flush_db()
    subarray = Subarray(0)
    subarray.activate()

    # TODO(BM) register workflow definitions for the SBI config
    sbi_config = generate_sbi_config()
    # FIXME(BM) HACK: Register test workflow definitions needed for this SBI.
    for i in range(len(sbi_config['processing_blocks'])):
        workflow_config = load_test_workflow_definition(
            sbi_config['processing_blocks'][i]['workflow']['id'],
            sbi_config['processing_blocks'][i]['workflow']['version']
        )
        add_workflow_definition(workflow_config, '')

    subarray.configure_sbi(sbi_config)
    subarray.abort()

    # TODO(BM) finish this test
