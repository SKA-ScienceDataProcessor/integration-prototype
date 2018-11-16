# -*- coding: utf-8 -*-
"""Extremely simple mock workflow stage task."""
import json
import logging
import sys
import time

from _version import __version__
from sip_logging import init_logger


def main():
    """Run the workflow task."""
    log = logging.getLogger('sip.mock_workflow_stage')

    if len(sys.argv) != 2:
        log.critical('Expecting JSON string as first argument!')
        return

    config = json.loads(sys.argv[1])
    log.info('Running mock_workflow_stage (version: %s).', __version__)
    log.info('Received configuration: %s', json.dumps(config))
    log.info('Starting task')

    i = 0
    start_time = time.time()
    duration = config.get('duration', 20)
    while time.time() - start_time <= duration:
        time.sleep(duration / 20)
        elapsed = time.time() - start_time
        log.info("  %s %2i / 20 (elapsed %.2f s)",
                 config.get('message', 'Progress '),
                 i + 1, elapsed)
        i += 1

    log.info('Task complete!')


if __name__ == '__main__':
    init_logger()
    main()
