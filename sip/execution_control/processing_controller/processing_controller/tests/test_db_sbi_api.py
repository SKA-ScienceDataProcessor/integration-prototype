# coding=utf-8
"""Test of EC Configuration database scheduling data API.

Note: this test requires that a Redis database instance has been started
and is accessible on localhost on the default Redis port. This can be started
with Docker using the command:

    docker run -d -p 6379:6379 --name=config_db redis:4.0.6-alpine

"""
import redis

from ..scheduler.db.generate import generate_sbi_config
from ..scheduler.db import sbi
from ..scheduler.db import pb


def test_add_sbi():
    """Test adding SBI data to the EC configuration DB."""
    client = redis.StrictRedis()
    client.flushall()

    sbi_event_queue = sbi.subscribe('test_add_sbi')
    sbi_config = generate_sbi_config(num_pbs=4)

    sbi.add(sbi_config)
    sbi_data = sbi.get_config(sbi_config['id'])
    assert sbi_data['id'] == sbi_config['id']
    assert len(sbi_data['processing_block_ids']) == 4
    events = sbi_event_queue.get_published_events()
    assert len(events) == 1
    assert events[0].data['type'] == 'created'
    status = sbi.get_status(sbi_data['id'])
    assert status == 'created'


def test_cancel_sbi():
    """Test cancelling SBI data."""
    client = redis.StrictRedis()
    client.flushall()

    # Add a SBI event to the database.
    sbi_events = sbi.subscribe('test_add_sbi')
    pb_events = pb.subscribe('test_add_sbi')
    num_pbs = 3
    for _ in range(2):
        sbi.add(generate_sbi_config(num_pbs=num_pbs))

    # Get the list of SBIs from the database.
    sbi_list = sbi.get_active()
    sbi_id = sbi_list[0]

    sbi.cancel(sbi_id)

    # Check that the SBI has been canceled.
    events = sbi_events.get_published_events()
    assert events[-1].type == 'cancelled'
    status = sbi.get_status(sbi_id)
    assert status == 'cancelled'
    cancelled_list = sbi.get_cancelled()
    assert len(cancelled_list) == 1
    assert cancelled_list[0] == sbi_id

    # Check that the PBs associated with the SBI have also been canceled
    events = pb_events.get_published_events()
    for i in range(num_pbs):
        assert events[-1 - i].type == 'cancelled'
    pb_ids = sbi.get_pb_ids(sbi_id)
    assert len(pb_ids) == num_pbs
    cancelled_list = pb.get_cancelled()
    assert len(cancelled_list) == num_pbs
    for pb_id in pb_ids:
        assert pb_id in cancelled_list
        assert pb.get_events(pb_id)[-1].type == 'cancelled'
