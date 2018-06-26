# -*- coding: utf-8 -*-
"""Utility to delete a Scheduling Block in the Configuration database.

This is intended to very loosely emulate the function of the Processing
Controller Interface on receiving a Scheduling Block Instance delete / cancel
Request command from TM.
"""

import random
from app.mock_config_db_client import (get_scheduling_block_ids,
                                       delete_scheduling_block)


def main():
    # Obtain list of scheduling blocks
    blocks = get_scheduling_block_ids()

    # Delete a random scheduling block
    if blocks:
        block_id = random.choice(blocks)
        delete_scheduling_block(block_id)
        print('Deleted Scheduling Block %s' % block_id)


if __name__ == '__main__':
    main()
