# -*- coding: utf-8 -*-
"""Test for the execution scheduler"""

import simplejson as json
from controller_client import SchedulingClient

def main():
    db = SchedulingClient()

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
    #
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

    print("Get Scheduling block")
    block_id = ["20180201-test-sbi000"]
    scheduling_block_instance = db.get_block_details(block_id)
    for instance in scheduling_block_instance:
        print(instance)
    print("")

    print("Get processing block")
    processing_block_id = ["sip-vis000", "sip-vis001"]
    processing_blocks = db.get_block_details(processing_block_id)
    for blocks in processing_blocks:
        print(blocks)
    print("")

    print("Get scheduling block and processing blocks")
    processing_block_id = ["20180201-test-sbi000", "sip-vis000", "sip-vis001"]
    processing_blocks = db.get_block_details(processing_block_id)
    for blocks in processing_blocks:
        print(blocks)
    print("")

    print("Update Value")
    block_id = "20180201-test-sbi000"
    field = "status"
    value = "Testing"
    db.update_value(block_id, field, value)
    print("Value Updated")
    print("")

    print("Get scheduling block ids")
    ids = db.get_scheduling_block_ids()
    for id in ids:
        print(id)
    print("")

    print("Get processing block ids")
    ids = db.get_processing_block_ids()
    for id in ids:
        print(id)
    print("")

    print("Get number of scheduling block ids")
    sched_num = db.get_num_scheduling_block_ids()
    print(sched_num)
    print("")

    print("Get number of processing block ids")
    process_num = db.get_num_processing_block_ids()
    print(process_num)
    print("")

    print("Get sub array ids")
    ids = db.get_sub_array_ids()
    for sub_array_ids in ids:
        print(sub_array_ids)
    print("")

    print("Get scheduling block id using sub array id")
    sub_array_id = 'subarray000'
    sched_id = db.get_scheduling_block_id_using_sub_array_id(sub_array_id)
    print(sched_id)

if __name__ == '__main__':
    main()


