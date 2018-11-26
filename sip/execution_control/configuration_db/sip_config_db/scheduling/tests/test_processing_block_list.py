# -*- coding: utf-8 -*-
"""Tests of the Processing Block List API.

The Processing Block List API gives functions for interfacing with the
list of PBs known to the configuration database.
"""
import time
from random import choice

import pytest

from .workflow_test_utils import add_test_sbi_workflow_definitions
from ..processing_block_list import ProcessingBlockList
from ..scheduling_block_instance import SchedulingBlockInstance
from ... import DB
from ...utils.generate_sbi_config import generate_sbi_config


def test_create_pb_list_object():
    """Test creating a PB list object."""
    pb_list = ProcessingBlockList()
    assert pb_list is not None


def test_pb_list_get_active():
    """Test method to get active PBs"""
    DB.flush_db()

    sbi_config = generate_sbi_config()
    add_test_sbi_workflow_definitions(sbi_config)

    sbi = SchedulingBlockInstance.from_config(sbi_config)
    active = ProcessingBlockList().active
    assert active[0] in sbi.get_pb_ids()


def test_pb_events():
    """Test the PB events API"""
    DB.flush_db()
    pb_list = ProcessingBlockList()

    subscriber = 'test_pb_events_subscriber'
    event_queue = pb_list.subscribe(subscriber)
    event_count = 4

    pb_object_id = 'PB-{:03d}'.format(0)
    pb_list.publish(pb_object_id, event_type='created')
    event_types = ['created', 'cancelled', 'queued', 'scheduled']
    for _ in range(event_count):
        event_type = choice(event_types)
        pb_list.publish(pb_object_id, event_type)

    # Note: When calling get() the oldest event is obtained first.
    events = []
    start_time = time.time()
    while len(events) != 5:
        event = event_queue.get()
        if event:
            assert event.id == 'pb_event_{:08d}'.format(len(events))
            assert event.object_id == pb_object_id
            assert event.object_type == 'pb'
            assert event.type in event_types
            events.append(event)
        if time.time() - start_time >= 2:
            pytest.fail('Unable to get PB events.')
