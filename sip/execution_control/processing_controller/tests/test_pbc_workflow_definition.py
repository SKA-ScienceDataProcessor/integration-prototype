# coding=utf-8
"""Unit tests of the workflow definition interface."""
import os
import redis

from config_db.workflow_definitions import get_workflow_definitions
from ..utils.pbc_workflow_definition import add_workflow_definitions

DB = redis.StrictRedis(decode_responses=True)


def test_add_workflow_definition():
    """Test adding a workflow definition."""
    # Delete all existing workflow definitions
    keys = DB.keys("workflow_definitions:*")
    for key in keys:
        DB.delete(key)

    # TODO(NJT): Need to fix this unit test
    # Load the test workflow definition
    workflows_dir = os.path.join(os.path.dirname(__file__), 'data',
                                 'workflows')
    add_workflow_definitions(workflows_dir)
    workflows = get_workflow_definitions()
    assert 'mock_workflow' in workflows
    assert len(workflows['mock_workflow']) == 1
    assert "test" in workflows["mock_workflow"]
