# -*- coding: utf-8 -*-
"""Unit tests of the Processing Block Queue."""
import random
import datetime
import sys
import pytest

from scheduler.pb_queue import ProcessingBlockQueue


def test_scheduler_pb_queue_simple_usage():
    """Tests simple usage of the Processing Block Queue."""
    # Obtain a queue object
    queue = ProcessingBlockQueue()

    # Fill the queue and save the set of test blocks added
    test_blocks = []
    pb_ids = []
    pb_type = 'offline'
    for i in range(13):
        block_id = 'pb-{:03d}'.format(i)
        pb_ids.append(block_id)
        priority = random.randint(0, 10)
        added_time = datetime.datetime.utcnow().isoformat()
        test_blocks.append((priority, sys.maxsize-i, block_id, pb_type,
                            added_time))
        queue.put(block_id, priority=priority)
        assert len(queue) == i + 1
        test_blocks.sort()
        test_blocks.reverse()
        for j, item in enumerate(queue):
            assert len(queue) == len(test_blocks)
            assert item[0] == test_blocks[j][0]
            assert item[1] == test_blocks[j][1]
            assert item[2] == test_blocks[j][2]
            assert item[3] == test_blocks[j][3]
            assert isinstance(item[4], str)

    # Delete a block somewhere in the middle of the queue
    queue_length = len(queue)
    block_id = queue[len(queue) // 2][2]
    queue.remove(block_id)
    assert len(queue) == queue_length - 1

    # Test that adding a duplicate PB raises an error
    block_id = queue[len(queue) // 2][2]
    with pytest.raises(KeyError):
        queue.put(block_id, 0)

    # Empty the queue
    while queue:
        pb_id = queue.get()
        assert pb_id in pb_ids

    assert not queue
