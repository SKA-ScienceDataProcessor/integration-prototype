# -*- coding: utf-8 -*-
"""Tests of the Processing Block Client API.

For instructions of how to run these tests see the README.md file in the
`sip/configuration_db/redis` folder.

"""
from random import choice
from ..sbi_client import SchedulingBlockDbClient
from ..pb_client import ProcessingBlockDbClient


def test_create_client_object():
    """Test creating a client object."""
    pb_db = ProcessingBlockDbClient()
    assert pb_db is not None


def test_pb_events():
    """Test the PB events API"""
    pb_db = ProcessingBlockDbClient()
    pb_db.clear()

    subscriber = 'pb_events_test'
    event_queue = pb_db.subscribe(subscriber)
    event_count = 4

    pb_id = '{:03d}'.format(0)
    pb_db.publish(pb_id, 'created')
    for _ in range(event_count):
        event_type = choice(['cancelled', 'queued', 'scheduled'])
        pb_db.publish(pb_id, event_type)

    # Note: When calling get() the oldest event is obtained first.
    events = []
    while len(events) != 5:
        event = event_queue.get()
        if event:
            assert event.id == 'pb_event_{:08d}'.format(len(events))
            assert event.data['pb_id'] == '000'
            events.append(event)


def test_get_active():
    """Test method to get active SBI"""

    sbi_db = SchedulingBlockDbClient()
    pb_db = ProcessingBlockDbClient()
    sbi_db.clear()
    sbi_db.subscribe('test_add_sbi')
    sbi_config = dict(id="20180110-sip-sbi000",
                      scheduling_block_id="20180101-sip-sb000",
                      sub_array_id="subarray000",
                      processing_blocks=[dict(id="sip-vis000",
                                              type='real-time')])

    # db.add_scheduling_block_instance(sbi_config)
    sbi_db.add_sbi(sbi_config)
    active_pb = pb_db.get_active()
    pb_id = pb_db.get_pb_ids(sbi_config['id'])
    assert active_pb[0] in pb_id
