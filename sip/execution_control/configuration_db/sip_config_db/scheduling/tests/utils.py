# coding=utf-8
"""Utility module for generating workflow definitions during testing."""
from .. import workflow_definition


def add_mock_workflow_definition(workflow_id: str, workflow_version: str):
    """Add a mock workflow definition.

    Args:
        workflow_id (str): The workflow identifier
        workflow_version (str): Workflow version

    """
    stage1 = dict(id='stage1', version='1.0.0', type='setup',
                  timeout='60s',
                  resources_required=[dict(type='cpu', value=0.1)])
    workflow = dict(schema_version='2.0', stages=[stage1], id=workflow_id,
                    version=workflow_version)
    workflow_definition.add(workflow, None)


def add_mock_sbi_workflow_definitions(sbi_config: dict):
    """Add any missing SBI workflow definitions as placeholders.

    This is a utility function used in testing and adds mock / test workflow
    definitions to the database for workflows defined in the specified
    SBI config.

    Args:
        sbi_config (dict): SBI configuration dictionary.

    """
    registered_workflows = []
    stage1 = dict(id='stage1', version='1.0.0', type='setup',
                  timeout='60s',
                  resources_required=[dict(type='cpu', value=0.1)])
    workflow = dict(schema_version='2.0', stages=[stage1])
    for pb_config in sbi_config['processing_blocks']:
        workflow_config = pb_config['workflow']
        workflow_name = '{}:{}'.format(workflow_config['id'],
                                       workflow_config['version'])
        workflow['id'] = workflow_config['id']
        workflow['version'] = workflow_config['version']
        workflow_definition.add(workflow, None)
        registered_workflows.append(workflow_name)
