# coding=utf-8
"""Module for handling workflow definition objects.

Intended for registering a new workflow type with the Configuration database.
"""
import ast
import json
import os
from os.path import abspath, dirname, isdir, isfile, join

import jsonschema
import yaml

from .. import ConfigDb

DB = ConfigDb()
GROUP_KEY = 'workflow_definition'


def load(filename: str):
    """Load and register a workflow definition.

    Args:
        filename (str): Full filename path to a workflow definition file.

    Raises:
        ValueError,
        jsonschema.ValidationError,

    """
    # Check the file exists.
    if not isfile(filename):
        raise ValueError("Specified workflow path does not exist! {}"
                         .format(filename))

    # Check that the workflow stages directory exists.
    stages_dir = join(abspath(dirname(filename)), 'stages')
    if not isdir(stages_dir):
        raise ValueError("Stages directory does not exist! {}"
                         .format(stages_dir))

    # Load the workflow definition file as a Python dictionary.
    with open(filename, 'r') as file:
        if filename.lower().endswith(('.json', '.json.j2')):
            workflow_definition = json.loads(file.read())
        elif filename.lower().endswith(('.yaml', '.yml', '.yaml.j2',
                                        '.yml.j2')):
            workflow_definition = yaml.safe_load(file.read())
        else:
            raise ValueError("Unexpected file extension. Allowed values: "
                             "(.json, .yaml, .yml).")

    add(workflow_definition, stages_dir)
    return workflow_definition


def get_workflow(workflow_id: str, workflow_version: str) -> dict:
    """Get a workflow definition from the Configuration Database.

    Args:
        workflow_id (str): Workflow identifier
        workflow_version (str): Workflow version

    Returns:
        dict, Workflow definition dictionary

    Raises:
        KeyError, if the specified workflow does not exist

    """
    name = "{}:{}:{}".format(GROUP_KEY, workflow_id, workflow_version)
    if not DB.key_exists(name):
        raise KeyError('Workflow definition {}:{} not found!'
                       .format(workflow_id, workflow_version))
    workflow = DB.get_hash_dict(name)
    workflow['stages'] = ast.literal_eval(workflow['stages'])
    return workflow


def get_workflows() -> dict:
    """Get dict of ALL known workflow definitions.

    Returns
        dict,

    """
    keys = DB.get_keys("{}:*".format(GROUP_KEY))
    known_workflows = dict()
    for key in keys:
        values = key.split(':')
        if values[1] not in known_workflows:
            known_workflows[values[1]] = list()
        known_workflows[values[1]].append(values[2])
    return known_workflows


def add(workflow_definition: dict, stages_dir: str = None):
    """Add a workflow definition to the Configuration Database.

    Args:
        workflow_definition (dict): Workflow definition dictionary
        stages_dir (str): Stages directory.

    """
    _validate_schema(workflow_definition)
    key = '{}:{}:{}'.format(GROUP_KEY, workflow_definition['id'],
                            workflow_definition['version'])
    if DB.get_keys(key):
        raise KeyError('Workflow definition already exists: {}'.format(key))

    if stages_dir is not None:
        for index, stage in enumerate(workflow_definition['stages']):
            stage_dir = join(stages_dir, stage['id'], stage['version'])
            compose_str = _load_stage_compose_file(stage_dir)
            args_str = _load_stage_args(stage_dir)
            parameters = _load_stage_parameters(stage_dir)
            workflow_definition['stages'][index]['parameters'] = parameters
            workflow_definition['stages'][index]['compose_file'] = compose_str
            workflow_definition['stages'][index]['args'] = args_str

    DB.save_dict(key, workflow_definition, hierarchical=False)


def _validate_schema(workflow_definition: dict):
    """Validate the workflow definition.

    Args:
        workflow_definition (dict): workflow definition dictionary.
    """
    schema_version = workflow_definition['schema_version']
    schema_path = join(dirname(__file__), 'schema',
                       'workflow_definition_{}.json'.format(schema_version))
    with open(schema_path, 'r') as file:
        schema = json.loads(file.read())
    jsonschema.validate(workflow_definition, schema)


def _load_stage_compose_file(stage_dir: str) -> str:
    """Load Docker Compose file for workflow stage.

    Args:
        stage_dir (str):  Directory for the stage.

    Raises:
        FileNotFoundError, if no Docker compose file is found

    """
    stage_files = os.listdir(stage_dir)
    matched = [item for item in stage_files
               if item.startswith('docker_compose')]
    if not matched:
        raise FileNotFoundError('Workflow stage Docker compose file missing! '
                                'found files: {}'.format(stage_files))

    with open(join(stage_dir, matched[0]), 'r') as file:
        return file.read()


def _load_stage_args(stage_dir: str) -> str:
    """Load args file for workflow stage.

    Args:
        stage_dir (str):  Directory for the stage.

    Raises:
        FileNotFoundError,

    """
    stage_files = os.listdir(stage_dir)
    matched = [item for item in stage_files if item.startswith('args')]

    # If no argument file exists (its optional!) return an empty string.
    if not matched:
        return ""

    expected_extensions = ('.yaml', '.yml', '.json',
                           '.yaml.j2', '.yml.j2', '.json.j2')
    if not matched[0].endswith(expected_extensions):
        raise FileNotFoundError('Expecting args file to have one of the '
                                'following extensions: {}'.
                                format(expected_extensions))

    with open(join(stage_dir, matched[0]), 'r') as file:
        return file.read()


def _load_stage_parameters(stage_dir: str) -> dict:
    """Load parameters file for workflow stage.

    Args:
        stage_dir (str):  Directory for the stage.

    Returns:
        dict, workflow stage parameters dictionary

    Raises:
        FileNotFoundError,

    """
    stage_files = os.listdir(stage_dir)
    matched = [item for item in stage_files if item.startswith('parameters')]

    # If no parameters file exists (its optional!), return an empty dict
    if not matched:
        return dict()

    # Only accept yaml or json parameters files.
    expected_extensions = ('.yaml', '.yml', '.json')
    if not matched[0].endswith(expected_extensions):
        raise FileNotFoundError('Expecting parameters file to have one of the '
                                'following extensions: {}'.
                                format(expected_extensions))

    # Load the parameters file and convert to a python dict.
    with open(join(stage_dir, matched[0]), 'r') as file:
        parameters_str = file.read()
    if matched[0].endswith(('.yaml', '.yml')):
        return yaml.load(parameters_str)
    return json.loads(parameters_str)
