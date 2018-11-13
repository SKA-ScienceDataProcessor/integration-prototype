#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility module to add workflow definitions into the Configuration Database."""

import json
from os import listdir
from os.path import dirname, join
import os
import jinja2

from config_db.config_db_redis import ConfigDb
from config_db.workflow_definitions import add_workflow_definition


def load_workflow_definition(workflows_path: str,
                             workflow_id: str = None,
                             workflow_version: str = None,
                             test_version: int = 2,
                             parameters: dict = None) -> dict:
    """Load a mock / test workflow definition.

    Args:
        workflows_path (str): Path used to store workflow definitions
        workflow_id (str): Workflow identifier
        workflow_version (str): Workflow version
        test_version (int): Test workflow definition template file version
        parameters (dict): Additional workflow definition template parameters

    Returns:
        dict, workflow definition dictionary

    """
    workflow_path = os.path.join(workflows_path,
                                 'mock_workflow_{}.json.j2'
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


def add_workflow_definitions(workflows_path: str):
    """Add workflow definitions.

    Args:
        workflows_path (str): Path used to store workflow definitions
    """
    workflow_files = [join(workflows_path, fn)
                      for fn in listdir(workflows_path)
                      if fn.endswith('.json')
                      and not fn.startswith('test')
                      and not fn == 'services.json']
    for file_path in workflow_files:
        print('* Loading workflow template: {}'.format(file_path))
        with open(file_path, 'r') as file:
            workflow_dict = json.load(file)
            add_workflow_definition(workflow_dict, join(workflows_path,
                                                        'templates'))


def add_sbi_workflow_definitions(sbi_config: dict, workflows_path: str,
                                 test_version: int = 1):

    """Add any missing SBI workflow definitions as placeholders.

    This is a utility function used in testing and adds mock / test workflow
    definitions to the database for workflows defined in the specified
    SBI config.

    Args:
        sbi_config (dict): SBI configuration dictionary.
        workflows_path (str): Path used to store workflow definitions
        test_version(int): version to select the test workflow definition.

    """

    for i in range(len(sbi_config['processing_blocks'])):
        workflow_config = sbi_config['processing_blocks'][i]['workflow']
        workflow_name = '{}:{}'.format(workflow_config['id'],
                                       workflow_config['version'])

        workflow_definition = load_workflow_definition(workflows_path,
                                                       workflow_config['id'],
                                                       workflow_config['version'],
                                                       test_version)

        print("WORKFLOW DEFINITION {}".format(workflow_definition))
        add_workflow_definition(workflow_definition, join(workflows_path,
                                                    'templates'))
