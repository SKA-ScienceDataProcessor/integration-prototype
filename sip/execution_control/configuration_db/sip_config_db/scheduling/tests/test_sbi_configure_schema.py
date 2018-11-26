# coding=utf-8
"""Test of JSON schema."""

import json
from os.path import dirname, join

import jsonschema


def test_sbi_schema():
    """Test SBI configuration schema validation."""
    schema_path = join(dirname(__file__), '..', 'schema', 'configure_sbi.json')
    with open(schema_path, 'r') as file:
        schema_data = file.read()
    schema = json.loads(schema_data)
    # print(json.dumps(schema, indent=2))

    config = {
        "id": "SBI-20181028-SIP-01",
        "version": "1.1.0",
        "datetime": "2018-10-28T11:32:05Z",
        "scheduling_block": {
            "id": "SB-20180910-SIP-01",
            "project": "sip",
            "programme_block": "sip_demos"
        },
        "processing_blocks": [
            {
                "id": "PB-20181028-SIP-01",
                "version": "1.0.0",
                "type": "realtime",
                "workflow": {
                    "id": "mock_vis_ingest",
                    "version": "1.0.0",
                    "parameters": {}
                }
            },
            {
                "id": "PB-20181028-SIP-02",
                "version": "1.0.0",
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
