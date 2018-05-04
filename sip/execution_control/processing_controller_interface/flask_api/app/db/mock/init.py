# -*- coding: utf-8 -*-
"""Script to initialise the configuration database for testing

Adds a set of Scheduling Block Instances to a test / mock configuration
database.

Run with:
    python3 -m utils.init_db
"""
import json
import random
import sys
from time import gmtime, strftime

from ..client import add_scheduling_block, clear_db


def generate_scheduling_block_id(num_blocks, project='test'):
    """Generate a scheduling_block id"""
    _date = strftime("%Y%m%d", gmtime())
    _project = project
    for x in range(num_blocks):
        yield '{}-{}-sbi{:03d}'.format(_date, _project, x)


def main():
    """Main Function"""
    num_blocks = int(sys.argv[1]) if len(sys.argv) == 2 else 3
    clear_db()
    for block_id in generate_scheduling_block_id(num_blocks=num_blocks,
                                                 project='sip'):
        config = {
            "id": block_id,
            "sub_array_id": str(random.choice(range(3))),
            "processing_blocks": []
        }
        for p in range(random.randint(1, 3)):
            config['processing_blocks'].append({
                "id": "{}:pb{:03d}".format(block_id, p),
                "workflow": {
                    "name": "{}".format(random.choice(['vis_ingest_01',
                                                       'dask_ical_01',
                                                       'dask_maps_01'])),
                    "template": {},
                    "stages": []
                }
            })
        print('-' * 40)
        print(json.dumps(config, indent=2))
        add_scheduling_block(config)


if __name__ == '__main__':
    main()
