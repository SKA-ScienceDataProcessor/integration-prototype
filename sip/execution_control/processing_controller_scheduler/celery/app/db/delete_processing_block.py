# -*- coding: utf-8 -*-
"""Utility to delete a Processing Block from the Configuration database.

This is intended to very loosely emulate the function of the Processing
Controller Interface on receiving a Processing Block delete / cancel
Request command from TM.
"""

import random
from app.mock_config_db_client import (get_scheduling_block_ids,
                                       get_scheduling_block,
                                       delete_processing_block)


def main():
    # Obtain list of scheduling blocks
    blocks = get_scheduling_block_ids()

    # Delete a random processing block
    if blocks:
        scheduling_block_id = random.choice(blocks)
        print(scheduling_block_id)
        config = get_scheduling_block(scheduling_block_id)
        processing_blocks = config.get('processing_blocks')
        if processing_blocks:
            processing_block_id = random.choice(processing_blocks).get('id')
            print(processing_block_id)
            delete_processing_block(scheduling_block_id, processing_block_id)
            print('Deleted Processing Block %s [Scheduling Block id = %s]' %
                  (processing_block_id, scheduling_block_id))


if __name__ == '__main__':
    main()
