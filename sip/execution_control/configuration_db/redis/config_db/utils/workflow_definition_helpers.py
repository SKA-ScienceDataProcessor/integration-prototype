# coding=utf-8
"""Utility module for generating workflow definitions during testing."""
import os
import json
import jinja2


def load_workflow_definition(workflow_id: str = None,
                             workflow_version: str = None,
                             template_version: int = 2) -> dict:
    """Load a workflow definition.

    Returns:
        dict, workflow definition dictionary

    """
    workflow_path = os.path.join(
        os.path.dirname(__file__),
        'data', 'test_workflow_definition_{}.json.j2'.format(template_version)
    )

    if workflow_id is None:
        workflow_id = 'test_workflow'

    if workflow_version is None:
        workflow_version = 'test'

    with open(workflow_path, 'r') as file:
        workflow_template = jinja2.Template(file.read())
        workflow_json = workflow_template.render(
            workflow_id=workflow_id, workflow_version=workflow_version)
        workflow_dict = json.loads(workflow_json)

    return workflow_dict
