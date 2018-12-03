# -*- coding: utf-8 -*-
"""Tests of the Scheduling Block Instance List API."""
from .workflow_test_utils import add_test_sbi_workflow_definitions
from .. import ProcessingBlock, ProcessingBlockList, \
    SchedulingBlockInstanceList, Subarray
from ... import ConfigDb
from ...utils.generate_sbi_config import generate_sbi_config

DB = ConfigDb()


def test_sbi_list_create():
    """Test creating a SBI list object."""
    sbi_list = SchedulingBlockInstanceList()
    assert sbi_list is not None


def test_sbi_list_add_sbi():
    """Test adding SBI data to the EC configuration DB."""
    DB.flush_db()
    subarray = Subarray(1)
    subarray.activate()

    sbi_config = generate_sbi_config(num_pbs=1)
    add_test_sbi_workflow_definitions(sbi_config)

    sbi_list = SchedulingBlockInstanceList()
    sbi_events = sbi_list.subscribe('test_sbi_list_subscriber')

    sbi = sbi_list.add(sbi_config)

    assert sbi_list.num_active == 1
    assert sbi_list.active[0] == sbi_config['id']

    assert sbi.id == sbi_config['id']
    assert sbi.num_processing_blocks == 1

    published = sbi_events.get_published_events()
    assert len(published) == 1
    assert published[0].type == 'status_changed'
    assert published[0].data.get('status') == 'created'
    assert published[0].object_id == sbi.id
    assert published[0].object_type == sbi.type
    assert sbi.status == 'created'


def test_sbi_list_abort():
    """Test cancelling SBI data."""
    DB.flush_db()
    # import sip_logging
    # print('')
    # init_logger(log_level='DEBUG')

    sbi_config = generate_sbi_config()
    add_test_sbi_workflow_definitions(sbi_config)

    sbi_list = SchedulingBlockInstanceList()
    pb_list = ProcessingBlockList()

    sbi_events = sbi_list.subscribe('test_sbi_subscriber')
    pb_events = pb_list.subscribe('test_pb_subscriber')

    # Add the SBI to the database
    sbi = sbi_list.add(sbi_config)

    # Abort the SBI
    sbi.abort()

    # Check that the SBI has been aborted.
    sbi_events = sbi_events.get_published_events()
    assert sbi_events[-1].type == 'status_changed'
    assert sbi_events[-1].data['status'] == 'aborted'
    assert sbi.status == 'aborted'
    assert sbi_list.num_aborted == 1
    assert sbi_list.aborted[0] == sbi.id

    # Check that the PBs associated with the SBI have also been aborted
    pb_events = pb_events.get_published_events()
    for i in range(sbi.num_processing_blocks):
        assert pb_events[-1 - i].type == 'status_changed'
        assert pb_events[-1 - i].data['status'] == 'aborted'
    assert sbi.num_processing_blocks == 3
    assert pb_list.num_aborted == 3

    for pb_id in sbi.processing_block_ids:
        assert pb_id in pb_list.aborted
        pb = ProcessingBlock(pb_id)
        assert pb.get_events()[-1].type == 'status_changed'
        assert pb.get_events()[-1].data['status'] == 'aborted'


def test_sbi_list_get_active():
    """Test method to get active SBI"""
    DB.flush_db()
    sbi_list = SchedulingBlockInstanceList()
    pb_list = ProcessingBlockList()
    sbi_list.subscribe('test_add_sbi')
    sbi_config = generate_sbi_config()

    # Register test workflow definitions needed for this SBI.
    add_test_sbi_workflow_definitions(sbi_config)

    sbi = sbi_list.add(sbi_config)
    active_sbi = sbi_list.active
    assert active_sbi[0] == sbi_config['id']

    # Test active PB
    active_pb = pb_list.active
    assert active_pb[0] in sbi.processing_block_ids
