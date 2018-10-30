# -*- coding: utf-8 -*-
"""Tests of the Scheduling Block Instance List API.

For instructions of how to run these tests see the README.md file in the
`sip/configuration_db/redis` folder.

TODO(BM)
    - Update sub-array interfaces to respect time
"""
import datetime

from ..sbi_list import SchedulingBlockInstanceList
from ..pb_list import ProcessingBlockList
from ..workflow_definitions import (register_workflow_definition,
                                    add_workflow_definition)
from ..utils.generate_sbi_configuration import (generate_sbi_config)


def test_create_sbi_list_object():
    """Test creating a SBI list object."""
    sbi_list = SchedulingBlockInstanceList()
    assert sbi_list is not None


def test_add_sbi():
    """Test adding SBI data to the EC configuration DB.

    When a SBI is added to the database ... TODO description of the test!

    """
    sbi_list = SchedulingBlockInstanceList()
    sbi_list.clear()
    sbi_event_queue = sbi_list.subscribe('test_add_sbi')
    num_pbs = 1
    sbi_config = generate_sbi_config(num_pbs=num_pbs)

    # HACK: Register workflow definitions needed for this SBI.

    for i in range(len(sbi_config['processing_blocks'])):
        workflow_config = dict(
            id=sbi_config['processing_blocks'][i]['workflow']['id'],
            version=sbi_config['processing_blocks'][i]['workflow']['version'],
            stages=[dict(id='stage1',
                         type='setup',
                         version='test',
                         resources_required=[],
                         ee_config={},
                         app_config={}),
                    dict(id='stage2',
                         type='processing',
                         version='test',
                         resources_required=[],
                         ee_config={},
                         app_config={})
                    ]
        )
        add_workflow_definition(workflow_config, '')

    sbi_list.add(sbi_config, subarray_id='subarray_01')
    sbi_data = sbi_list.get_block_details(sbi_config['id'])

    assert sbi_data['id'] == sbi_config['id']
    assert len(sbi_data['processing_block_ids']) == num_pbs
    events = sbi_event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].data['type'] == 'created'
    status = sbi_list.get_status(sbi_data['id'])
    assert status == 'created'


def test_abort_sbi():
    """Test cancelling SBI data."""
    sbi_list = SchedulingBlockInstanceList()
    pb_list = ProcessingBlockList()
    sbi_list.clear()

    # Add a SBI event to the database.
    sbi_events = sbi_list.subscribe('test_add_sbi')
    pb_events = pb_list.subscribe('test_add_sbi')
    num_pbs = 3
    sbi_config = generate_sbi_config()

    # HACK: Register workflow definitions needed for this SBI.
    for i in range(len(sbi_config['processing_blocks'])):
        _id = sbi_config['processing_blocks'][i]['workflow']['id']
        _version = sbi_config['processing_blocks'][i]['workflow']['version']
        register_workflow_definition(_id, _version)

    sbi_list.add(sbi_config)

    # Get the list of SBIs from the database.
    sbi_id = sbi_list.get_active()[0]
    sbi_list.abort(sbi_id)

    # Check that the SBI has been canceled.
    events = sbi_events.get_published_events()
    assert events[-1].type == 'aborted'
    status = sbi_list.get_status(sbi_id)
    assert status == 'aborted'
    aborted_list = sbi_list.get_aborted()
    assert len(aborted_list) == 1
    assert aborted_list[0] == sbi_id

    # Check that the PBs associated with the SBI have also been canceled
    events = pb_events.get_published_events()
    for i in range(num_pbs):
        assert events[-1 - i].type == 'aborted'
    pb_ids = sbi_list.get_pb_ids(sbi_id)
    assert len(pb_ids) == num_pbs
    aborted_list = pb_list.get_aborted()
    assert len(aborted_list) == num_pbs
    for pb_id in pb_ids:
        assert pb_id in aborted_list
        assert pb_list.get_events(pb_id)[-1].type == 'aborted'


def test_get_active():
    """Test method to get active SBI"""
    sbi_list = SchedulingBlockInstanceList()
    pb_list = ProcessingBlockList()
    sbi_list.clear()
    sbi_list.subscribe('test_add_sbi')
    sbi_config = generate_sbi_config()

    # HACK: Register workflow definitions needed for this SBI.
    for i in range(len(sbi_config['processing_blocks'])):
        _id = sbi_config['processing_blocks'][i]['workflow']['id']
        _version = sbi_config['processing_blocks'][i]['workflow']['version']
        register_workflow_definition(_id, _version)

    sbi_list.add(sbi_config)
    active_sbi = sbi_list.get_active()
    assert active_sbi[0] == sbi_config['id']

    # Test active PB
    active_pb = pb_list.get_active()
    pb_id = sbi_list.get_pb_ids(sbi_config['id'])
    assert active_pb[0] in pb_id


def delete_sbis():
    """TODO"""
    sbi_list = SchedulingBlockInstanceList()
    sbi_list.delete_all()
