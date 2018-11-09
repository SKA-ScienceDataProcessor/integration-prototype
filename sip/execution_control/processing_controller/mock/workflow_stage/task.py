# -*- coding: utf-8 -*-
"""Extremely simple mock workflow stage task."""
import logging
import sys
import json
import time
import enlighten


LOG = logging.getLogger('sip.mock_workflow_stage')


def main():
    """Run the workflow task."""
    if len(sys.argv) != 2:
        LOG.critical('Expecting JSON string as first argument!')
        return

    config = json.loads(sys.argv[1])
    LOG.info('Running mock workflow stage 01.')
    LOG.info('Received configuration: %s', config)
    LOG.info('Starting task')

    # Setup progress bar
    manager = enlighten.get_manager()
    progress = manager.counter(total=20, desc="task", unit='steps')

    i = 0
    start_time = time.time()
    duration = config.get('duration', 20)
    while time.time() - start_time <= duration:
        time.sleep(duration / 20)
        elapsed = time.time() - start_time
        LOG.info("%s", config.get('message', 'hello {}'.format(i + 1)))
        LOG.info("elapsed = %.2f s", elapsed)
        i += 1
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
