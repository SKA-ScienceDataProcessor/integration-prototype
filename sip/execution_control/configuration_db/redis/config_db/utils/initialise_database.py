# -*- coding: utf-8 -*-
"""Utility module to set initial data into the Configuration Database.

Run with:
    `python -m config_db.utils.initialise_database`
"""
from os.path import join, dirname
from os import listdir
import json

from config_db.config_db_redis import ConfigDb
from config_db.sdp_state import SDPState
from config_db.service_state import ServiceState
from config_db.subarray_list import SubarrayList
from config_db.workflow_definitions import add_workflow_definition


def initialise_states():
    """Initialise fields for the state of SDP."""
    print('* Initialising SDP state')
    SDPState()
    with open(join(dirname(__file__), 'data', 'services.json'), 'r') as file:
        services = json.load(file)
        for service in services['services']:
            print('* Initialising service state: {}'.format(service))
            subsystem, name, version = service.split('.')
            ServiceState(subsystem, name, version)


def initialise_subarrays():
    """Initialise subarrays."""
    print('* Initialising subarrays')
    SubarrayList()


def add_workflow_definitions():
    """Add workflow definitions."""
    path = join(dirname(__file__), 'data')
    workflow_files = [join(path, fn) for fn in listdir(path)
                      if fn.endswith('.json')
                      and not fn.startswith('test')
                      and not fn == 'services.json']
    for file_path in workflow_files:
        print('* Loading workflow template: {}'.format(file_path))
        with open(file_path, 'r') as file:
            workflow_dict = json.load(file)
            templates_dir = join(path, 'templates', workflow_dict['id'],
                                 workflow_dict['version'])
            add_workflow_definition(workflow_dict, templates_dir)


def main():
    """Initialise the database."""
    ConfigDb().flush_db()
    initialise_subarrays()
    initialise_states()
    add_workflow_definitions()


if __name__ == '__main__':
    main()
