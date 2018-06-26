# -*- coding: utf-8 -*-
"""Utility to create a Scheduling Block in the Configuration database.

This is intended to very loosely emulate the function of the Processing
Controller Interface on receiving a new Scheduling Block Instance Create
Request command from TM.
"""

import random
import pprint
from app.mock_config_db_client import add_scheduling_block


def main():
    # Generate Scheduling Block Instance request data
    # (Note this only as the approximate structure of the actual schema
    # as defined in by the actual Configuration Service)
    scheduling_block_id = 'sb-{:03d}'.format(random.randint(0, 999))
    processing_blocks = []
    for i in range(random.randint(1, 3)):
        processing_block_id = '{}:pb-{:03d}'.format(scheduling_block_id, i)
        processing_blocks.append(dict(id=processing_block_id))
    scheduling_block = dict(id=scheduling_block_id,
                            processing_blocks=processing_blocks)

    # Call Mock client method to add a scheduling block to the
    # Configuration database
    add_scheduling_block(scheduling_block)
    print('Created scheduling block %s' % scheduling_block_id)
    pprint.pprint(scheduling_block)


if __name__ == '__main__':
    main()
