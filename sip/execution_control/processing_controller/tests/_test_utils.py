# -*- coding: utf-8 -*-
"""Utilities used by PBC unit tests."""
import json
from os import listdir
from os.path import join

from sip_config_db.scheduling import workflow_definitions


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
        with open(file_path, 'r') as file:
            workflow_dict = json.load(file)
            workflow_definitions.add(workflow_dict, join(workflows_path,
                                                         'templates'))
