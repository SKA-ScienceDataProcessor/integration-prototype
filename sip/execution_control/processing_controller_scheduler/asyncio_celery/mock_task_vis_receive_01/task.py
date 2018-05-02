# -*- coding: utf-8 -*-
"""Extremely simple mock workflow task."""
import logging
import sys
import json
import time
import enlighten


LOG = logging.getLogger('sip.mock_task_vis_receive_01')


def main():
    """Main function."""
    if len(sys.argv) != 2:
        LOG.critical('Expecting JSON string as first argument!')
        return

    config = json.loads(sys.argv[1])
    LOG.info('Running mock receive vis.')
    LOG.info('Received configuration: {0}'.format(config))
    LOG.info('Starting task')

    num_blocks = 400

    # Setup progress bar
    manager = enlighten.get_manager()
    progress = manager.counter(total=num_blocks, desc="task", unit='steps')

    for i in range(num_blocks):
        LOG.info("Receiving visibility block %s" % i)
        time.sleep(60 / num_blocks)
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
