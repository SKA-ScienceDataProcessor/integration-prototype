# -*- coding: utf-8 -*-
"""Script to initialise the configuration database for testing

Adds a set of Scheduling Block Instances to the configuration database

Run with:
    python3 -m app.db.utils.init_db
"""

import logging
import random
import sys
from time import gmtime, strftime

from jsonschema import ValidationError

from .client import ConfigDbClient

LOG = logging.getLogger('SIP.PCI.DB.utils')


def _scheduling_block_ids(num_blocks, project):
    """Generate Scheduling Block instance ID"""
    for i in range(num_blocks):
        _root = '{}-{}'.format(strftime("%Y%m%d", gmtime()), project)
        yield '{}-sb{:03d}'.format(_root, i), \
              '{}-sbi{:03d}'.format(_root, i)


def _generate_processing_blocks(start_id, min_blocks=0, max_blocks=4):
    """Generate a number of Processing Blocks"""
    processing_blocks = []
    num_blocks = random.randint(min_blocks, max_blocks)
    for i in range(start_id, start_id + num_blocks):
        _id = 'sip-pb{:03d}'.format(i)
        block = dict(id=_id, resources_requirement={}, workflow={})
        processing_blocks.append(block)
    return processing_blocks


def _scheduling_block_config(num_blocks=5, project='sip'):
    """Return a Scheduling Block Configuration dictionary"""
    pb_id = 0
    for sb_id, sbi_id in _scheduling_block_ids(num_blocks, project):
        sub_array_id = 'subarray-{:02d}'.format(random.choice(range(5)))
        config = dict(id=sbi_id,
                      sched_block_id=sb_id,
                      sub_array_id=sub_array_id,
                      processing_blocks=_generate_processing_blocks(pb_id))
        pb_id += len(config['processing_blocks'])
        yield config


def main():
    """Main function"""
    _log = logging.getLogger('SIP.EC.PCI.CDB')
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter(
        '%(name)-20s | %(filename)-15s | %(levelname)-5s | %(message)s'))
    _log.addHandler(_handler)
    _log.setLevel(logging.DEBUG)

    db_client = ConfigDbClient()
    LOG.info('Resetting database ...')
    db_client.clear()

    # Get the number of Scheduling Block Instances to generate
    num_blocks = int(sys.argv[1]) if len(sys.argv) == 2 else 3

    # Register Scheduling Blocks Instances with the DB
    try:
        for config in _scheduling_block_config(num_blocks):
            LOG.info('Creating SBI %s with %i PBs.', config['id'],
                     len(config['processing_blocks']))
            db_client.add_scheduling_block(config)
    except ValidationError:
        raise


if __name__ == '__main__':
    main()
