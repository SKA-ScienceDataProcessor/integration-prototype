# coding=utf-8
"""Test the processing block events API."""
from random import choice

import redis

from ..scheduler.db import pb
from ..scheduler.db import sbi
from ..scheduler.db.generate import generate_sbi_config


def test_pb_events():
    """Test the PB events API"""
    print(redis.__version__)
    db_client = redis.StrictRedis()
    db_client.flushall()

    subscriber = 'pb_events_test'
    event_queue = pb.subscribe(subscriber)
    event_count = 4

    pb_id = '{:03d}'.format(0)
    pb.publish(pb_id, 'created')
    for _ in range(event_count):
        event_type = choice(['cancelled', 'queued', 'scheduled'])
        pb.publish(pb_id, event_type)

    # Note: When calling get() the oldest event is obtained first.
    events = []
    while len(events) != 5:
        event = event_queue.get()
        if event:
            assert event.id == 'pb_event_{:08d}'.format(len(events))
            assert event.data['pb_id'] == '000'
            events.append(event)

    # print(events[0])

    # TODO(BM) check the status of the aggregate after the event has been \
    # applied


def test_pb():
    """Test of the Processing Block functions."""
    db_client = redis.StrictRedis()
    db_client.flushall()

    for _ in range(2):
        sbi.add(generate_sbi_config())

    active = pb.get_active()
    assert len(active) == 6
    assert not pb.get_completed()
    assert not pb.get_cancelled()

    pb.cancel(active[0])

    assert len(pb.get_active()) == 5
    assert not pb.get_completed()
    assert len(pb.get_cancelled()) == 1

    events = pb.get_events(active[1])
    assert len(events) == 1

    # The PB that was cancelled should have two events
    events = pb.get_events(active[0])
    assert len(events) == 2
    assert pb.get_status(active[0]) == 'cancelled'
