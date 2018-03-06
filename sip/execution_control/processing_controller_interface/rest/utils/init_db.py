# -*- coding: utf-8 -*-
"""Script to initialise the configuration database for testing

Adds a set of Scheduling Block Instances to a test / mock configuration
database.

Run with:
    python3 -m utils.init_db
"""
import random
from time import gmtime, strftime
import json


from app.mock_config_db_client import add_scheduling_block, \
                                      clear_db


def generate_scheduling_block_id(num_blocks, project='test'):
    """Generate a scheduling_block id"""
    _date = strftime("%Y%m%d", gmtime())
    _project = project
    for x in range(num_blocks):
        yield '{}-{}-sbi{:03d}'.format(_date, _project, x)


def main():
    """Main Function"""
    clear_db()
    for block_id in generate_scheduling_block_id(4):
        config = {
            "id": block_id,
            "sub_array_id": "",
            "processing_blocks": []
        }
        for p in range(random.randint(1, 3)):
            config['processing_blocks'].append({
                "id": "pb-{:02d}".format(p),
                "workflow": {"template": "", "stages": []}
            })
        print('-' * 40)
        print(json.dumps(config, indent=2))
        add_scheduling_block(config)


if __name__ == '__main__':
    main()
