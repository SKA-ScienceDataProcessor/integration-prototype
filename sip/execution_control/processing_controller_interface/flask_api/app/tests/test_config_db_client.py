# -*- coding: utf-8 -*-
"""Test config db client functions used by the Processing Controller Interface

Run with:
    pytest [-vv] [-s] app/tests/test_config_db_client.py
"""
import pytest
import jsonschema
import random

from ..db.client import ConfigDb
from ..db.init import add_scheduling_blocks


DB = ConfigDb()


def test_scheduling_block_list():
    """Test functions handling the list of scheduling block instances"""
    # Clear the Database
    DB.clear()

    assert len(DB.get_sched_block_instance_ids()) == 0

    # Add some scheduling blocks and check the number of blocks has increased.
    add_scheduling_blocks(5, clear=True)
    assert len(DB.get_sched_block_instance_ids()) == 5

    # Add some more scheduling blocks
    add_scheduling_blocks(5, clear=False)
    assert len(DB.get_sched_block_instance_ids()) == 10

    # Delete a scheduling block and check that it is gone.
    sbi_ids = DB.get_sched_block_instance_ids()
    sbi_id = random.choice(sbi_ids)
    DB.delete_sched_block_instance(sbi_id)
    assert len(DB.get_sched_block_instance_ids()) == 9
    assert sbi_id not in DB.get_sched_block_instance_ids()

    # Add a scheduling block instance with invalid config
    with pytest.raises(jsonschema.ValidationError, match="^'id' is a required"):
        config = {}
        DB.add_sched_block_instance(config)
    assert len(DB.get_sched_block_instance_ids()) == 9

    # Add a scheduling block instance with valid config
    config = dict(id="20180531-sip-sbi001",
                  sched_block_id="20180531-sip-sb001",
                  sub_array_id="subarray-04",
                  processing_blocks=[])
    DB.add_sched_block_instance(config)
    assert len(DB.get_sched_block_instance_ids()) == 10


def test_scheduling_block():
    """Test functions getting details of a Scheduling Block Instance"""


def test_processing_block_list():
    """Test functions handling the list of processing blocks"""
    DB.clear()

    pb_ids = DB.get_processing_block_ids()
    assert len(pb_ids) == 0

    config = dict(id="00000000-sip-sbi000",
                  sched_block_id="00000000-sip-sb000",
                  sub_array_id="subarray-00",
                  processing_blocks=[
                      dict(id="sip-pb01",
                           resources_requirement={},
                           workflow={}),
                      dict(id="sip-pb02",
                           resources_requirement={},
                           workflow={}),
                  ])
    DB.add_sched_block_instance(config)
    pb_ids = DB.get_processing_block_ids()
    assert len(pb_ids) == 2

    DB.delete_processing_block('sip-pb01')
    pb_ids = DB.get_processing_block_ids()
    assert len(pb_ids) == 1
    assert 'sip-pb01' not in pb_ids


def test_processing_block():
    """Test functions getting details of a Processing Block."""
    add_scheduling_blocks(50, clear=True)
    pb_ids = DB.get_processing_block_ids()
    assert len(pb_ids) > 0
    pb_id = random.choice(pb_ids)

    # FIXME(BM) need to check condition where argument isnt a list
    # FIXME(BM) should not have to call __next__() ?!
    pb_config = DB.get_block_details([pb_id]).__next__()

    assert 'id' in pb_config
    assert 'workflow' in pb_config

    assert pb_config['id'] == pb_id


def test_sub_array_list():
    """Test functions getting information on the current set of sub-arrays."""


def test_sub_array():
    """Test functions getting information a given sub-array."""
