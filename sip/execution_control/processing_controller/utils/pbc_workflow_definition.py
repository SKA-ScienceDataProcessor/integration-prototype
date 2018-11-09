#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility module to add workflow definitions into the Configuration Database."""

import json
from os import listdir
from os.path import dirname, join

from config_db.config_db_redis import ConfigDb
from config_db.workflow_definitions import add_workflow_definition


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
