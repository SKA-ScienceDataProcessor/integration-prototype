# coding=utf-8
"""Unit tests of the workflow definition interface."""
import os
import json

import redis

from ..workflow_definitions import (add_workflow_definition,
                                    get_workflow_definition,
                                    get_workflow_definitions,
                                    register_workflow_definition,
                                    delete_workflow_definitions)

DB = redis.StrictRedis(decode_responses=True)


def test_add_workflow_definition():
    """Test adding a workflow definition."""
    # Delete all existing workflow definitions
    keys = DB.keys("workflow_definitions:*")
    for key in keys:
        DB.delete(key)

    # Load the test workflow definition
    workflows_dir = os.path.join(os.path.dirname(__file__), 'data',
                                 'workflows')
    workflow_path = os.path.join(workflows_dir, 'test_workflow.json')
    with open(workflow_path, 'r') as file:
        workflow_definition = json.loads(file.read())

    # Set workflow definition templates directory
    templates_root = os.path.join(workflows_dir, 'templates')
    add_workflow_definition(workflow_definition, templates_root)

    # Load the workflow definition and test against expected result
    wfd = get_workflow_definition(workflow_definition["id"],
                                  workflow_definition["version"])

    assert wfd == workflow_definition


def test_get_workflow_definitions():
    """Test retrieving workflow definitions."""
    workflows = get_workflow_definitions()
    assert 'test_workflow' in workflows
    assert len(workflows['test_workflow']) == 1

    register_workflow_definition("workflow1", "1.0.0")
    register_workflow_definition("workflow1", "1.0.1")
    register_workflow_definition("workflow1", "1.0.2")

    workflows = get_workflow_definitions()
    assert 'test_workflow' in workflows
    assert len(workflows['test_workflow']) == 1
    assert 'workflow1' in workflows
    assert len(workflows['workflow1']) == 3
    assert "1.0.0" in workflows["workflow1"]

    delete_workflow_definitions()
