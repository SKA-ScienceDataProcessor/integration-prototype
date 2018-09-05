# -*- coding: utf-8 -*-
"""Tests of the Config db client API Processing Controller resources.

For instructions of how to run these tests see the README.md file in the
`sip/configuration_db/redis` folder.

TODO(BM)
    - Add methods to genereate ids (eg. sub_array_ids etc)
    - Update sub-array interfaces to respect time

"""
import datetime

from random import choice
from ..sbi_client import SchedulingBlockDbClient
from ..pb_client import ProcessingBlockDbClient


def test_create_client_object():
    """Test creating a client object."""
    sbi_db = SchedulingBlockDbClient()
    assert sbi_db is not None

    pb_db = ProcessingBlockDbClient()
    assert pb_db is not None


def test_add_sbi():
    """Test adding SBI data to the EC configuration DB."""
    sbi_db = SchedulingBlockDbClient()
    sbi_db.clear()

    sbi_event_queue = sbi_db.subscribe('test_add_sbi')

    # TODO (NJT) Need to fix scheduling block instance data generator
    # generate_data = generate_sbi_config(num_pbs=4)
    # print(generate_data)
    sbi_config = dict(id="20180110-sip-sbi000",
                      scheduling_block_id="20180101-sip-sb000",
                      sub_array_id="subarray000",
                      processing_blocks=[dict(id="sip-vis000",
                                              type='real-time')])

    # db.add_scheduling_block_instance(sbi_config)
    sbi_db.add_sbi(sbi_config)
    sbi_data = sbi_db.get_block_details(sbi_config['id'])

    assert sbi_data['id'] == sbi_config['id']
    assert len(sbi_data['processing_block_ids']) == 1
    events = sbi_event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].data['type'] == 'created'
    status = sbi_db.get_status(sbi_data['id'])
    assert status == 'created'


def test_cancel_sbi():
    """Test cancelling SBI data."""
    sbi_db = SchedulingBlockDbClient()
    pb_db = ProcessingBlockDbClient()
    sbi_db.clear()

    # Add a SBI event to the database.
    sbi_events = sbi_db.subscribe('test_add_sbi')
    pb_events = pb_db.subscribe('test_add_sbi')
    num_pbs = 3

    # TODO (NJT) Need to fix generator
    # for _ in range(2):
    #     sbi.add(generate_sbi_config(num_pbs=num_pbs))
    sbi_config = dict(id="20180110-sip-sbi000",
                      scheduling_block_id="20180101-sip-sb000",
                      sub_array_id="subarray000",
                      processing_blocks=[dict(id="sip-vis000",
                                              type='real-time'),
                                         dict(id="sip-vis001",
                                              type='real-time'),
                                         dict(id="sip-vis002",
                                              type='real-time')])

    sbi_db.add_sbi(sbi_config)

    # Get the list of SBIs from the database.
    sbi_list = sbi_db.get_active()
    sbi_id = sbi_list[0]
    sbi_db.cancel_sbi(sbi_id)

    # Check that the SBI has been canceled.
    events = sbi_events.get_published_events()
    assert events[-1].type == 'cancelled'
    status = sbi_db.get_status(sbi_id)
    assert status == 'cancelled'
    cancelled_list = sbi_db.get_cancelled()
    assert len(cancelled_list) == 1
    assert cancelled_list[0] == sbi_id

    # Check that the PBs associated with the SBI have also been canceled
    events = pb_events.get_published_events()
    for i in range(num_pbs):
        assert events[-1 - i].type == 'cancelled'
    pb_ids = pb_db.get_pb_ids(sbi_id)
    assert len(pb_ids) == num_pbs
    cancelled_list = pb_db.get_cancelled()
    assert len(cancelled_list) == num_pbs
    for pb_id in pb_ids:
        assert pb_id in cancelled_list
        assert pb_db.get_events(pb_id)[-1].type == 'cancelled'


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

    # TODO(BM) check the status of the aggregate after the event has been \
    # applied


def test_get_sbi_id():
    """Test method to generate a valid SBI id."""
    sbi_db = SchedulingBlockDbClient()
    sbi_db.clear()

    sbi_id = sbi_db.get_sbi_id()
    now = datetime.datetime.utcnow()
    assert sbi_id == '{}-sip-sbi000'.format(now.strftime('%Y%m%d'))

    sbi_id = sbi_db.get_sbi_id(project='test')
    now = datetime.datetime.utcnow()
    assert sbi_id == '{}-test-sbi000'.format(now.strftime('%Y%m%d'))

    sbi_id = sbi_db.get_sbi_id(date='20180101')
    assert sbi_id == '20180101-sip-sbi000'

    sbi_id = sbi_db.get_sbi_id(datetime.datetime(2018, 3, 2))
    assert sbi_id == '20180302-sip-sbi000'
