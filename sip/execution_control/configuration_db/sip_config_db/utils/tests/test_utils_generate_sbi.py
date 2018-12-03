# coding=utf-8
"""Test of the utility functions for generating mock SBI configurations."""
import json
import os

import jsonschema
import pytest

from ..generate_sbi_config import generate_sbi_config, generate_sbi_json
from ... import ConfigDb

DB = ConfigDb()


@pytest.fixture
def sbi_schema():
    """Fixture which loads the SBI JSON schema."""
    schema_path = os.path.join(os.path.dirname(__file__), '..', '..',
                               'scheduling', 'schema',
                               'configure_sbi.json')
    with open(schema_path, 'r') as file:
        schema_data = file.read()
    return json.loads(schema_data)


# pylint: disable=redefined-outer-name
def test_utils_generate_sbi_config(sbi_schema):
    """Test generating an SBI configuration dictionary."""
    DB.flush_db()
    sbi_config = generate_sbi_config()
    try:
        jsonschema.validate(sbi_config, sbi_schema)
    except jsonschema.ValidationError:
        pytest.fail('Generated invalid SBI configuration')


# pylint: disable=redefined-outer-name
def test_utils_generate_sbi_json(sbi_schema):
    """Test generating an SBI configuration JSON string."""
    DB.flush_db()
    sbi_json = generate_sbi_json(register_workflows=True)
    try:
        jsonschema.validate(json.loads(sbi_json), sbi_schema)
    except jsonschema.ValidationError:
        pytest.fail('Generated invalid SBI configuration')
