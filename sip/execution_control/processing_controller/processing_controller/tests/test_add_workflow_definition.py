# coding=utf-8
"""Unit tests of the workflow definition interface."""
import os
import json

import redis

from config_db.workflow_definitions import get_workflow_definition
from ..utils.pbc_workflow_definition import add_workflow_definitions

DB = redis.StrictRedis(decode_responses=True)


# for testing
# ConfigDb().flush_db()
# default_data_path = join(dirname(__file__), '../data')
#
# print(default_data_path)
# # data_path = sys.argv[1] if len(sys.argv) > 1 else default_data_path
# add_workflow_definitions(join(default_data_path, 'workflows'))

def test_add_workflow_definition():
    """Test adding a workflow definition."""
    # Delete all existing workflow definitions
    keys = DB.keys("workflow_definitions:*")
    for key in keys:
        DB.delete(key)

    # TODO(NJT): Need to fix this unit test
    # Load the test workflow definition
    workflows_dir = os.path.join(os.path.dirname(__file__), 'data')
    workflow_path = os.path.join(workflows_dir, 'mock_workflow_test.json')
    with open(workflow_path, 'r') as file:
        workflow_definition = json.loads(file.read())
    # Load the workflow definition and test against expected result
    # # # add_workflow_definitions(join(default_data_path, 'workflows'))
    add_workflow_definitions(workflows_dir)
    wfd = get_workflow_definition(workflow_definition["id"],
                                  workflow_definition["version"])


    assert wfd == workflow_definition

    # # Load the test workflow definition
    # workflows_dir = os.path.join(os.path.dirname(__file__), 'data',
    #                              'workflows')
    # print("------------")
    # print(workflows_dir)
    # workflow_path = os.path.join(workflows_dir, 'mock_workflow_test.json')
    # print("############-------")
    # print(workflow_path)
    # with open(workflow_path, 'r') as file:
    #     workflow_definition = json.loads(file.read())
    #
    # # # add_workflow_definitions(join(default_data_path, 'workflows'))
    # add_workflow_definitions(workflows_dir)
    # #
    # # Load the workflow definition and test against expected result
    # wfd = get_workflow_definition(workflow_definition["id"],
    #                               workflow_definition["version"])
    #
    # print(wfd)
    #
    # print("#################")
    #
    # print(workflow_definition)

    # assert wfd == workflow_definition
