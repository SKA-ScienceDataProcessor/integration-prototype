# -*- coding: utf-8 -*-
"""Test for the execution scheduler"""

import simplejson as json
import logging
import sys
from controller_client import controllerClient

def main():
    db = controllerClient()

    print("***Test Execution Scheduler***")

    with open('utils/scheduling_block_data.json', 'r') as f:
        block_data = f.read()
    scheduling_block = json.loads(block_data)
    db.set_scheduling_block(scheduling_block)

    # print("Delete scheduling block")
    # block_id = "180201-sched-blinst0"
    # db.delete_scheduling_block(block_id)
    # print("scheduling block deleted")
    # print("")

    # print("Delete processing blocks")
    # processing_block_id = ["180201-sip-vis0", "180201-sip-vis1"]
    # db.delete_processing_block(processing_block_id)
    # print("processing block deleted")
    # print("")

    print("Get Scheduling block Event")
    event_block = "scheduling_block"
    event = db.get_latest_event(event_block)
    print(event)
    print("")

    print("Get Processing Block Event")
    processing_block = "processing_block"
    event = db.get_latest_event(processing_block)
    print(event)
    print("")

if __name__ == '__main__':
    main()


