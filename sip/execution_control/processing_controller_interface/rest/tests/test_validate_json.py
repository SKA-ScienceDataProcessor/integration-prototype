# -*- coding: utf-8 -*-
"""Tests to check schema input validation.

Run with:

    pytest -s tests/test_validate_json.py
"""
import os
import json
import jsonschema


def fix_file_refs(schema, path):
    """Modify schema $ref key values where the URI points to a file.

    Adds the specified path as the root path of all file $ref uri's
    This assumes that the URI to be 'fixed' originally consists of a path
    relative to the specified path argument.

    Args:
        schema (dict): JSON schema definition dictionary.
        path (str): Root path
    """
    for key in schema:
        if key == '$ref':
            if schema[key].startswith('file:///'):
                new_path = 'file://' + path + os.path.sep + schema[key][8:]
                schema[key] = new_path
        if isinstance(schema[key], dict):
            fix_file_refs(schema[key], path)


def load_schema():
    schema_root = os.path.join(os.path.dirname(__file__),
                               "..", "app", "schema", "post")
    schema_path = os.path.join(schema_root,
                               'scheduling_block_instance_request.json')
    with open(schema_path) as json_data:
        schema = json.load(json_data)

    # Fix file references. This is needed as file uri's need absolute paths.
    # https://en.wikipedia.org/wiki/File_URI_scheme
    fix_file_refs(schema, schema_root)
    # print(json.dumps(schema, indent=2))
    return schema


def test_validate_simple():
    schema = load_schema()

    test_sbi = {
        "id": "sb-01",
        "sub_array_id": "01",
        "processing_blocks": []
    }

    jsonschema.validate(test_sbi, schema)


def test_validate_workflow():
    """When a processing block is defined, the id and workflow properties are
    required"""
    schema = load_schema()

    test_sbi = {
        "id": "sb-01",
        "sub_array_id": "01",
        "processing_blocks": [
            {
                "id": "pb-01",
                "workflow": {
                    "template": "workflow_template",
                    "stages": []
                }
            }
        ]
    }
    jsonschema.validate(test_sbi, schema)

