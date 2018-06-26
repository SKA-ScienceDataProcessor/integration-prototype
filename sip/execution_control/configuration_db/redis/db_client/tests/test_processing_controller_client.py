# -*- coding: utf-8 -*-
r"""Tests of the Config db client API Processing Controller resources.

Run with:

    py.test --pylint --codestyle -s -v --durations=3 \
        --pylint-rcfile=../../../../.pylintrc \
        db_client/tests/test_processing_controller_client.py
"""
import pytest
import jsonschema

from ..processing_controller_client import ProcessingControllerDbClient


def test_create_client_object():
    """Test creating a client object."""
    db_client = ProcessingControllerDbClient()
    assert db_client is not None


def test_add_scheduling_block():
    """Test adding a scheduling block to the db"""
    db_client = ProcessingControllerDbClient()

    # Add a block with an invalid schema.
    with pytest.raises(jsonschema.ValidationError,
                       match=r'^\'id\' is a required'):
        db_client.add_scheduling_block({})

    # config = dict(id="20180531-sip-sbi001",
    #               sched_block_id="20180531-sip-sb001",
    #               sub_array_id="subarray-04",
    #               processing_blocks=[])
    # db_client.add_scheduling_block(config)
