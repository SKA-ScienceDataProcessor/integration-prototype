# coding=utf-8
"""Test of the utility functions for generating mock SBI configurations."""
import json
import os

import jsonschema
import pytest

from ..utils import generate_sbi_configuration as generate


@pytest.fixture
def sbi_schema():
    """Fixture which loads the SBI JSON schema."""
    schema_path = os.path.join(os.path.dirname(__file__), '..',
                               'schema', 'sbi_configure_schema.json')
    with open(schema_path, 'r') as file:
        schema_data = file.read()
    return json.loads(schema_data)


# pylint: disable=redefined-outer-name
def test_utils_generate_sbi_config(sbi_schema):
    """Test generating an SBI configuration dictionary."""
    generate.DB.flush_db()
    sbi_config = generate.generate_sbi_config()
    try:
        jsonschema.validate(sbi_config, sbi_schema)
    except jsonschema.ValidationError:
        pytest.fail('Generated invalid SBI configuration')


# pylint: disable=redefined-outer-name
def test_utils_generate_sbi_json(sbi_schema):
    """Test generating an SBI configuration JSON string."""
    generate.DB.flush_db()
    sbi_json = generate.generate_sbi_json(register_workflows=True)
    try:
        jsonschema.validate(json.loads(sbi_json), sbi_schema)
    except jsonschema.ValidationError:
        pytest.fail('Generated invalid SBI configuration')
