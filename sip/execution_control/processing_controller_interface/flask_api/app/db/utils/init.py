# -*- coding: utf-8 -*-
"""Script to initialise the configuration database for testing

Adds a set of Scheduling Block Instances to the configuration database

Run with:
    python3 -m app.db.utils.init_db
"""

import random
import sys
from time import gmtime, strftime
from pprint import pprint

from jsonschema import ValidationError

from ..client import ConfigDbClient


def _sched_block_ids(num_blocks, project):
    """Generate Scheduling Block instance ID"""
    for ii in range(num_blocks):
        _root = '{}-{}'.format(strftime("%Y%m%d", gmtime()), project)
        yield '{}-sb{:03d}'.format(_root, ii), \
              '{}-sbi{:03d}'.format(_root, ii)


def _scheduling_block_config(num_blocks=5, project='sip'):
    """Return a Scheduling Block Configuration dictionary"""
    for sb, sbi in _sched_block_ids(num_blocks, project):
        sub_array_id = 'subarray-{:02d}'.format(random.choice(range(5)))
        config = dict(sched_block_id=sb,
                      sched_block_instance_id=sbi,
                      sub_array_id=sub_array_id,
                      processing_blocks=[])
        yield config


def main():
    """Main function"""
    db = ConfigDbClient()
    print('Resetting database ...')
    db.clear()

    # Get the number of Scheduling Block Instances to generate
    num_blocks = int(sys.argv[1]) if len(sys.argv) == 2 else 3

    # Register Scheduling Blocks Instances with the DB
    try:
        for config in _scheduling_block_config(num_blocks):
            print('Creating Scheduling Block Instance, ID = %s' %
                  config['sched_block_instance_id'])
            db.set_scheduling_block(config)
    except ValidationError:
        raise


if __name__ == '__main__':
    main()
