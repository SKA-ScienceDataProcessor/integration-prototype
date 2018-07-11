# -*- coding: utf-8 -*-
"""Module of utility functions for generating Docker compose files."""
import os

import json
import jinja2


def validate_config(config, stage_type, ee_type):
    """Check that the specifed config is of the expected type and ee_type.

    Args:
        config (dict): Workflow stage configuration dictionary.
        stage_type (str): Expected workflow stage type
        ee_type (str): Expected ee type

    Raises:
        RuntimeError, if invalid configuration is detected

    """
    # Make sure the workflow type is as expected.
    if config['type'] != stage_type:
        raise RuntimeError('Unexpected workflow stage type!')

    # Make sure the Execution engine is as expected.
    if config['ee_config']['type'] != ee_type:
        raise RuntimeError('Unexpected EE type!')

    # Make sure the ee_config and app_config sections exist
    if 'ee_config' not in config or 'app_config' not in config:
        raise RuntimeError('Invalid configuration.')


def load_template(file_path, search_paths=None):
    """Load a Jinja2 template file.

    Args:
        file_path (str): Path of the template file to be loaded. This path
                         should be relative to a path specified in the
                         search_paths list.
        search_paths (list, optional): List of search paths where templates
                                       are located.

    Returns:
        (jinja2.Template) Jinja2 template object.

    """
    # Set the default search path, if not defined in the function argument.
    if not search_paths:
        cwd = os.path.abspath(os.path.dirname(__file__))
        search_paths = os.path.join(cwd, 'static')

    # Load the template
    loader = jinja2.FileSystemLoader(searchpath=search_paths)
    env = jinja2.Environment(loader=loader)
    template = env.get_template(file_path)
    return template


def load_json_file(file_path, search_paths=None):
    """Load a json file.

    Args:
        file_path (str): Path of the json file to be loaded. This path
                         should be relative to a path specified in the
                         search_paths list.
        search_paths (list, optional): List of search paths where templates
                                       are located.

    Returns:
        dict, Python dictionary representation of the JSON.

    """
    # Set the default search path, if not defined in the function argument.
    if not search_paths:
        cwd = os.path.abspath(os.path.dirname(__file__))
        search_paths = os.path.join(cwd, 'static')

    if not isinstance(search_paths, list):
        search_paths = [search_paths]

    file_ok = False
    for path in search_paths:
        full_path = os.path.join(path, file_path)
        if os.path.isfile(full_path):
            file_ok = True
            break

    if not file_ok:
        raise FileExistsError('Unable to find specified json file.')

    with open(full_path) as _file:
        data = json.load(_file)

    return data
