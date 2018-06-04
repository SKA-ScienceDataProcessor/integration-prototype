# -*- coding: utf-8 -*-
"""Test config db client functions used by the Processing Controller Interface

Run with:
    pytest [-vv] [-s] app/tests/test_config_db_client.py
"""
import random
import re

import jsonschema
import pytest

from ..db.client import ConfigDb
from ..db.init import add_scheduling_blocks

DB = ConfigDb()


def test_scheduling_block_list():
    """Test functions handling the list of scheduling block instances"""
    # Clear the Database
    DB.clear()
    assert not DB.get_sched_block_instance_ids()

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
    with pytest.raises(jsonschema.ValidationError,
                       match="^'id' is a required"):
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
    # Reset the database adding 5 SBIs
    add_scheduling_blocks(5, clear=True)

    # Get the list of SBI ids.
    sbi_ids = DB.get_sched_block_instance_ids()

    # Get the block details for the first SBI
    # FIXME(BM) Consider replacing this function with one that isnt a generator
    sbi_id = sbi_ids[0]
    block = DB.get_block_details([sbi_id]).__next__()

    # Check that the ID matches what we asked for.
    assert block['id'] == sbi_id

    # Check that the SBI contains a list of processing blocks.
    assert 'processing_blocks' in block

    # FIXME(BM) Sort out the types - this should be a list!
    assert isinstance(block['processing_blocks'], str)


def test_processing_block_list():
    """Test functions handling the list of processing blocks"""
    # Make sure the database is clear before starting this test
    DB.clear()

    # There should be no processing blocks left in the database.
    pb_ids = DB.get_processing_block_ids()
    assert not pb_ids

    # Seed the database: Add a SBI with two processing blocks.
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

    # Check that the list of processing blocks in the database is of length 2
    pb_ids = DB.get_processing_block_ids()
    assert len(pb_ids) == 2

    # Add a 2nd SBI with 3 PBs
    config = dict(id="00000000-sip-sbi001",
                  sched_block_id="00000000-sip-sb000",
                  sub_array_id="subarray-00",
                  processing_blocks=[
                      dict(id="sip-pb03",
                           resources_requirement={},
                           workflow={}),
                      dict(id="sip-pb04",
                           resources_requirement={},
                           workflow={}),
                  ])
    DB.add_sched_block_instance(config)

    # There should now be 4 PBs in the database
    pb_ids = DB.get_processing_block_ids()
    assert len(pb_ids) == 4

    # Delete a PB
    DB.delete_processing_block('sip-pb01')

    # There should now be 3 PBs in the database.
    pb_ids = DB.get_processing_block_ids()
    assert len(pb_ids) == 3

    # Check that the PB we deleted no longer exists.
    assert 'sip-pb01' not in pb_ids


def test_processing_block():
    """Test functions getting details of a Processing Block."""
    add_scheduling_blocks(50, clear=True)
    pb_ids = DB.get_processing_block_ids()
    assert pb_ids
    pb_id = random.choice(pb_ids)

    # FIXME(BM) need to check condition where argument isnt a list
    # FIXME(BM) should not have to call __next__() ?!
    pb_config = DB.get_block_details([pb_id]).__next__()

    assert 'id' in pb_config
    assert 'workflow' in pb_config

    assert pb_config['id'] == pb_id


def test_sub_array_list():
    """Test functions getting information on the current set of sub-arrays."""
    # Reset the database adding 100 SBIs
    add_scheduling_blocks(50, clear=True)

    # Get the list of sub-array ids
    subarray_ids = DB.get_sub_array_ids()
    pattern = re.compile('^subarray-[0-1][0-5]')

    # There should be a maximum number of 16 sub-arrays defined
    assert len(subarray_ids) <= 16

    # Check that all the subarray id's conform to the naming pattern.
    for _id in subarray_ids:
        assert re.match(pattern, _id)


def test_sub_array():
    """Test functions getting information a given sub-array."""
    DB.clear()
    config = dict(id="00000000-sip-sbi000",
                  sched_block_id="00000000-sip-sb000",
                  sub_array_id="subarray-00",
                  processing_blocks=[])
    DB.add_sched_block_instance(config)
    config = dict(id="00000000-sip-sbi001",
                  sched_block_id="00000000-sip-sb000",
                  sub_array_id="subarray-01",
                  processing_blocks=[])
    DB.add_sched_block_instance(config)
    config = dict(id="00000000-sip-sbi002",
                  sched_block_id="00000000-sip-sb000",
                  sub_array_id="subarray-00",
                  processing_blocks=[])
    DB.add_sched_block_instance(config)

    subarray_ids = DB.get_sub_array_ids()
    assert subarray_ids[0] == 'subarray-00'
    assert subarray_ids[1] == 'subarray-01'

    # Get the SBI id's for subarray-00
    sbi_ids = DB.get_sub_array_sbi_ids(subarray_ids[0])
    assert len(sbi_ids) == 2
    assert sbi_ids[0] == '00000000-sip-sbi000'
    assert sbi_ids[1] == '00000000-sip-sbi002'

    # Get the SBI id's for subarray-02
    sbi_ids = DB.get_sub_array_sbi_ids(subarray_ids[1])
    assert len(sbi_ids) == 1
    assert sbi_ids[0] == '00000000-sip-sbi001'
