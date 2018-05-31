# -*- coding: utf-8 -*-
"""Test for the execution scheduler"""

import os

import simplejson as json

from ..processing_controller_client import ProcessingControllerDbClient


# class DbClientTests(unittest.TestCase):
#     def setUp(self):
#         self._db = ProcessingControllerClient()
#         self._log = logging.getLogger("DbClientTests.testPath")
#
#     def tearDown(self):
#         """Executed after each test."""

# if __name__ == '__main__':
#     # Deletes all the data in the database
#     r = redis.Redis()
#     r.flushdb()
#
#     # Populates the database with initial data
#     os.system("python3 -m utils.set_initial_data")
#
#     logging.basicConfig(stream=sys.stderr)
#     logging.getLogger("DbClientTests.testPath").setLevel(logging.DEBUG)
#     unittest.main()


def test_events(db_client):
    """Test Scheduling Block Instance and Processing Block events."""
    print("Get Scheduling block Event")
    event_block = "scheduling_block"
    event = db_client.get_latest_event(event_block)
    print(event)

    print("Get Processing Block Event")
    processing_block = "processing_block"
    event = db_client.get_latest_event(processing_block)
    print(event)


def test_get_block_details(db_client):
    """Test returning details of a SBI or PB"""
    print("Get Scheduling block")
    block_id = ["20180201-test-sbi000"]
    scheduling_block_instance = db_client.get_block_details(block_id)
    for instance in scheduling_block_instance:
        print(instance)

    print("Get Scheduling block which has no processing block")
    block_id = ["20180201-test-sbi001"]
    scheduling_block_instance = db_client.get_block_details(block_id)
    for instance in scheduling_block_instance:
        print(instance)

    print("Get processing block")
    p_blk_ids = ["sip-vis000", "sip-vis001", "sip-vis001"]
    block_ids = db_client.get_processing_block_ids()
    _blocks = [b for b in db_client.get_block_details(p_blk_ids, sort=True)]
    print(_blocks)
    assert len(block_ids) == len(_blocks)

    print("Get scheduling block and processing blocks")
    processing_block_id = ["20180201-test-sbi000", "sip-vis000", "sip-vis001"]
    processing_blocks = db_client.get_block_details(processing_block_id)
    for blocks in processing_blocks:
        print(blocks)


def test_get_ids(db_client):
    """Test asking for various ids (PB, SBI, Subarray) from the db."""
    print("Get number of scheduling block ids")
    num_blocks = db_client.get_num_scheduling_block_ids()
    print(num_blocks)

    print("Get number of processing block ids")
    num_blocks = db_client.get_num_processing_block_ids()
    print(num_blocks)

    print("Get scheduling block ids")
    for _id in db_client.get_sched_block_instance_ids():
        print(_id)

    print("Get processing block ids")
    for _id in db_client.get_processing_block_ids():
        print(_id)

    print("Get sub array ids")
    for _id in db_client.get_sub_array_ids():
        print(_id)

    print("Get scheduling block id using sub array id")
    sub_array_id = 'subarray000'
    _id = db_client.get_sub_array_sbi_ids(sub_array_id)
    print(_id)


def main():
    """."""
    db_client = ProcessingControllerDbClient()

    print("***Test Configuration Db client for the Processing Controller***")

    file_path = os.path.dirname(__file__)
    config_path = os.path.join(file_path, '..', 'utils',
                               'scheduling_block_data.json')
    with open(config_path, 'r') as file:
        block_data = file.read()
    scheduling_block = json.loads(block_data)
    db_client.add_scheduling_block(scheduling_block)

    # print("Delete scheduling block")
    # block_id = "20180201-test-sbi000"
    # db.delete_scheduling_block(block_id)
    # print("scheduling block deleted")

    # print("Delete scheduling block which has no processing block")
    # block_id = "20180201-test-sbi001"
    # db.delete_scheduling_block(block_id)
    # print("scheduling block deleted")

    test_events(db_client)

    print("Delete processing blocks")
    processing_block_id = "sip-vis001"
    db_client.delete_processing_block(processing_block_id)
    print("processing block deleted")

    test_get_block_details(db_client)

    print("Update Value")
    block_id = "20180201-test-sbi000"
    field = "status"
    value = "Testing"
    db_client.update_value(block_id, field, value)
    print("Value Updated")

    test_get_ids(db_client)

    print("Clear the database")
    db_client.clear()


if __name__ == '__main__':
    main()
