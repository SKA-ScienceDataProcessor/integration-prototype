# -*- coding: utf-8 -*-
"""Extremely simple mock workflow stage task."""
import json
import logging
import sys
import time

import enlighten

from sip_logging import init_logger


def main():
    """Run the workflow task."""
    log = logging.getLogger('sip.mock_workflow_stage')

    if len(sys.argv) != 2:
        log.critical('Expecting JSON string as first argument!')
        return

    config = json.loads(sys.argv[1])
    log.info('Running mock workflow stage 01.')
    log.info('Received configuration: %s', config)
    log.info('Starting task')

    # Setup progress bar
    manager = enlighten.get_manager()
    progress = manager.counter(total=20, desc="task", unit='steps')

    i = 0
    start_time = time.time()
    duration = config.get('duration', 20)
    while time.time() - start_time <= duration:
        time.sleep(duration / 20)
        elapsed = time.time() - start_time
        log.info("%s", config.get('message', 'hello {}'.format(i + 1)))
        log.info("elapsed = %.2f s", elapsed)
        i += 1
        progress.update()

    log.info('Task complete!')


if __name__ == '__main__':
    init_logger()
    main()
