# coding=utf-8
"""Unit tests of the workflow definition interface."""
from os.path import dirname, join
import json

from ... import DB
from .. import workflow_definitions


def test_add_workflow_definition():
    """Test adding a workflow definition."""
    DB.flush_db()

    # Load the test workflow definition
    workflows_dir = join(dirname(__file__), 'data', 'workflows')
    workflow_path = join(workflows_dir, 'test_workflow.json')
    with open(workflow_path, 'r') as file:
        workflow_definition = json.loads(file.read())

    # Set workflow definition templates directory
    templates_root = join(workflows_dir, 'templates')
    workflow_definitions.add(workflow_definition, templates_root)

    # Load the workflow definition and test against expected result
    wfd = workflow_definitions.get_workflow(workflow_definition["id"],
                                            workflow_definition["version"])

    assert wfd == workflow_definition


def test_get_workflow_definitions():
    """Test retrieving workflow definitions."""
    DB.flush_db()

    workflows = workflow_definitions.get_workflows()
    assert not workflows

    workflow_definitions.register("workflow1", "1.0.0")
    workflow_definitions.register("workflow1", "1.0.1")
    workflow_definitions.register("workflow1", "1.0.2")

    workflows = workflow_definitions.get_workflows()
    assert 'workflow1' in workflows
    assert len(workflows['workflow1']) == 3
    assert "1.0.0" in workflows["workflow1"]
    assert "1.0.1" in workflows["workflow1"]
    assert "1.0.2" in workflows["workflow1"]

    workflow_definitions.delete()
