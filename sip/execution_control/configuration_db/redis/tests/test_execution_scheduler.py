# -*- coding: utf-8 -*-
"""
Script to test with the config client service is
working according to the requirement

# A sample schema, like what we'd get from json.load()
schema = {
    "type": "object",
    "properties": {
        "price": {"type": "number"},
        "name": {"type": "string"},
    },
}

# if no exception is raised by validate(), the instance is valid.
validate({'name': "myname", "price": 34.99}, schema)
"""

from jsonschema import validate
import simplejson as json
from flatten_json import flatten

import sys
import os


from app.config_api import ConfigDB


def main():
    db = ConfigDB()

    """ Testing Scheduling Block"""

    with open('utils/scheduling_block_data.json', 'r') as f:
        schema_data = f.read()
    scheduling_block = json.loads(schema_data)
    db.set_scheduling_block(scheduling_block)
    print("")

    # print("Delete scheduling block")
    # block_id = "180201-sched-blinst0"
    # db.delete_block( block_id)
    # print("scheduling block deleted")
    # print("")

    # print("Delete processing blocks")
    # processing_block_id = ["180201-sip-vis0", "180201-sip-vis1"]
    # db.delete_processing_block(processing_block_id)
    # print("processing block deleted")
    # print("")

    # print("Get Scheduling block Event")
    # scheduling_block = "scheduling_block"
    # event = db.get_event(scheduling_block)
    # print(event)
    # print("")
    #
    # print("Get Processing Block Event")
    # processing_block = "processing_block"
    # event = db.get_event(processing_block)
    # print(event)
    # print("")

    print("Update Status")
    scheduling_key = ["scheduling_block_instance", "180201-sched-blinst0"]
    processing_key = ["processing_block", "180201-sip-vis0"]
    value = "Testing"
    field = "status"
    db.update_status(processing_key, field , value)



if __name__ == '__main__':
    main()


