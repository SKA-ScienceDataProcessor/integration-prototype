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
from typing import re

from jsonschema import validate
import simplejson as json
from flatten_json import flatten

import sys
import os


from app.config_client_api import ConfigClient


def main():
    """ Testing Scheduling Block"""
    with open('schema/scheduling_block_instance_data.json', 'r') as f:
        schema_data = f.read()
    sched_block_instance_schema = json.loads(schema_data)

    redis_api = ConfigClient()

    redis_api.set_schedule_block_instance(sched_block_instance_schema)

    event = redis_api.get_scheduling_block_event()

    # print(event)
    #
    # print(event['type'])
    # print(event['id'])
    #
    # print("Getting scheduling block instance using id")
    #
    # block_id = "180201-sched-blinst0"
    #
    #
    # redis_api.delete_scheduling_block(block_id)
    #
    # event1 = redis_api.get_scheduling_block_event()
    #
    # print(event1)
    #
    # print(event1['type'])
    # print(event1['id'])

    # print(block)

    # event1 = redis_api.get_processing_blocks_event()
    #
    # print(event1['type'])
    # print(event1['id'])

    # delete = input("Do you want to delete the block instance = ")
    #
    # scheduling_bl_inst_id = "180201-sched-blinst0"
    # proc_id = ["180201-sip-vis0", "180201-sip-vis1"]
    #
    # # For Testing
    # # for i in proc_id:
    # #     print(i)
    #
    # if delete != "no":
    #     redis_api.remove_sched_block_instance(scheduling_bl_inst_id)
    #     print("Removed the instance")
    ########################################################################################

        # scheduling_bl_inst_id = "180201-sched-blinst0"
        # proc_id = ["180201-sip-vis0", "180201-sip-vis1"]
        # processing_id = "180201-sip-vis0"
        # stage = "service_stage"
        #
        # status = 'UPDATE'
        #
        # # Update status of the scheduling block instance
        # redis_api.update_status(scheduling_bl_inst_id, status, processing_id, status, stage)

    #######################################################################################

    # """Testing Master Controller"""
    #
    # with open('schema/init_data.json', 'r') as f:
    #     schema_data = f.read()
    # master_controller_data = json.loads(schema_data)
    #
    # # print(master_controller_data)
    #
    # redis_api = ConfigClient()
    # redis_api.set_init_data(master_controller_data)
    #
    # # Get the status
    # # service = 'master_controller'
    # service = 'system_services'
    #
    # sub_service = 'logging'
    # # sub_service = 'local_sky_model'
    # state = 'state'
    #
    # state = redis_api.get_state(service, state, sub_service=sub_service)
    # print(state)
    #
    # # Update the status
    # service1 = 'master_controller'
    # service_s = 'sdp_services'
    #
    # sub_service1 = 'local_sky_model'
    # # sub_service = 'local_sky_model'
    # new_state = 'stopped'
    # new_state1 = 'off'
    # master_controller_state= 'TANGO_state'
    #
    # state = redis_api.update_state(service1, new_state1, m_state=master_controller_state)
    # state = redis_api.update_state(service_s, new_state, sub_service=sub_service1)
    #
    #
    # # Get service list
    #
    # list = redis_api.get_service_list()
    #
    # print(list)
    #
    # for i in list:
    #     print(i)
    #
    # print("Get service from the service list")
    # print("")
    #
    # name = "sdp_services.data_queue"
    # enabled = redis_api.get_service_from_list(name)
    #
    # for i in enabled:
    #     print(i)







    #########################################################################################

    # with open('/home/nijinjose123/integration-prototype/'
    #           'sip/execution_control/configuration_db/'
    #           'schema/top_level_schema.json', 'r') as f:
    #     schema_top_data = f.read()
    # schema_top = json.loads(schema_top_data)
    #
    # #print(schema_top)
    #
    # validate(schema_top, schema)
    #
    # print('Sucessful')
    #
    # flat = flatten(schema_top)
    #
    # print(flat)


if __name__ == '__main__':
    main()


