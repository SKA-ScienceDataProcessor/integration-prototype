# -*- coding: utf-8 -*-
"""Module defining the Processing Block Scheduler Queue data model.

TODO(BM) need to consider linked Processing Blocks.
    See SDP scheduling model document:
    https://docs.google.com/document/d/14nsnMx69dsIl_4T4f1xmrh8HNjYdezdjlUQLxz829yI
"""
try:
    import threading
except ImportError:
    import dummy_threading as threading
import datetime

from .log import LOG


class ProcessingBlockQueue:
    """Processing Block Queue class.

    Stores a list of Processing block ID's ordered by priority.
    """

    def __init__(self):
        """Create a ProcessingBlockQueue object."""
        self._queue = []  # List of Processing Blocks in order of priority.
        self._index = 0
        self._mutex = threading.Lock()
        self._block_map = {}

    def put(self, block_id, priority, pb_type='offline'):
        """Add a Processing Block to the queue.

        Args:
            block_id (str):
            priority (int):
            pb_type (str):
        """
        # LOG.info("Processing Block ID %s", block_id)
        with self._mutex:
            added_time = datetime.datetime.utcnow().isoformat()
            entry = (priority, self._index, block_id, added_time, pb_type)
            self._index += 1
            if self._block_map.get(block_id) is not None:
                raise KeyError('ERROR: Block id "{}" already exists in '
                               'PC PB queue!'.
                               format(block_id))
            self._block_map[block_id] = entry
            LOG.debug("Adding PB %s to queue", block_id)
            self._queue.append(entry)
            self._queue.sort()  # Sort by priority followed by insertion order.
            self._queue.reverse()
            # LOG.info("Sorted Queue: %s", self._queue)

    def get(self):
        """Get the highest priority Processing Block from the queue."""
        with self._mutex:
            entry = self._queue.pop()
            del self._block_map[entry[2]]
            return entry

    def remove(self, block_id):
        """Remove a Processing Block from the queue.

        Args:
            block_id (str):
        """
        with self._mutex:
            entry = self._block_map[block_id]
            self._queue.remove(entry)

    def __len__(self):
        """Return the length of the queue."""
        with self._mutex:
            return len(self._queue)

    def __getitem__(self, i):
        """Return an item in the queue."""
        with self._mutex:
            return self._queue[i]

    def __str__(self):
        """Return a string representation of the queue."""
        with self._mutex:
            return '\n'.join('{:03d} | {:<5d} | {} | {}'.
                             format(i, entry[0], entry[2], entry[3])
                             for i, entry in enumerate(self._queue))
