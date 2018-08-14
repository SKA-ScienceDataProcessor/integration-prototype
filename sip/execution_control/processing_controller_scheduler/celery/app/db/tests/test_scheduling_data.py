# coding=utf-8
"""Test of EC Configuration database scheduling data API.

Note: this test requires that a Redis database instance has been started
and is accessible on localhost on the default Redis port. This can be started
with Docker using the command:

    docker run -d -p 6379:6379 --name=config_db redis:4.0.6-alpine

"""
import json
from random import randint

import redis

from ..generate import generate_sbi_config
from ..scheduling_data import add_sbi, cancel_sbi
from .. import events


def test_add_sbi():
    """Test adding SBI data to the EC configuration DB."""
    client = redis.StrictRedis()
    client.flushall()

    print('')
    pb_event_queue = events.subscribe('pb', 'test')
    sbi_event_queue = events.subscribe('sbi', 'test')

    sbi_config = generate_sbi_config(num_pbs=4)
    # print(json.dumps(sbi_config, indent=2))

    add_sbi(sbi_config)
    # TODO(BM) check that the SBI was created correctly and there is an event

    cancel_sbi(sbi_config['id'])
    # TODO(BM) check that the SBI cancel event was created correctly

    # event = pb_events.get()
    # print(event)
    # event = pb_events.get()
    # print(event)

    pb_events = pb_event_queue.get_published_events()
    pb_events[0].complete()

    pb_events = pb_event_queue.get_active_events()
    # for event in pb_events:
    #     print(event)
    # for event_id, event_data in pb_events.items():
    #     print('2', event_id, event_data)
    #
    # print(event_id)
    # set_event_complete(event_id)
