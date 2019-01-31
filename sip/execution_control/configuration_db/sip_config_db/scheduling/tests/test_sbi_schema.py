# coding=utf-8
"""Test of JSON schema."""

import json
from os.path import dirname, join

import jsonschema


def test_sbi_schema():
    """Test SBI configuration schema validation."""
    schema_path = join(dirname(__file__), '..', 'schema',
                       'configure_sbi_2.0.json')
    with open(schema_path, 'r') as file:
        schema_data = file.read()
    schema = json.loads(schema_data)

    config = {
        "id": "SBI-20181028-SIP-01",
        "version": "2.0",
        "scheduling_block": {
            "id": "SB-20180910-SIP-01",
            "project": "sip",
            "programme_block": "sip_demos"
        },
        "processing_blocks": [
            {
                "id": "PB-20181028-SIP-01",
                "type": "realtime",
                "workflow": {
                    "id": "mock_vis_ingest",
                    "version": "1.0.0",
                    "parameters": {}
                }
            },
            {
                "id": "PB-20181028-SIP-02",
                "type": "offline",
                "workflow": {
                    "id": "mock_ical",
                    "version": "1.0.0",
                    "parameters": {}
                }
            }
        ]
    }
    jsonschema.validate(config, schema)
