# -*- coding: utf-8 -*-
"""Module to load JSON schema used by the Processing Controller."""
import os
import json


def load_scheduling_block_schema():
    """Return a Python dictionary with the scheduling block schema"""
    schema_path = os.path.join(os.path.dirname(__file__),
                               'scheduling_block_schema.json')
    with open(schema_path) as json_data:
        schema = json.load(json_data)
    return schema


SCHEDULING_BLOCK_SCHEMA = load_scheduling_block_schema()
