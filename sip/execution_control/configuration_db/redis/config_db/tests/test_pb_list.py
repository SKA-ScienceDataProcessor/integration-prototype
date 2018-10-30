# -*- coding: utf-8 -*-
"""Tests of the Processing Block API.

For instructions of how to run these tests see the README.md file in the
`sip/configuration_db/redis` folder.
"""
from random import choice
import json

from ..sbi_list import SchedulingBlockInstanceList
from ..pb_list import ProcessingBlockList
from ..workflow_definitions import register_workflow_definition
from ..utils.generate_sbi_configuration import generate_sbi_config


def test_create_client_object():
    """Test creating a PB list object."""
    pb_list = ProcessingBlockList()
    assert pb_list is not None


def test_pb_events():
    """Test the PB events API"""
    pb_list = ProcessingBlockList()
    pb_list.clear()

    subscriber = 'pb_events_test'
    event_queue = pb_list.subscribe(subscriber)
    event_count = 4

    pb_id = '{:03d}'.format(0)
    pb_list.publish(pb_id, 'created')
    for _ in range(event_count):
        event_type = choice(['cancelled', 'queued', 'scheduled'])
        pb_list.publish(pb_id, event_type)

    # Note: When calling get() the oldest event is obtained first.
    events = []
    while len(events) != 5:
        event = event_queue.get()
        if event:
            assert event.id == 'pb_event_{:08d}'.format(len(events))
            assert event.data['pb_id'] == '000'
            events.append(event)


def test_get_active():
    """Test method to get active PBs"""
    sbi_list = SchedulingBlockInstanceList()
    pb_list = ProcessingBlockList()
    sbi_list.clear()
    # sbi.subscribe('test_add_sbi')
    sbi_config = generate_sbi_config()

    # FIXME(BM) this is a hack to avoid registering workflows properly...
    for pb in sbi_config['processing_blocks']:
        _id = pb['workflow']['id']
        _version = pb['workflow']['version']
        register_workflow_definition(_id, _version)

    sbi_list.add(sbi_config)
    active = pb_list.get_active()

    pb_ids = sbi_list.get_pb_ids(sbi_config['id'])
    assert active[0] in pb_ids


def test_get_workflow_stages():
    """Test method to get specific stage details in workflow"""
    sbi_list = SchedulingBlockInstanceList()
    pb_list = ProcessingBlockList()
    pb_list.clear()
    sbi_config = generate_sbi_config(num_pbs=1)

    # HACK: Register workflow definitions needed for this SBI.
    for i in range(len(sbi_config['processing_blocks'])):
        _id = sbi_config['processing_blocks'][i]['workflow']['id']
        _version = sbi_config['processing_blocks'][i]['workflow']['version']
        register_workflow_definition(_id, _version)

    # Add the SBI to the database.
    sbi_list.add(sbi_config)

    pb_ids = sbi_list.get_pb_ids(sbi_config['id'])

    # TODO Check workflow keys have been added to the PB from the workflow
    # definition.

    # for pb_id in pb_ids:
    #     assigned_resources = pb_list.get_workflow_stage(
    #         pb_id, 'assigned_resources')
    #     assert assigned_resources['volume'] == "mount"
    #     assert assigned_resources['cpu'] == 1
    #     resource_requirement = pb_list.get_workflow_stage(
    #         pb_id, 'resource_requirement')
    #     assert resource_requirement['storage_type'] == "hot"
    #     assert resource_requirement['cpu'] == 2


# def test_add_assigned_resources():
#     """Test method to add assigned resources data"""
#     sbi_list = SchedulingBlockInstanceList()
#     pb_list = ProcessingBlockList()
#     pb_list.clear()
#     sbi_config = generate_sbi_config()
#     assigned_resources_data = dict(storage_type="hot", volume="mount", cpu=1)
#     sbi_list.add(sbi_config)
#     pb_ids = pb_list.get_pb_ids(sbi_config['id'])
#     for pb_id in pb_ids:
#         pb_list.add_assigned_resources(pb_id, assigned_resources_data)
#         assigned_resources = pb_list.get_workflow_stage(
#             pb_id, 'assigned_resources')
#         assert assigned_resources['volume'] == "mount"
#         assert assigned_resources['cpu'] == 1
#
#     # SBI config with assigned resources field in workflow
#     new_config = dict(id="20180110-sip-sbi001",
#                       scheduling_block_id="20180101-sip-sb001",
#                       sub_array_id="subarray000",
#                       processing_blocks=[dict(id="sip-vis001",
#                                               type='real-time',
#                                               workflow=[dict(
#                                                   resource_requirement=dict(
#                                                       storage_type="hot",
#                                                       volume="mount",
#                                                       cpu=2))])])
#     new_resources_data = dict(storage_type="cold", volume="mount", cpu=5)
#     sbi_list.add(new_config)
#     pb_ids = pb_list.get_pb_ids(new_config['id'])
#     for pb_id in pb_ids:
#         pb_list.add_assigned_resources(pb_id, new_resources_data)
#         assigned_resources = pb_list.get_workflow_stage(
#             pb_id, 'assigned_resources')
#         assert assigned_resources['storage_type'] == "cold"
#         assert assigned_resources['cpu'] == 5
