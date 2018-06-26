# -*- coding: utf-8 -*-
"""Unit tests of the Processing Block Queue

Run with:
    python3 -m pytest tests/test_processing_block_queue.py
"""

from app.queue import ProcessingBlockQueue
import random


def test_simple_usage():
    """Tests simple usage of the Processing Block Queue"""

    queue = ProcessingBlockQueue()
    test_blocks = []

    # Fill the queue
    for i in range(10):
        block_id = 'pb-{:03d}'.format(i)
        priority = random.randint(0, 10)
        test_blocks.append((priority, i, block_id))
        queue.put(block_id, priority=priority)
        assert len(queue) == i + 1
        test_blocks.sort()
        for j in range(len(queue)):
            assert len(queue) == len(test_blocks)
            assert queue[j] == test_blocks[j]

    # Delete a block somewhere in the middle of the queue
    queue_length = len(queue)
    block_id = queue[len(queue) // 2][2]
    queue.remove(block_id)
    assert len(queue) == queue_length - 1

    # TODO(BM) test that inserting a duplicate block raises an error
    # block_id = queue[len(queue) // 2][2]
    # queue.put(block_id, 0)

    # Empty the queue
    priority, _, _ = queue.get()
    while len(queue) > 0:
        item = queue.get()
        assert item[0] >= priority
        priority = item[0]

    assert len(queue) == 0


    #

    #
    #
    # # Check that calling get removes the highest priority item.
    # # assert queue.get() == item3
    # # item = queue.get()
    # # assert item == item1
    # # item = queue.get()
    # # assert item == item2

    print(queue)


if __name__ == '__main__':
    test_simple_usage()
