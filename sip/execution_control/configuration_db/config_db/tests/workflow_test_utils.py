# coding=utf-8
"""Utility module for generating workflow definitions during testing."""
import json
import os

import jinja2

from ..workflow_definitions import add_workflow_definition


DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'workflows')


def load_workflow_definition(workflow_id: str = None,
                             workflow_version: str = None,
                             test_version: int = 2,
                             parameters: dict = None) -> dict:
    """Load a mock / test workflow definition.

    Args:
        workflow_id (str): Workflow identifier
        workflow_version (str): Workflow version
        test_version (int): Test workflow definition template file version
        parameters (dict): Additional workflow definition template parameters

    Returns:
        dict, workflow definition dictionary

    """
    workflow_path = os.path.join(DATA_PATH,
                                 'test_workflow_definition_{}.json.j2'
                                 .format(test_version))

    if workflow_id is None:
        workflow_id = 'test_workflow'

    if workflow_version is None:
        workflow_version = 'test'

    with open(workflow_path, 'r') as file:
        workflow_template = jinja2.Template(file.read())
        template_args = dict(workflow_id=workflow_id,
                             workflow_version=workflow_version)
        if parameters is not None:
            template_args = {**template_args, **parameters}
        workflow_json = workflow_template.render(**template_args)
        workflow_dict = json.loads(workflow_json)

    return workflow_dict


def add_test_sbi_workflow_definitions(sbi_config: dict,
                                      test_version: int = 2):
    """Add any missing SBI workflow definitions as placeholders.

    This is a utility function used in testing and adds mock / test workflow
    definitions to the database for workflows defined in the specified
    SBI config.

    Args:
        sbi_config (dict): SBI configuration dictionary.
        test_version(int): version to select the test workflow definition.

    """
    registered_workflows = []
    templates_root = os.path.join(DATA_PATH, 'templates')
    for i in range(len(sbi_config['processing_blocks'])):
        workflow_config = sbi_config['processing_blocks'][i]['workflow']
        workflow_name = '{}:{}'.format(workflow_config['id'],
                                       workflow_config['version'])
        if workflow_name in registered_workflows:
            continue
        workflow_definition = load_workflow_definition(
            workflow_config['id'], workflow_config['version'],
            test_version)
        add_workflow_definition(workflow_definition, templates_root)
        registered_workflows.append(workflow_name)
