# -*- coding: utf-8 -*-
"""Extremely simple mock workflow task."""
import logging
import sys
import json
import time
import enlighten


LOG = logging.getLogger('sip.mock_task_vis_ingest_processing_01')


def main():
    """Run the workflow task."""
    if len(sys.argv) != 2:
        LOG.critical('Expecting JSON string as first argument!')
        return

    config = json.loads(sys.argv[1])
    LOG.info('Running mock workflow task 01.')
    LOG.info('Received configuration: %s', config)
    LOG.info('Starting task')

    # Setup progress bar
    manager = enlighten.get_manager()
    progress = manager.counter(total=20, desc="task", unit='steps')

    for i in range(20):
        LOG.info("Processing step %i", i)
        time.sleep(5/20)
        progress.update()

    LOG.info('Task complete!')


if __name__ == '__main__':
    _HANDLER = logging.StreamHandler()
    _HANDLER.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d - '
                                            '%(name)s - '
                                            '%(levelname).1s - '
                                            '%(message)s',
                                            '%Y-%m-%d %H:%M:%S'))
    LOG.addHandler(_HANDLER)
    LOG.setLevel(logging.DEBUG)

    main()
