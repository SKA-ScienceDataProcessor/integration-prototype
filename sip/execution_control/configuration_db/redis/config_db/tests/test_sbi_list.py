# -*- coding: utf-8 -*-
"""Tests of the Scheduling Block Instance List API."""
from ..config_db_redis import ConfigDb
from ..pb_list import ProcessingBlockList
from ..pb import ProcessingBlock
from ..sbi_list import SchedulingBlockInstanceList
from ..utils.generate_sbi_configuration import generate_sbi_config
from ..utils.workflow_definition_helpers import load_workflow_definition
from ..workflow_definitions import add_workflow_definition
from ..subarray import Subarray


def test_create_sbi_list_object():
    """Test creating a SBI list object."""
    sbi_list = SchedulingBlockInstanceList()
    assert sbi_list is not None


def test_add_sbi():
    """Test adding SBI data to the EC configuration DB."""
    ConfigDb().flush_db()
    Subarray(1).activate()

    sbi_config = generate_sbi_config(num_pbs=1)
    # HACK: Register test workflow definitions needed for this SBI.
    # TODO(BM) replace with utility function.
    for i in range(len(sbi_config['processing_blocks'])):
        workflow_config = load_workflow_definition(
            sbi_config['processing_blocks'][i]['workflow']['id'],
            sbi_config['processing_blocks'][i]['workflow']['version']
        )
        add_workflow_definition(workflow_config, '')

    sbi_list = SchedulingBlockInstanceList()
    sbi_events = sbi_list.subscribe('test_add_sbi')

    sbi = sbi_list.add(sbi_config, subarray_id='subarray_01')

    assert sbi_list.num_active == 1
    assert sbi_list.active[0] == sbi_config['id']

    assert sbi.id == sbi_config['id']
    assert sbi.num_processing_blocks == 1

    published = sbi_events.get_published_events()
    assert len(published) == 1
    assert published[0].type == 'status_changed'
    assert published[0].data['status'] == 'created'
    assert sbi.status == 'created'


def test_abort_sbi():
    """Test cancelling SBI data."""
    ConfigDb().flush_db()

    sbi_config = generate_sbi_config()
    # Register test workflow definitions needed for this SBI.
    for i in range(len(sbi_config['processing_blocks'])):
        workflow_config = load_workflow_definition(
            sbi_config['processing_blocks'][i]['workflow']['id'],
            sbi_config['processing_blocks'][i]['workflow']['version']
        )
        add_workflow_definition(workflow_config, '')

    subarray = Subarray(1)
    subarray.activate()

    sbi_list = SchedulingBlockInstanceList()
    pb_list = ProcessingBlockList()

    sbi_events = sbi_list.subscribe('test')
    pb_events = pb_list.subscribe('test')

    # Add the SBI to the database
    sbi = sbi_list.add(sbi_config, subarray.id)

    # Abort the SBI
    sbi.abort()

    # Check that the SBI has been aborted.
    published = sbi_events.get_published_events()
    assert published[-1].type == 'status_changed'
    assert published[-1].data['status'] == 'aborted'
    assert sbi.status == 'aborted'
    assert sbi_list.num_aborted == 1
    assert sbi_list.aborted[0] == sbi.id

    # Check that the PBs associated with the SBI have also been aborted
    published = pb_events.get_published_events()
    for i in range(sbi.num_processing_blocks):
        assert published[-1 - i].type == 'status_changed'
        assert published[-1 - i].data['status'] == 'aborted'
    assert sbi.num_processing_blocks == 3
    assert pb_list.num_aborted == 3
    for pb_id in sbi.processing_block_ids:
        assert pb_id in pb_list.aborted
        _pb = ProcessingBlock(pb_id)
        assert _pb.get_events()[-1].type == 'status_changed'
        assert _pb.get_events()[-1].data['status'] == 'aborted'


def test_get_active():
    """Test method to get active SBI"""
    ConfigDb().flush_db()
    sbi_list = SchedulingBlockInstanceList()
    pb_list = ProcessingBlockList()
    sbi_list.subscribe('test_add_sbi')
    sbi_config = generate_sbi_config()

    # Register test workflow definitions needed for this SBI.
    for i in range(len(sbi_config['processing_blocks'])):
        workflow_config = load_workflow_definition(
            sbi_config['processing_blocks'][i]['workflow']['id'],
            sbi_config['processing_blocks'][i]['workflow']['version']
        )
        add_workflow_definition(workflow_config, '')

    sbi = sbi_list.add(sbi_config)
    active_sbi = sbi_list.active
    assert active_sbi[0] == sbi_config['id']

    # Test active PB
    active_pb = pb_list.active
    assert active_pb[0] in sbi.processing_block_ids
