# coding=utf-8
"""Module for handling workflow definition objects.

Intended for registering a new workflow type with the Configuration database.
"""
import ast
import json
import os

import jsonschema

from .config_db_redis import ConfigDb

DB = ConfigDb()


def add_workflow_definition(workflow_definition: dict,
                            templates_root: str):
    """Add a workflow definition to the Configuration Database.

    Templates are expected to be found in a directory tree with the following
    structure:

        - workflow_id:
            |- workflow_version
                |- stage_id
                    |- stage_version
                        |- <templates>

    Args:
        workflow_definition (dict): Workflow definition.
        templates_root (str): Workflow templates root path

    """
    schema_path = os.path.join(
        os.path.dirname(__file__), 'schema',
        'workflow_definition_schema.json')
    with open(schema_path, 'r') as file:
        schema = json.loads(file.read())

    jsonschema.validate(workflow_definition, schema)

    _id = workflow_definition['id']
    _version = workflow_definition['version']
    _load_templates(workflow_definition, templates_root)

    workflow_id = workflow_definition['id']
    version = workflow_definition['version']
    name = "workflow_definitions:{}:{}".format(workflow_id, version)

    if DB.get_keys(name):
        raise KeyError('Workflow definition already exists: {}'.format(name))

    DB.set_hash_values(name, workflow_definition)


def register_workflow_definition(workflow_id, workflow_version):
    """Register an (empty) workflow definition in the database."""
    name = "workflow_definitions:{}:{}".format(workflow_id, workflow_version)
    DB.set_hash_values(name, dict(id=workflow_id, version=workflow_version,
                                  stages=[]))


def get_workflow_definitions() -> dict:
    """Get list of known workflow definitions.

    Returns
        list[dict]

    """
    keys = DB.get_keys("workflow_definitions:*")
    known_workflows = dict()
    for key in keys:
        values = key.split(':')
        if values[1] not in known_workflows:
            known_workflows[values[1]] = list()
        known_workflows[values[1]].append(values[2])

    return known_workflows


def delete_workflow_definitions(workflow_id: str = None,
                                workflow_version: str = None):
    """Delete workflow definitions.

    Args:
        workflow_id (str, optional): Optional workflow identifier
        workflow_version (str, optional): Optional workflow identifier version

    If workflow_id and workflow_version are None, delete all workflow
    definitions.

    """
    if workflow_id is None and workflow_version is None:
        keys = DB.get_keys("workflow_definitions:*")
        DB.delete(*keys)
    elif workflow_id is not None and workflow_version is None:
        keys = DB.get_keys("workflow_definitions:{}:*".format(workflow_id))
        DB.delete(*keys)
    elif workflow_id is None and workflow_version is not None:
        keys = DB.get_keys("workflow_definitions:*:{}"
                           .format(workflow_version))
        DB.delete(*keys)
    else:
        name = "workflow_definitions:{}:{}".format(workflow_id,
                                                   workflow_version)
        DB.delete(name)


def get_workflow_definition(workflow_id: str, workflow_version: str) -> dict:
    """Get a workflow definition from the Configuration Database.

    Args:
        workflow_id (str): Workflow identifier
        workflow_version (str): Workflow version

    Returns:
        dict, Workflow definition dictionary

    """
    name = "workflow_definitions:{}:{}".format(workflow_id, workflow_version)
    workflow = DB.get_hash_dict(name)
    workflow['stages'] = ast.literal_eval(workflow['stages'])
    return workflow


def _load_templates(workflow: dict, templates_root: str):
    """Load templates keys."""
    workflow_template_path = os.path.join(templates_root, workflow['id'],
                                          workflow['version'])
    for i, stage_config in enumerate(workflow['stages']):
        stage_template_path = os.path.join(workflow_template_path,
                                           stage_config['id'],
                                           stage_config['version'])
        for config_type in ['ee_config', 'app_config']:
            for key, value in stage_config[config_type].items():
                if 'template' in key:
                    template_file = os.path.join(stage_template_path, value)
                    with open(template_file, 'r') as file:
                        template_str = file.read()
                        workflow['stages'][i][config_type][key] = template_str
