

from jsonschema import validate
import simplejson as json
from flatten_json import flatten

import sys
import os
import ast
import unittest


from app.config_api import ConfigDB


def main():

    """Testing Master Controller"""
    print("Generic Database API Test")

    db = ConfigDB()

    print("Get SDP State")
    key = ['execution_control', 'master_controller']
    field = ['SDP_state']
    value = db.get_state(key, field)
    print(value)
    print("")

    print("Get the length of the service list")
    length_key = ['execution_control', 'master_controller', 'service_list']
    print(db.get_list_length(length_key))
    print("")

    print("Get the full list")
    list = db.get_list(length_key)
    for j in list:
        print(j)
        print(j['name'])
        print(j['enabled'])
    print("")

    print("Get the nth element from the list")
    n_element = db.get_element(length_key, 1)
    print(n_element)
    print("")

    print("Test return 0 if no nth element is found")
    n_element = db.get_element(length_key, 7)
    print(n_element)
    print("")

    print("Add element to the service list")
    # dict = {
    #           'name': 'sdp_services.data_queue',
    #           'enabled': 'False'
    #        }
    # db.add_element(length_key, dict)
    test_add_element = db.get_element(length_key, 0)
    print(test_add_element)
    print(test_add_element['name'])
    print(test_add_element['enabled'])
    print("")

    print("Converts a value from the database to a service path list")
    print("Updates the state of a service")
    element = db.get_element(length_key, 3)
    v_path = element['name']
    state = 'state'
    value = "stopped"
    db.update_state(v_path, state, value)
    print("")


if __name__ == '__main__':
    main()




