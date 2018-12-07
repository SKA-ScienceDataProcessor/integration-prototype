# -*- coding: utf-8 -*-
"""Unit tests of the Processing Block Queue."""
import random
import pytest

from scheduler.pb_queue import ProcessingBlockQueue


def test_simple_usage():
    """Tests simple usage of the Processing Block Queue."""
    # Obtain a queue object
    queue = ProcessingBlockQueue()

    # Fill the queue and save the set of test blocks added
    test_blocks = []
    pb_type = 'offline'
    for i in range(10):
        block_id = 'pb-{:03d}'.format(i)
        priority = random.randint(0, 10)
        test_blocks.append((priority, i, block_id, pb_type))
        queue.put(block_id, priority=priority)
        assert len(queue) == i + 1
        test_blocks.sort()
        for j, item in enumerate(queue):
            assert len(queue) == len(test_blocks)
            assert item == test_blocks[j]

    # print('')
    # print(queue)

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
    priority, _, _, _ = queue.get()
    while queue:
        item = queue.get()
        assert item[0] >= priority
        priority = item[0]

    assert not queue

    # # Check that calling get removes the highest priority item.
    # # assert queue.get() == item3
    # # item = queue.get()
    # # assert item == item1
    # # item = queue.get()
    # # assert item == item2
    # print(queue)
